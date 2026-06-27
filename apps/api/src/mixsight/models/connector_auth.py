"""ConnectorAuth — organization-level OAuth credential per platform. Per §7.14.

One row per `(organization, platform)`. OAuth tokens are stored as
`EncryptedSecret` refs (never inline). `accessible_accounts` is the list of
ad accounts / properties the auth grants access to — populated on auth and
on subsequent validations; AMs pick from this list when wiring an
`AdAccountMapping` per (client, market).

`status` is `active` / `reauth_needed` / `revoked` per §7.14 — text rather
than Postgres ENUM for the migration-friction reason in `migration` skill.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class ConnectorAuth(SQLModel, table=True):
    __tablename__ = "connector_auth"
    __table_args__ = (
        UniqueConstraint("organization_id", "platform", name="connector_auth_org_platform_unique"),
    )

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="connector_auth_organization_id_fk"),
            nullable=False,
        ),
    )
    platform: str = Field(sa_column=Column(Text, nullable=False))
    oauth_token_ref: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "encrypted_secrets.id",
                name="connector_auth_oauth_token_ref_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
    )
    refresh_token_ref: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "encrypted_secrets.id",
                name="connector_auth_refresh_token_ref_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
    )
    token_expires_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    accessible_accounts: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="'[]'::jsonb"),
    )
    last_validated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    status: str = Field(
        default="active",
        sa_column=Column(Text, nullable=False, server_default="'active'"),
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
