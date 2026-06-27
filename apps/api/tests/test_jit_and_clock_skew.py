"""Coverage for Week 3 / Day 2 HIGH carry-overs from Week 2 /code-review.

Two distinct contracts:

1. **JIT user provisioning** (per §7.19 eventual-consistency window). When a
   valid Clerk JWT arrives before the matching webhook has synced the User
   row, `_jit_provision_user` upserts both Organization and User inline
   using JWT claims. The webhook later updates the placeholder name + email
   with real values.

2. **Stale-event clock-skew fix.** `is_stale_event` now compares Clerk-
   clock to Clerk-clock (via the new `clerk_last_event_at` column) instead
   of server-clock to Clerk-clock. Regression test below would FAIL under
   the Week 2 implementation — two close-together Clerk events with
   timestamps slightly in the past (relative to the server clock) used to
   be silently dropped as "stale."
"""

from __future__ import annotations

import time

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.auth.clerk import ClerkTokenPayload
from mixsight.auth.dependencies import _find_or_create_organization, _jit_provision_user
from mixsight.models import Organization
from mixsight.webhooks.handlers.dispatch import dispatch


def _payload(clerk_user_id: str, clerk_org_id: str, role: str = "org:admin") -> ClerkTokenPayload:
    """Synthetic JWT payload — matches the subset `current_user` reads."""
    return ClerkTokenPayload(
        sub=clerk_user_id,
        iss="https://test.clerk",
        exp=2_000_000_000,
        iat=1_700_000_000,
        org_id=clerk_org_id,
        org_role=role,
    )


@pytest.mark.asyncio
async def test_jit_provisions_organization_and_user(db_session: AsyncSession) -> None:
    user = await _jit_provision_user(db_session, _payload("user_jit_a", "org_jit_a"))
    await db_session.commit()

    assert user.clerk_user_id == "user_jit_a"
    assert user.role == "admin"
    assert user.email == "user_jit_a@unknown.local"

    org = (
        await db_session.execute(
            select(Organization).where(col(Organization.clerk_organization_id) == "org_jit_a")
        )
    ).scalar_one()
    assert org.name == "Unnamed"  # webhook fills the real name later
    assert user.organization_id == org.id


@pytest.mark.asyncio
async def test_jit_reuses_existing_organization(db_session: AsyncSession) -> None:
    """Two users in the same Clerk org → one Organization row, both Users linked."""
    user_a = await _jit_provision_user(db_session, _payload("user_jit_b1", "org_jit_b"))
    user_b = await _jit_provision_user(db_session, _payload("user_jit_b2", "org_jit_b"))
    await db_session.commit()

    orgs = list(
        (
            await db_session.execute(
                select(Organization).where(col(Organization.clerk_organization_id) == "org_jit_b")
            )
        )
        .scalars()
        .all()
    )
    assert len(orgs) == 1
    assert user_a.organization_id == orgs[0].id
    assert user_b.organization_id == orgs[0].id


@pytest.mark.asyncio
async def test_find_or_create_organization_is_idempotent(
    db_session: AsyncSession,
) -> None:
    org_first = await _find_or_create_organization(db_session, "org_idem")
    org_second = await _find_or_create_organization(db_session, "org_idem")
    await db_session.commit()
    assert org_first.id == org_second.id


@pytest.mark.asyncio
async def test_close_together_clerk_events_both_apply_despite_server_clock_drift(
    db_session: AsyncSession,
) -> None:
    """Regression for the Week 2 clock-skew bug.

    Both events have Clerk timestamps in the past (relative to server now()),
    arriving in correct order. Under the old `is_stale_event(entity.updated_at,
    event_ts)` impl, the second event was marked stale because its
    Clerk-clock timestamp predated the server-clock `updated_at` set when
    the first event was applied. The fix compares stored Clerk-clock to
    incoming Clerk-clock, so close-together events apply correctly.
    """
    now_ms = int(time.time() * 1000)
    old_clerk_ts = now_ms - 5_000  # 5 seconds ago in Clerk's clock
    newer_clerk_ts = now_ms - 4_000  # 4 seconds ago, still past server now()

    await dispatch(
        {
            "type": "organization.updated",
            "data": {"id": "org_clkskew", "name": "First", "updated_at": old_clerk_ts},
        },
        db_session,
    )
    await db_session.commit()

    await dispatch(
        {
            "type": "organization.updated",
            "data": {"id": "org_clkskew", "name": "Second", "updated_at": newer_clerk_ts},
        },
        db_session,
    )
    await db_session.commit()

    org = (
        await db_session.execute(
            select(Organization).where(col(Organization.clerk_organization_id) == "org_clkskew")
        )
    ).scalar_one()
    # Under the old comparison this asserted "First" (second event dropped).
    assert org.name == "Second"
    assert org.clerk_last_event_at is not None


@pytest.mark.asyncio
async def test_genuinely_stale_event_still_skipped(db_session: AsyncSession) -> None:
    """Sanity check the fix didn't accidentally disable the stale guard:
    an event whose Clerk timestamp predates the stored one is still
    dropped."""
    now_ms = int(time.time() * 1000)
    await dispatch(
        {
            "type": "organization.updated",
            "data": {"id": "org_stale_v2", "name": "Newer", "updated_at": now_ms + 5_000},
        },
        db_session,
    )
    await db_session.commit()
    await dispatch(
        {
            "type": "organization.updated",
            "data": {"id": "org_stale_v2", "name": "Older", "updated_at": now_ms - 5_000},
        },
        db_session,
    )
    await db_session.commit()

    org = (
        await db_session.execute(
            select(Organization).where(col(Organization.clerk_organization_id) == "org_stale_v2")
        )
    ).scalar_one()
    assert org.name == "Newer"
