"""MarketConfig — per-market attribution + GA4 property. Per §7.4.

One row per Market (UNIQUE constraint). Splitting from `Market` keeps the
core tenant row narrow while letting the AM-configurable surface evolve
with the platform-specific attribution model.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    pk_column,
    updated_at_column,
)


class MarketConfig(SQLModel, table=True):
    __tablename__ = "market_configs"
    __table_args__ = (UniqueConstraint("market_id", name="market_configs_market_id_unique"),)

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="market_configs_organization_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "markets.id",
                name="market_configs_market_id_fk",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
    )
    attribution_settings: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    ga4_property_id: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
