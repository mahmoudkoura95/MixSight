"""ReconciliationFactor — Mode A vs Mode B reconciliation per (channel, week). Per §7.4 + §7.9.

Captures the ratio between platform-native and cross-platform (GA4) measurement
for an `(client, market, channel, week)`. Surfaced inline in the evidence-column
drilldown. UNIQUE on the dimension tuple — one row per week per channel per
(client, market).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class ReconciliationFactor(SQLModel, table=True):
    __tablename__ = "reconciliation_factors"
    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "market_id",
            "channel",
            "week_ending",
            name="reconciliation_factors_unique_week",
        ),
    )

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="reconciliation_factors_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="reconciliation_factors_client_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="reconciliation_factors_market_id_fk"),
            nullable=False,
        ),
    )
    channel: str = Field(sa_column=Column(Text, nullable=False))
    week_ending: date = Field(sa_column=Column(Date, nullable=False))
    ga4_to_platform_ratio: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 6), nullable=True)
    )
    sample_size: int | None = Field(default=None, sa_column=Column(Integer, nullable=True))
    confidence: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
