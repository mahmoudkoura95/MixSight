"""ContributionFit — MMM model fit metadata + diagnostics. Phase 2. Per §7.4.

Provisioned empty in Phase 1a per the locked decision. Populated when MMM
ships in Phase 2a (PyMC-Marketing engine first per §6.2 / §8.2).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import Column, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class ContributionFit(SQLModel, table=True):
    __tablename__ = "contribution_fits"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="contribution_fits_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="contribution_fits_client_id_fk"),
            nullable=False,
        ),
    )
    model_version: str = Field(sa_column=Column(Text, nullable=False))
    engine: str = Field(sa_column=Column(Text, nullable=False))
    fit_date: date = Field(sa_column=Column(Date, nullable=False))
    training_window_start: date = Field(sa_column=Column(Date, nullable=False))
    training_window_end: date = Field(sa_column=Column(Date, nullable=False))
    parameters_uri: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    diagnostics: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    status: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
