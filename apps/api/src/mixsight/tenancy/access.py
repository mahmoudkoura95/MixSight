"""Tenancy enforcement dependencies per §7.19.

`enforce_client_access` — required on every route with a `client_id`. Validates
that the authenticated user's `Organization` owns the `Client`, and (for
account_manager role) that an explicit `UserClientAccess` grant exists.

`enforce_organization_access` — required on every route with an `organization_id`.
Validates that the user belongs to that org.

`require_role(role)` — gate sensitive operations (e.g., connector reauth is
admin-only per §7.19).

Cross-org access returns 404 rather than 403 to avoid leaking existence.
Missing UserClientAccess (within-org) returns 403 — existence is already known.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.auth.dependencies import current_user
from mixsight.db import get_db
from mixsight.models.client import Client
from mixsight.models.user import User
from mixsight.models.user_client_access import UserClientAccess


async def enforce_client_access(
    client_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    client = await db.get(Client, client_id)
    if client is None or client.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Client not found")

    if client.organization_id != user.organization_id:
        # Cross-org: 404 to avoid leaking the client's existence.
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Client not found")

    if user.role == "admin":
        return  # Admin sees every client in their org.

    stmt = select(UserClientAccess).where(
        col(UserClientAccess.user_id) == user.id,
        col(UserClientAccess.client_id) == client_id,
        col(UserClientAccess.deleted_at).is_(None),
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Access denied")


async def enforce_organization_access(
    organization_id: UUID,
    user: User = Depends(current_user),
) -> None:
    if user.organization_id != organization_id:
        # Cross-org: 404 to avoid leaking existence.
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organization not found")


def require_role(
    role: str,
) -> Callable[[User], Coroutine[Any, Any, None]]:
    """Return a dep that enforces `user.role == role`. 403 otherwise."""

    async def _checker(user: User = Depends(current_user)) -> None:
        if user.role != role:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"{role} role required",
            )

    return _checker
