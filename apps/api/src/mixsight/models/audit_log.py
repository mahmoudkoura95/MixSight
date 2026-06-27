"""AuditLog — §7.4 + §6.6.

Append-only. Every mutation across the §7.4 entity set writes here via the
SQLAlchemy event hook in `mixsight.audit.hooks`. 7-year retention; field
scrubbing on customer deletion per §6.6 anonymization (Phase 2+).

Neither `organization_id` nor `actor_user_id` is a foreign key — the audit
trail outlives the entities it audits, so orphaned references are
intentional (and FK enforcement would block hard-deleting an Organization
in the same transaction the audit hook tries to log).

`metadata_` is the Python-side name for the JSONB column named `metadata` in
SQL. The name clashes with SQLAlchemy's `MetaData` if used directly on a
mapped class, hence the underscore suffix mapped via `sa_column(name=...)`.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(UUID(as_uuid=True), nullable=True),
    )
    actor_user_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(UUID(as_uuid=True), nullable=True),
    )
    entity_type: str = Field(sa_column=Column(Text, nullable=False))
    entity_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False),
    )
    action: str = Field(sa_column=Column(Text, nullable=False))
    before: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )
    after: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )
    occurred_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    request_id: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    metadata_: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column("metadata", JSONB, nullable=True),
    )
