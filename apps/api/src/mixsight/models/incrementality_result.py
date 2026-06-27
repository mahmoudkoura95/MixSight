"""IncrementalityResult — lift estimates. Phase 2/3. Per §7.4.

Sourced from geo holdout tests + platform-native lift studies. Provisioned
empty in Phase 1a per the locked decision. Phase 2 ingestion; Phase 3
design (§9.2 geo holdout designer). Lift values are percentages stored
as `numeric(8, 4)` per §6.2.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class IncrementalityResult(SQLModel, table=True):
    __tablename__ = "incrementality_results"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="incrementality_results_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="incrementality_results_client_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="incrementality_results_market_id_fk"),
            nullable=True,
        ),
    )
    channel: str = Field(sa_column=Column(Text, nullable=False))
    test_type: str = Field(sa_column=Column(Text, nullable=False))
    test_start: date = Field(sa_column=Column(Date, nullable=False))
    test_end: date = Field(sa_column=Column(Date, nullable=False))
    lift_estimate: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(8, 4), nullable=True)
    )
    lift_ci_low: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(8, 4), nullable=True)
    )
    lift_ci_high: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(8, 4), nullable=True)
    )
    source: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    notes: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
