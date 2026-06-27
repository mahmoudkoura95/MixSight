"""ForecastRun — append-only record of a forecast generation. Phase 3. Per §7.4.

Provisioned empty in Phase 1a per the locked decision. Populated when
forecasting ships in Phase 3a (§9.2 pre-flight + in-flight + reforecast).

Append-only — excluded from the §7.4 AuditLog event hook (audit-log skill).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class ForecastRun(SQLModel, table=True):
    __tablename__ = "forecast_runs"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="forecast_runs_client_id_fk"),
            nullable=False,
        ),
    )
    run_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    run_type: str = Field(sa_column=Column(Text, nullable=False))
    input_plan_version: int | None = Field(default=None, sa_column=Column(Integer, nullable=True))
    input_model_fit_id: uuid.UUID | None = Field(
        default=None, sa_column=Column(UUID(as_uuid=True), nullable=True)
    )
    input_external_signals_uri: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    output_trajectory: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    output_summary: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
