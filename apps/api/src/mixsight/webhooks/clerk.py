"""Clerk webhook handler.

Verifies `svix-*` signature headers per Clerk's webhook contract, parses
the event, and dispatches to the right handler in
`mixsight.webhooks.handlers`. Handlers mutate via the FastAPI-injected
`AsyncSession`; the session commits at the end of a successful dispatch.

Per §7.19: Clerk is the auth source of truth; this handler keeps the
authorization tables (Organization, User, UserClientAccess) in sync.

Out-of-order delivery: each handler compares the event's `updated_at`
timestamp against the existing entity's and skips stale events.
Idempotency: handlers use upsert semantics keyed by `clerk_*_id`.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from svix.webhooks import Webhook, WebhookVerificationError

from mixsight.config import get_settings
from mixsight.db import get_db
from mixsight.logging import get_logger
from mixsight.webhooks.handlers.dispatch import dispatch

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
log = get_logger("mixsight.webhooks.clerk")


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    svix_id: str = Header(alias="svix-id"),
    svix_timestamp: str = Header(alias="svix-timestamp"),
    svix_signature: str = Header(alias="svix-signature"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    settings = get_settings()
    if settings.CLERK_WEBHOOK_SECRET is None:
        log.error("clerk_webhook.secret_not_configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk webhook secret not configured",
        )

    body = await request.body()
    headers = {
        "svix-id": svix_id,
        "svix-timestamp": svix_timestamp,
        "svix-signature": svix_signature,
    }
    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        wh.verify(body, headers)
    except WebhookVerificationError as e:
        log.warning("clerk_webhook.invalid_signature", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid svix signature",
        ) from e

    try:
        event = json.loads(body)
    except json.JSONDecodeError as e:
        log.warning("clerk_webhook.malformed_json", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON payload",
        ) from e

    event_type = await dispatch(event, db)
    await db.commit()
    log.info("clerk_webhook.processed", event_type=event_type, svix_id=svix_id)
    return {"status": "ok", "event_type": event_type}
