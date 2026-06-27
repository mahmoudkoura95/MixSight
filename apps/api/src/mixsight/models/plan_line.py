"""PlanLine — one row of a Plan: market × channel × period × spend. Per §7.4.

`planned_spend_local` is `numeric(18,4)` (§6.2 money convention). Stored in
each market's local currency; `planned_spend_reporting` is computed at
ingestion time via FX rate.

`objective_type` values per §7.5 ClientTaxonomy seeded schema: conversions,
traffic, reach, engagement, video_views, app_installs, leads. Drives the
§7.8 drift formula branch.

`labels` JSONB is the per-line dimension values applied by `CampaignLabelRule`
or by the AI parser (§7.6 Phase 1b). GIN index for filter-bar queries.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Column, Date, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class PlanLine(SQLModel, table=True):
    __tablename__ = "plan_lines"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="plan_lines_organization_id_fk"),
            nullable=False,
        ),
    )
    plan_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("plans.id", name="plan_lines_plan_id_fk", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="plan_lines_market_id_fk"),
            nullable=False,
        ),
    )
    channel: str = Field(sa_column=Column(Text, nullable=False))
    campaign_label: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    period_start: date = Field(sa_column=Column(Date, nullable=False))
    period_end: date = Field(sa_column=Column(Date, nullable=False))
    planned_spend_local: Decimal = Field(sa_column=Column(Numeric(18, 4), nullable=False))
    planned_spend_reporting: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    objective_type: str = Field(
        default="conversions",
        sa_column=Column(Text, nullable=False, server_default="'conversions'"),
    )
    kpi_target: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    kpi_target_efficiency: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    labels: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    extraction_confidence: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
