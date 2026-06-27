"""ConnectorPull — append-only log of every actuals pull. Per §7.4 + §7.14.

One row per pull attempt regardless of outcome. `pull_type` covers daily /
weekly / monthly / backfill / manual / catch_up per §7.14. `rows_revised`
tracks restatement (existing row's value changed > threshold).

Append-only — excluded from the §7.4 AuditLog event hook (audit-log skill).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class ConnectorPull(SQLModel, table=True):
    __tablename__ = "connector_pulls"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="connector_pulls_client_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="connector_pulls_market_id_fk"),
            nullable=False,
        ),
    )
    platform: str = Field(sa_column=Column(Text, nullable=False))
    pull_window_start: date = Field(sa_column=Column(Date, nullable=False))
    pull_window_end: date = Field(sa_column=Column(Date, nullable=False))
    pull_type: str = Field(sa_column=Column(Text, nullable=False))
    status: str = Field(sa_column=Column(Text, nullable=False))
    rows_fetched: int | None = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    rows_upserted: int | None = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    rows_revised: int | None = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    error_message: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    attempted_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    completed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
