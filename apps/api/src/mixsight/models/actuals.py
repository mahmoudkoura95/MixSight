"""Actuals — per-day per-campaign performance row. Per §7.4 + §7.14.

UNIQUE on `(client_id, market_id, channel, campaign_external_id, date, source)`
is the §7.14 idempotency contract. Every connector pull (CSV upload in
Phase 1a per ADR-003; API pulls Phase 1b/1c) upserts on this key.

Spend stored in market's local currency; reporting-currency value computed
at ingestion time via `fx_rate_used` and surfaced on read. §6.2 numeric
discipline: `numeric(18, 4)` for money, `numeric(20, 10)` for FX.
"""

from __future__ import annotations

import uuid
from datetime import date as date_
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    pk_column,
    updated_at_column,
)


class Actuals(SQLModel, table=True):
    __tablename__ = "actuals"
    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "market_id",
            "channel",
            "campaign_external_id",
            "date",
            "source",
            name="actuals_unique_pull",
        ),
    )

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="actuals_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="actuals_client_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="actuals_market_id_fk"),
            nullable=False,
        ),
    )
    channel: str = Field(sa_column=Column(Text, nullable=False))
    campaign_external_id: str = Field(sa_column=Column(Text, nullable=False))
    campaign_label: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    date: date_ = Field(sa_column=Column(Date, nullable=False))
    spend_local: Decimal = Field(sa_column=Column(Numeric(18, 4), nullable=False))
    spend_reporting: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    impressions: int | None = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    clicks: int | None = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    conversions: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    conversions_value: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    conversions_alt_attributions: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    labels: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    source: str = Field(sa_column=Column(Text, nullable=False))
    pull_timestamp: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    pull_window_start: date_ | None = Field(default=None, sa_column=Column(Date, nullable=True))
    pull_window_end: date_ | None = Field(default=None, sa_column=Column(Date, nullable=True))
    fx_rate_used: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(20, 10), nullable=True)
    )
    archived_at_source: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
