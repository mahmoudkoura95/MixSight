"""Clerk session JWT verification.

Per §7.19: Clerk is the authentication source of truth; our DB is the
authorization source of truth. The session JWT carries the role as a custom
claim for fast checks; mutations and sensitive operations re-check the DB.

Frontend API URL is derived from the publishable key (base64 of
`<domain>$`). JWKS is fetched + cached by `PyJWKClient` (default 5-min TTL,
sufficient for Phase 1a — Anthropic-style key rotation discipline tightens
in Phase 1c).
"""

from __future__ import annotations

import asyncio
import base64
import functools
from typing import Any

import jwt
from jwt import PyJWKClient
from pydantic import BaseModel, ConfigDict, model_validator

from mixsight.config import get_settings


class ClerkTokenPayload(BaseModel):
    """Subset of Clerk session JWT claims used by the API."""

    model_config = ConfigDict(extra="allow")

    sub: str  # clerk_user_id
    iss: str
    exp: int
    iat: int
    org_id: str | None = None
    org_role: str | None = None  # "admin" / "account_manager" (or "org:"-prefixed)
    org_permissions: list[str] | None = None

    @model_validator(mode="before")
    @classmethod
    def _hoist_compact_org_claim(cls, data: object) -> object:
        """Clerk's modern session token packs the active org into a compact
        `o` claim (`{id, rol, slg}`) rather than the legacy flat
        `org_id` / `org_role`. Lift it so downstream tenancy code keeps
        reading `org_id` / `org_role`. Legacy flat claims still win if present.
        """
        if isinstance(data, dict) and not data.get("org_id"):
            org = data.get("o")
            if isinstance(org, dict):
                return {**data, "org_id": org.get("id"), "org_role": org.get("rol")}
        return data


class InvalidClerkTokenError(Exception):
    """Raised when a Clerk session token fails verification."""


@functools.lru_cache(maxsize=1)
def _frontend_api_url() -> str:
    """Derive Clerk frontend API URL from the publishable key."""
    settings = get_settings()
    pk = settings.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
    if pk is None:
        raise RuntimeError(
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY not configured; cannot derive Clerk frontend API URL"
        )
    encoded = pk.split("_", 2)[-1]
    padded = encoded + "=" * ((4 - len(encoded) % 4) % 4)
    decoded = base64.b64decode(padded).decode()
    return f"https://{decoded.rstrip('$')}"


@functools.lru_cache(maxsize=1)
def _jwk_client() -> PyJWKClient:
    return PyJWKClient(f"{_frontend_api_url()}/.well-known/jwks.json")


async def verify_clerk_jwt(token: str) -> ClerkTokenPayload:
    """Verify a Clerk session JWT. Raises `InvalidClerkTokenError` on failure.

    `PyJWKClient.get_signing_key_from_jwt` is synchronous and does an HTTP
    fetch on cold cache; running it inline would block the event loop on the
    first sign-in after server boot (and after every JWKS rotation). Wrapping
    it in `asyncio.to_thread` keeps the loop responsive without bringing in
    a second async-aware JWKS implementation.
    """
    try:
        signing_key = await asyncio.to_thread(_jwk_client().get_signing_key_from_jwt, token)
        claims: dict[str, Any] = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=_frontend_api_url(),
            options={"verify_aud": False},  # Clerk session tokens don't set aud
        )
    except jwt.InvalidTokenError as e:
        raise InvalidClerkTokenError(str(e)) from e
    except Exception as e:
        raise InvalidClerkTokenError(f"JWKS verification failed: {e}") from e
    return ClerkTokenPayload.model_validate(claims)
