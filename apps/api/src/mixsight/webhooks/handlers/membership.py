"""Handlers for Clerk `organizationMembership.*` events.

Membership is the moment a User joins an Organization — and in our model,
the moment we can create the User row (since `User.organization_id` is
NOT NULL).

`organizationMembership.created` → ensure Organization exists (JIT if not)
+ upsert User linked to it.
`organizationMembership.updated` → update User.role.
`organizationMembership.deleted` → soft-delete User (single-org model
implies losing org membership is losing access).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.logging import get_logger
from mixsight.models import Organization, User
from mixsight.webhooks.handlers.common import (
    clerk_ts_to_dt,
    is_stale_event,
    map_clerk_role,
)
from mixsight.webhooks.handlers.organization import handle_created as org_handle_created

log = get_logger("mixsight.webhooks.clerk.membership")


def _extract_clerk_ids(data: dict[str, Any]) -> tuple[str | None, str | None]:
    """Pull `(clerk_org_id, clerk_user_id)` from a membership payload."""
    org = data.get("organization") or {}
    clerk_org_id = org.get("id") if isinstance(org, dict) else None
    public_user = data.get("public_user_data") or {}
    clerk_user_id = public_user.get("user_id") if isinstance(public_user, dict) else None
    return clerk_org_id, clerk_user_id


async def _ensure_organization(data: dict[str, Any], session: AsyncSession) -> Organization | None:
    clerk_org_id, _ = _extract_clerk_ids(data)
    if not clerk_org_id:
        return None

    stmt = select(Organization).where(col(Organization.clerk_organization_id) == clerk_org_id)
    org = (await session.execute(stmt)).scalar_one_or_none()
    if org is not None:
        return org

    # JIT-create the org from the embedded `organization` payload.
    org_data = data.get("organization") or {}
    await org_handle_created(org_data, session)
    await session.flush()  # populate org.id for the User FK below
    return (await session.execute(stmt)).scalar_one_or_none()


async def handle_created(data: dict[str, Any], session: AsyncSession) -> None:
    clerk_org_id, clerk_user_id = _extract_clerk_ids(data)
    if not clerk_org_id or not clerk_user_id:
        log.warning("clerk_webhook.membership.created.missing_ids")
        return

    org = await _ensure_organization(data, session)
    if org is None:
        log.warning(
            "clerk_webhook.membership.created.no_org",
            clerk_organization_id=clerk_org_id,
        )
        return

    stmt = select(User).where(col(User.clerk_user_id) == clerk_user_id)
    user = (await session.execute(stmt)).scalar_one_or_none()

    role = map_clerk_role(data.get("role"))
    public_user = data.get("public_user_data") or {}
    email = public_user.get("identifier") or f"{clerk_user_id}@unknown.local"
    event_updated_at = clerk_ts_to_dt(data.get("updated_at"))

    if user is None:
        user = User(
            organization_id=org.id,
            clerk_user_id=clerk_user_id,
            email=str(email),
            role=role,
            clerk_last_event_at=event_updated_at,
        )
        session.add(user)
        log.info(
            "clerk_webhook.membership.created.user_provisioned",
            clerk_user_id=clerk_user_id,
            clerk_organization_id=clerk_org_id,
        )
    else:
        # User already exists (possibly from JIT). Update role + org link.
        user.role = role
        user.organization_id = org.id
        if user.deleted_at is not None:
            user.deleted_at = None  # restore
        if event_updated_at is not None:
            user.clerk_last_event_at = event_updated_at
        session.add(user)


async def handle_updated(data: dict[str, Any], session: AsyncSession) -> None:
    _, clerk_user_id = _extract_clerk_ids(data)
    if not clerk_user_id:
        return

    stmt = select(User).where(col(User.clerk_user_id) == clerk_user_id)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        # Treat as create.
        await handle_created(data, session)
        return

    event_updated_at = clerk_ts_to_dt(data.get("updated_at"))
    if is_stale_event(user.clerk_last_event_at, event_updated_at):
        log.info("clerk_webhook.membership.updated.stale", clerk_user_id=clerk_user_id)
        return

    user.role = map_clerk_role(data.get("role"))
    if event_updated_at is not None:
        user.clerk_last_event_at = event_updated_at
    session.add(user)


async def handle_deleted(data: dict[str, Any], session: AsyncSession) -> None:
    _, clerk_user_id = _extract_clerk_ids(data)
    if not clerk_user_id:
        return

    stmt = select(User).where(col(User.clerk_user_id) == clerk_user_id)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        return

    if user.deleted_at is None:
        user.deleted_at = datetime.now(UTC)
        session.add(user)
