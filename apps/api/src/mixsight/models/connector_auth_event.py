"""ConnectorAuthEvent — append-only log of credential-lifecycle + CSV-ingestion events.

Per ADR-003: event_type values cover API + CSV. API-side: `initial_auth`,
`refresh`, `reauth`, `revoked`, `validated`. CSV-side: `csv_uploaded`,
`csv_parse_failed`, `schema_mismatch`, `partial_ingestion`.

This table is **append-only** and excluded from the §7.4 AuditLog SQLAlchemy
event hook (per audit-log skill). It IS its own audit trail.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class ConnectorAuthEvent(SQLModel, table=True):
    __tablename__ = "connector_auth_events"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "organizations.id",
                name="connector_auth_events_organization_id_fk",
            ),
            nullable=False,
        ),
    )
    platform: str = Field(sa_column=Column(Text, nullable=False))
    connector_auth_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "connector_auth.id",
                name="connector_auth_events_connector_auth_id_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
    )
    event_type: str = Field(sa_column=Column(Text, nullable=False))
    user_id: uuid.UUID | None = Field(
        default=None, sa_column=Column(UUID(as_uuid=True), nullable=True)
    )
    success: bool = Field(sa_column=Column(Boolean, nullable=False))
    error_code: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    error_message: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    occurred_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
