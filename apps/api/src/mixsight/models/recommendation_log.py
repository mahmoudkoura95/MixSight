"""RecommendationLog — append-only calibration record. Per §7.10 step 11.

Every `ReallocationSuggestion` creation writes a `RecommendationLog` row,
capturing prediction + (later) observed outcome. The Phase 4 calibration UI
(§10.2 'the tool that knows its own track record') reads this history to
surface per-channel / per-customer accuracy.

Append-only — excluded from the §7.4 AuditLog event hook per the audit-log
skill. `implemented`, `observed_outcome`, etc. fill in over time as the
recommendation is executed and outcomes resolve.

`recommendation_source` values: `heuristic_v1` (Phase 1), `model_v2`
(Phase 2 MMM-derived).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

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
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class RecommendationLog(SQLModel, table=True):
    __tablename__ = "recommendation_log"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="recommendation_log_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="recommendation_log_client_id_fk"),
            nullable=False,
        ),
    )
    suggestion_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "reallocation_suggestions.id",
                name="recommendation_log_suggestion_id_fk",
            ),
            nullable=False,
        ),
    )
    recommended_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    predicted_delta: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    predicted_confidence: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(8, 4), nullable=True)
    )
    recommendation_source: str = Field(sa_column=Column(Text, nullable=False))
    implemented: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    implemented_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    implemented_amount: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    observed_outcome: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(18, 4), nullable=True)
    )
    outcome_window_end: date | None = Field(default=None, sa_column=Column(Date, nullable=True))
    calibration_score: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(8, 4), nullable=True)
    )
