"""Coverage for the Clerk webhook dispatcher.

Tests bypass svix signature verification (already exercised by the svix
library) and call `dispatch` directly with realistic Clerk event payloads.
The `db_session` fixture wraps each test in a SAVEPOINT.

Per §7.19 contract:
- Organization upsert by `clerk_organization_id`.
- User created when the membership event lands (User requires org_id).
- Out-of-order events are skipped via `updated_at` comparison.
- Repeated events are idempotent.
"""

from __future__ import annotations

import time
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.models import Organization, User
from mixsight.webhooks.handlers.dispatch import dispatch


def _now_ms() -> int:
    """Realistic Clerk-style millisecond timestamp anchored at test-run time."""
    return int(time.time() * 1000)


def _organization_created(clerk_org_id: str, name: str) -> dict[str, Any]:
    now = _now_ms()
    return {
        "type": "organization.created",
        "data": {
            "id": clerk_org_id,
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "created_at": now,
            "updated_at": now,
        },
    }


def _organization_updated(clerk_org_id: str, name: str, ts_ms: int | None = None) -> dict[str, Any]:
    return {
        "type": "organization.updated",
        "data": {
            "id": clerk_org_id,
            "name": name,
            "updated_at": ts_ms if ts_ms is not None else _now_ms() + 1000,
        },
    }


def _membership_created(
    clerk_org_id: str,
    org_name: str,
    clerk_user_id: str,
    email: str,
    role: str = "org:admin",
) -> dict[str, Any]:
    now = _now_ms()
    return {
        "type": "organizationMembership.created",
        "data": {
            "id": f"orgmem_{clerk_user_id}_{clerk_org_id}",
            "organization": {
                "id": clerk_org_id,
                "name": org_name,
                "created_at": now,
                "updated_at": now,
            },
            "public_user_data": {
                "user_id": clerk_user_id,
                "identifier": email,
                "first_name": "Test",
            },
            "role": role,
            "created_at": now,
            "updated_at": now,
        },
    }


def _user_updated(clerk_user_id: str, email: str, ts_ms: int | None = None) -> dict[str, Any]:
    primary_id = "idn_primary"
    return {
        "type": "user.updated",
        "data": {
            "id": clerk_user_id,
            "primary_email_address_id": primary_id,
            "email_addresses": [{"id": primary_id, "email_address": email}],
            "updated_at": ts_ms if ts_ms is not None else _now_ms() + 1000,
        },
    }


def _user_deleted(clerk_user_id: str) -> dict[str, Any]:
    return {"type": "user.deleted", "data": {"id": clerk_user_id, "deleted": True}}


@pytest.mark.asyncio
async def test_dispatch_organization_created(db_session: AsyncSession) -> None:
    await dispatch(_organization_created("org_abc", "Brave Bison"), db_session)
    await db_session.commit()

    org = (
        await db_session.execute(
            select(Organization).where(col(Organization.clerk_organization_id) == "org_abc")
        )
    ).scalar_one()
    assert org.name == "Brave Bison"
    assert org.deleted_at is None
    assert org.deletion_status == "active"


@pytest.mark.asyncio
async def test_dispatch_organization_created_idempotent(
    db_session: AsyncSession,
) -> None:
    await dispatch(_organization_created("org_dup", "First"), db_session)
    await db_session.commit()
    await dispatch(_organization_created("org_dup", "Second"), db_session)
    await db_session.commit()

    rows = (
        (
            await db_session.execute(
                select(Organization).where(col(Organization.clerk_organization_id) == "org_dup")
            )
        )
        .scalars()
        .all()
    )
    assert len(list(rows)) == 1


@pytest.mark.asyncio
async def test_dispatch_organization_updated_creates_if_missing(
    db_session: AsyncSession,
) -> None:
    """Out-of-order delivery: `updated` arrives before `created` → JIT-create."""
    await dispatch(_organization_updated("org_late", "Late Name"), db_session)
    await db_session.commit()

    org = (
        await db_session.execute(
            select(Organization).where(col(Organization.clerk_organization_id) == "org_late")
        )
    ).scalar_one()
    assert org.name == "Late Name"


@pytest.mark.asyncio
async def test_dispatch_membership_created_provisions_user(
    db_session: AsyncSession,
) -> None:
    await dispatch(
        _membership_created(
            "org_xyz", "New Balance EMEA", "user_123", "am@example.com", "org:admin"
        ),
        db_session,
    )
    await db_session.commit()

    org = (
        await db_session.execute(
            select(Organization).where(col(Organization.clerk_organization_id) == "org_xyz")
        )
    ).scalar_one()
    user = (
        await db_session.execute(select(User).where(col(User.clerk_user_id) == "user_123"))
    ).scalar_one()
    assert user.organization_id == org.id
    assert user.email == "am@example.com"
    assert user.role == "admin"


@pytest.mark.asyncio
async def test_dispatch_membership_account_manager_role(
    db_session: AsyncSession,
) -> None:
    await dispatch(
        _membership_created(
            "org_am",
            "Agency",
            "user_am",
            "am@example.com",
            "org:account_manager",
        ),
        db_session,
    )
    await db_session.commit()

    user = (
        await db_session.execute(select(User).where(col(User.clerk_user_id) == "user_am"))
    ).scalar_one()
    assert user.role == "account_manager"


@pytest.mark.asyncio
async def test_dispatch_user_updated_changes_email(db_session: AsyncSession) -> None:
    await dispatch(
        _membership_created("org_u", "Org", "user_u", "old@example.com"),
        db_session,
    )
    await db_session.commit()

    await dispatch(_user_updated("user_u", "new@example.com"), db_session)
    await db_session.commit()

    user = (
        await db_session.execute(select(User).where(col(User.clerk_user_id) == "user_u"))
    ).scalar_one()
    assert user.email == "new@example.com"


@pytest.mark.asyncio
async def test_dispatch_user_deleted_soft_deletes(db_session: AsyncSession) -> None:
    await dispatch(
        _membership_created("org_d", "Org", "user_d", "d@example.com"),
        db_session,
    )
    await db_session.commit()

    await dispatch(_user_deleted("user_d"), db_session)
    await db_session.commit()

    user = (
        await db_session.execute(select(User).where(col(User.clerk_user_id) == "user_d"))
    ).scalar_one()
    assert user.deleted_at is not None


@pytest.mark.asyncio
async def test_dispatch_unknown_event_type_is_noop(db_session: AsyncSession) -> None:
    event_type = await dispatch({"type": "session.created", "data": {"id": "sess_x"}}, db_session)
    assert event_type == "session.created"  # logged + ignored, no DB writes


@pytest.mark.asyncio
async def test_dispatch_stale_organization_update_skipped(
    db_session: AsyncSession,
) -> None:
    """An `updated` event whose timestamp predates the current row is skipped."""
    now = _now_ms()
    await dispatch(
        _organization_updated("org_stale", "Newer Name", ts_ms=now + 10_000),
        db_session,
    )
    await db_session.commit()
    # Stale event arrives after but with an earlier timestamp.
    await dispatch(
        _organization_updated("org_stale", "Older Name", ts_ms=now - 10_000),
        db_session,
    )
    await db_session.commit()

    org = (
        await db_session.execute(
            select(Organization).where(col(Organization.clerk_organization_id) == "org_stale")
        )
    ).scalar_one()
    assert org.name == "Newer Name"
