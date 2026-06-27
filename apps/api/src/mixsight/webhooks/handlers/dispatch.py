"""Dispatch a verified Clerk webhook event to the right handler."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from mixsight.logging import get_logger
from mixsight.webhooks.handlers import membership, organization, user

log = get_logger("mixsight.webhooks.clerk.dispatch")

Handler = Callable[[dict[str, Any], AsyncSession], Awaitable[None]]

HANDLERS: dict[str, Handler] = {
    "organization.created": organization.handle_created,
    "organization.updated": organization.handle_updated,
    "organization.deleted": organization.handle_deleted,
    "user.created": user.handle_created,
    "user.updated": user.handle_updated,
    "user.deleted": user.handle_deleted,
    "organizationMembership.created": membership.handle_created,
    "organizationMembership.updated": membership.handle_updated,
    "organizationMembership.deleted": membership.handle_deleted,
}


async def dispatch(event: dict[str, Any], session: AsyncSession) -> str:
    """Route a verified Clerk event payload to its handler.

    Returns the event type for logging. Unhandled types are logged + ignored
    (Clerk fires a lot of event types; we only care about a subset).
    """
    event_type = event.get("type")
    if not isinstance(event_type, str):
        log.warning("clerk_webhook.malformed_event", payload=event)
        return "unknown"

    handler = HANDLERS.get(event_type)
    if handler is None:
        log.info("clerk_webhook.unhandled_event_type", event_type=event_type)
        return event_type

    data = event.get("data") or {}
    if not isinstance(data, dict):
        log.warning("clerk_webhook.malformed_data", event_type=event_type)
        return event_type

    await handler(data, session)
    return event_type
