"""DefenseKit — the Monday-morning artifact. Per §7.13 + §7.17.

Two render modes: per-market and rolled-up. HTML server-rendered + PDF via
Playwright. `narrative_status` tracks the §7.17 LLM-dependence state:
`generated` (LLM succeeded), `templated_fallback` (LLM failed, structural
narrative used), `regenerated` (AM re-ran after fallback).

**Defense kit never blocks on LLM** — when narrative_status =
`templated_fallback`, the row is still complete and shippable.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    pk_column,
    updated_at_column,
)


class DefenseKit(SQLModel, table=True):
    __tablename__ = "defense_kits"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="defense_kits_organization_id_fk"),
            nullable=False,
        ),
    )
    snapshot_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("pacing_snapshots.id", name="defense_kits_snapshot_id_fk"),
            nullable=False,
        ),
    )
    render_mode: str = Field(sa_column=Column(Text, nullable=False))
    narrative_text: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    narrative_status: str = Field(
        default="pending",
        sa_column=Column(Text, nullable=False, server_default="'pending'"),
    )
    included_suggestion_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "reallocation_suggestions.id",
                name="defense_kits_included_suggestion_id_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
    )
    generated_pdf_uri: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    am_user_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("users.id", name="defense_kits_am_user_id_fk", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    sent_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
