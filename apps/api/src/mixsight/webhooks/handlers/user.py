"""Handlers for Clerk `user.*` events.

`user.created` → **no-op** in our model: User requires `organization_id`
(NOT NULL), which we only know once `organizationMembership.created`
fires. The membership handler creates the User row.

`user.updated` → update email if User row exists.
`user.deleted` → soft-delete if User row exists.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.logging import get_logger
from mixsight.models import User
from mixsight.webhooks.handlers.common import (
    clerk_ts_to_dt,
    is_stale_event,
    primary_email,
)

log = get_logger("mixsight.webhooks.clerk.user")


async def _find_by_clerk_id(session: AsyncSession, clerk_user_id: str) -> User | None:
    stmt = select(User).where(col(User.clerk_user_id) == clerk_user_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def handle_created(data: dict[str, Any], _session: AsyncSession) -> None:
    # User in our model requires org context (NOT NULL FK). Wait for
    # organizationMembership.created to land the row.
    log.info(
        "clerk_webhook.user.created.deferred",
        clerk_user_id=data.get("id"),
        reason="awaiting_organization_membership",
    )


async def handle_updated(data: dict[str, Any], session: AsyncSession) -> None:
    clerk_user_id = data.get("id")
    if not clerk_user_id:
        return

    user = await _find_by_clerk_id(session, clerk_user_id)
    if user is None:
        # No org yet → no User row to update. Will reconcile on first sign-in JIT.
        return

    event_updated_at = clerk_ts_to_dt(data.get("updated_at"))
    if is_stale_event(user.clerk_last_event_at, event_updated_at):
        log.info("clerk_webhook.user.updated.stale", clerk_user_id=clerk_user_id)
        return

    email = primary_email(data)
    if email:
        user.email = email
    if event_updated_at is not None:
        user.clerk_last_event_at = event_updated_at
    session.add(user)


async def handle_deleted(data: dict[str, Any], session: AsyncSession) -> None:
    clerk_user_id = data.get("id")
    if not clerk_user_id:
        return

    user = await _find_by_clerk_id(session, clerk_user_id)
    if user is None:
        return

    if user.deleted_at is None:
        user.deleted_at = datetime.now(UTC)
        session.add(user)
