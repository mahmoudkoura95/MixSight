"""MacroSignal — external signal per market per date. Per §7.4.

Signal types: Google Trends (brand + category), holidays, weather, CPI,
custom. Provisioned empty in Phase 1a per the locked decision. Populated
from Phase 2a onward; Google Trends backfilled at Phase 2 start per §8.4.
"""

from __future__ import annotations

import uuid
from datetime import date as date_
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class MacroSignal(SQLModel, table=True):
    __tablename__ = "macro_signals"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="macro_signals_organization_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="macro_signals_market_id_fk"),
            nullable=False,
        ),
    )
    signal_type: str = Field(sa_column=Column(Text, nullable=False))
    date: date_ = Field(sa_column=Column(Date, nullable=False))
    value: Decimal | None = Field(default=None, sa_column=Column(Numeric(20, 6), nullable=True))
    source: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    captured_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
