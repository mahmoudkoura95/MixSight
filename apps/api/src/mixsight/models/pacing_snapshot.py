"""PacingSnapshot + PacingSnapshotLine — weekly frozen pacing view. Per §7.4 + §7.16.

The PacingSnapshot is the Monday-morning artifact: a frozen, dated snapshot
of pacing per (client, market, week, allocation_mode). PacingSnapshotLine
holds one row per plan line, with both spend and KPI drift, status, and
the evidence-column payload.

`is_partial_week` is the §7.18 empty-state flag for backfill-in-progress
clients. `drift_explanation_status` tracks LLM-generated text per §7.17.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class PacingSnapshot(SQLModel, table=True):
    __tablename__ = "pacing_snapshots"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="pacing_snapshots_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="pacing_snapshots_client_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="pacing_snapshots_market_id_fk"),
            nullable=False,
        ),
    )
    week_ending: date = Field(sa_column=Column(Date, nullable=False))
    allocation_mode: str = Field(sa_column=Column(Text, nullable=False))
    fx_rate_used: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(20, 10), nullable=True)
    )
    generated_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    is_partial_week: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )


class PacingSnapshotLine(SQLModel, table=True):
    __tablename__ = "pacing_snapshot_lines"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "organizations.id",
                name="pacing_snapshot_lines_organization_id_fk",
            ),
            nullable=False,
        ),
    )
    snapshot_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "pacing_snapshots.id",
                name="pacing_snapshot_lines_snapshot_id_fk",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
    )
    plan_line_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("plan_lines.id", name="pacing_snapshot_lines_plan_line_id_fk"),
            nullable=False,
        ),
    )
    actual_spend_to_date: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    planned_spend_to_date: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    spend_drift_pct: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(8, 4), nullable=True)
    )
    actual_kpi_to_date: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    planned_kpi_to_date: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    kpi_drift_pct: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(8, 4), nullable=True)
    )
    status: str = Field(sa_column=Column(Text, nullable=False))
    drift_explanation_text: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    drift_explanation_status: str = Field(
        default="pending",
        sa_column=Column(Text, nullable=False, server_default="'pending'"),
    )
    evidence_payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    objective_type: str = Field(sa_column=Column(Text, nullable=False))
    labels: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
