"""FastAPI dependencies for Clerk-authenticated routes.

Per §7.19: middleware extracts `clerk_user_id`, looks up `User`, attaches
`current_user` to request scope. Every endpoint with `client_id` then layers
`enforce_client_access` (see `mixsight.tenancy`).

JIT user provisioning: when a valid JWT arrives but no `User` row exists
(the eventual-consistency window before Clerk's webhook lands), the
dependency upserts both Organization (via `clerk_organization_id` from the
JWT `org_id` claim) and User (via `clerk_user_id` from `sub`) inline. Email
and org name use placeholders that the subsequent webhook updates with real
values. Without a JWT `org_id` (rare — user belongs to no Clerk org) we
fall back to the prior 401 since `User.organization_id` is NOT NULL.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.audit.context import set_actor_user_id
from mixsight.auth.clerk import ClerkTokenPayload, InvalidClerkTokenError, verify_clerk_jwt
from mixsight.db import get_db
from mixsight.logging import get_logger
from mixsight.models.organization import Organization
from mixsight.models.user import User
from mixsight.webhooks.handlers.common import map_clerk_role

_bearer = HTTPBearer(auto_error=False)
log = get_logger("mixsight.auth")


async def _find_or_create_organization(
    db: AsyncSession, clerk_organization_id: str
) -> Organization:
    """JIT lookup: find Organization by clerk_organization_id or create a
    placeholder. Name is filled by the `organization.created` webhook when
    it lands."""
    stmt = select(Organization).where(
        col(Organization.clerk_organization_id) == clerk_organization_id
    )
    org = (await db.execute(stmt)).scalar_one_or_none()
    if org is not None:
        return org
    org = Organization(clerk_organization_id=clerk_organization_id, name="Unnamed")
    db.add(org)
    await db.flush()  # populate org.id for the User FK
    log.info("auth.jit_organization_created", clerk_organization_id=clerk_organization_id)
    return org


async def _jit_provision_user(db: AsyncSession, payload: ClerkTokenPayload) -> User:
    """Create the User row from JWT claims. Pre-condition: caller has
    already confirmed no row exists. Email + org name are placeholders the
    webhook will replace. Race with a concurrent webhook write surfaces as
    an `IntegrityError` on commit; per the Week 2 MEDIUM carry-over this
    will get ON CONFLICT DO NOTHING handling later — for now the retry on
    the next request resolves it cleanly because the row will exist."""
    if not payload.org_id:
        # Single-org tenancy model: no org_id in JWT means we can't link
        # the User to anything. Treat as the prior 401 case.
        log.info("auth.jit_skipped_no_org", clerk_user_id=payload.sub)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has no organization. Sign in again after joining one.",
        )
    org = await _find_or_create_organization(db, payload.org_id)
    user = User(
        organization_id=org.id,
        clerk_user_id=payload.sub,
        email=f"{payload.sub}@unknown.local",
        role=map_clerk_role(payload.org_role),
    )
    db.add(user)
    await db.flush()
    log.info(
        "auth.jit_user_provisioned",
        clerk_user_id=payload.sub,
        clerk_organization_id=payload.org_id,
    )
    return user


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = await verify_clerk_jwt(credentials.credentials)
    except InvalidClerkTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    stmt = select(User).where(
        col(User.clerk_user_id) == payload.sub,
        col(User.deleted_at).is_(None),
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    if user is None:
        user = await _jit_provision_user(db, payload)

    set_actor_user_id(user.id)
    return user
