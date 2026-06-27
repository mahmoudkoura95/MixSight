"""Handlers for Clerk `organization.*` events.

`organization.created` → upsert by `clerk_organization_id`.
`organization.updated` → update name + branding.
`organization.deleted` → soft-delete (set `deleted_at`).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.logging import get_logger
from mixsight.models import Organization
from mixsight.webhooks.handlers.common import clerk_ts_to_dt, is_stale_event

log = get_logger("mixsight.webhooks.clerk.organization")


async def _find_by_clerk_id(
    session: AsyncSession, clerk_organization_id: str
) -> Organization | None:
    stmt = select(Organization).where(
        col(Organization.clerk_organization_id) == clerk_organization_id
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def handle_created(data: dict[str, Any], session: AsyncSession) -> None:
    clerk_org_id = data.get("id")
    if not clerk_org_id:
        log.warning("clerk_webhook.organization.created.missing_id")
        return

    existing = await _find_by_clerk_id(session, clerk_org_id)
    if existing is not None:
        log.info(
            "clerk_webhook.organization.created.duplicate",
            clerk_organization_id=clerk_org_id,
        )
        return

    org = Organization(
        clerk_organization_id=clerk_org_id,
        name=str(data.get("name") or "Unnamed"),
        clerk_last_event_at=clerk_ts_to_dt(data.get("updated_at")),
    )
    session.add(org)
    log.info("clerk_webhook.organization.created", clerk_organization_id=clerk_org_id)


async def handle_updated(data: dict[str, Any], session: AsyncSession) -> None:
    clerk_org_id = data.get("id")
    if not clerk_org_id:
        return

    org = await _find_by_clerk_id(session, clerk_org_id)
    if org is None:
        # Out-of-order delivery: created hasn't arrived yet. JIT-create.
        log.info(
            "clerk_webhook.organization.updated.jit_create",
            clerk_organization_id=clerk_org_id,
        )
        await handle_created(data, session)
        return

    event_updated_at = clerk_ts_to_dt(data.get("updated_at"))
    if is_stale_event(org.clerk_last_event_at, event_updated_at):
        log.info(
            "clerk_webhook.organization.updated.stale",
            clerk_organization_id=clerk_org_id,
        )
        return

    if data.get("name"):
        org.name = str(data["name"])
    if event_updated_at is not None:
        org.clerk_last_event_at = event_updated_at
    session.add(org)


async def handle_deleted(data: dict[str, Any], session: AsyncSession) -> None:
    clerk_org_id = data.get("id")
    if not clerk_org_id:
        return

    org = await _find_by_clerk_id(session, clerk_org_id)
    if org is None:
        return  # already gone

    if org.deleted_at is None:
        org.deleted_at = datetime.now(UTC)
        org.deletion_status = "deleted"
        session.add(org)
