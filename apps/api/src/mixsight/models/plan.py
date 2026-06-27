"""Plan — versioned media plan for a Client. Per §7.4 + §7.7.

`source_method` values: `csv_upload` (Phase 1a per ADR-003), `parser`
(Phase 1b §7.6), `template` (Phase 1b §7.7). `template_id` UUID without
FK until `plan_templates` exists.

`status` values: `draft`, `active`, `superseded`, `archived` — single
active version per client at a time (enforced at app layer; column is
plain Text rather than ENUM for migration ergonomics).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class Plan(SQLModel, table=True):
    __tablename__ = "plans"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="plans_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="plans_client_id_fk"),
            nullable=False,
        ),
    )
    version: int = Field(
        default=1, sa_column=Column(Integer, nullable=False, server_default=text("1"))
    )
    source_artifact_uri: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    source_method: str = Field(sa_column=Column(Text, nullable=False))
    template_id: uuid.UUID | None = Field(
        default=None, sa_column=Column(UUID(as_uuid=True), nullable=True)
    )
    status: str = Field(
        default="draft",
        sa_column=Column(Text, nullable=False, server_default="'draft'"),
    )
    period_start: date = Field(sa_column=Column(Date, nullable=False))
    period_end: date = Field(sa_column=Column(Date, nullable=False))
    currency_handling: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    ingested_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    ingested_by_user_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "users.id",
                name="plans_ingested_by_user_id_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
    )
    change_summary: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
