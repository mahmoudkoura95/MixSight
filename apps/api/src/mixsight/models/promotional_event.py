"""PromotionalEvent — AM-entered date range with expected impact note. Per §7.4 + §8.2.

Phase 1a Week 3-4: minimal entry UI. Phase 2 modeling consumes these as
covariates in the MMM (Black Friday, end-of-season, regional holidays).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class PromotionalEvent(SQLModel, table=True):
    __tablename__ = "promotional_events"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="promotional_events_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="promotional_events_client_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="promotional_events_market_id_fk"),
            nullable=True,
        ),
    )
    name: str = Field(sa_column=Column(Text, nullable=False))
    event_type: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))
    expected_impact_notes: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
