"""Shared helpers for Clerk webhook handlers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from mixsight.logging import get_logger

log = get_logger("mixsight.webhooks.clerk.handlers")

# Per §7.19 + §6.3: Clerk's custom organization roles map to our two-role model.
_CLERK_ROLE_MAP = {
    "org:admin": "admin",
    "org:account_manager": "account_manager",
}


def map_clerk_role(clerk_role: str | None) -> str:
    """Map a Clerk org-membership role to our `User.role` enum.

    Unknown roles default to `account_manager` (least-privileged) + log a
    warning so role-mapping drift is observable.
    """
    if clerk_role is None:
        log.warning("clerk_webhook.role_missing", default="account_manager")
        return "account_manager"
    mapped = _CLERK_ROLE_MAP.get(clerk_role)
    if mapped is None:
        log.warning(
            "clerk_webhook.role_unknown",
            clerk_role=clerk_role,
            default="account_manager",
        )
        return "account_manager"
    return mapped


def clerk_ts_to_dt(ms_since_epoch: int | None) -> datetime | None:
    """Clerk timestamps are integer milliseconds since epoch. Returns UTC datetime."""
    if ms_since_epoch is None:
        return None
    return datetime.fromtimestamp(ms_since_epoch / 1000, tz=UTC)


def is_stale_event(
    stored_clerk_event_at: datetime | None,
    incoming_clerk_event_at: datetime | None,
) -> bool:
    """Out-of-order guard per §7.19: skip if the incoming event predates the
    last Clerk-clock event we've already applied to this entity. Returns
    False if either timestamp is unknown — first event for an entity (no
    prior Clerk timestamp stored) always applies.

    Both args must be Clerk-clock timestamps. Comparing Clerk-clock to
    server-clock `updated_at` is the bug this signature change closes —
    NTP / timezone drift between Clerk and our server would mark legitimate
    close-together events as stale and silently drop them.
    """
    if stored_clerk_event_at is None or incoming_clerk_event_at is None:
        return False
    return incoming_clerk_event_at < stored_clerk_event_at


def primary_email(data: dict[str, Any]) -> str | None:
    """Pull primary email address from a Clerk `user.*` payload."""
    addresses = data.get("email_addresses") or []
    primary_id = data.get("primary_email_address_id")
    for addr in addresses:
        if addr.get("id") == primary_id:
            email = addr.get("email_address")
            return str(email) if email else None
    if addresses:
        first = addresses[0].get("email_address")
        return str(first) if first else None
    return None
