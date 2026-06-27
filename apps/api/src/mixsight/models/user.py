"""User — belongs to Organization, has a role. Per §7.4 + §6.3.

Phase 1a Week 1 minimum fields. Clerk is the authentication source of truth;
our DB is the authorization source of truth (per §7.19). `clerk_user_id`
links the two; role is mirrored from Clerk via webhook.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="users_organization_id_fk"),
            nullable=False,
        ),
    )
    email: str = Field(sa_column=Column(Text, nullable=False))
    role: str = Field(
        sa_column=Column(
            Enum("admin", "account_manager", name="user_role"),
            nullable=False,
        ),
    )
    clerk_user_id: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    # See Organization.clerk_last_event_at — Clerk-clock high-water mark
    # so `is_stale_event` compares Clerk-to-Clerk, not server-vs-Clerk.
    clerk_last_event_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
