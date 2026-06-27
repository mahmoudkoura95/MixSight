"""Client — a brand under an Organization. One billable workspace. Per §7.4.

`reporting_currency` is ISO 4217; nullable until the client is configured
during AM onboarding. `default_allocation_mode` is `mode_a` for Phase 1a
(platform-native only); `mode_b` and paired views land Phase 1b.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="clients_organization_id_fk"),
            nullable=False,
        ),
    )
    name: str = Field(sa_column=Column(Text, nullable=False))
    reporting_currency: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    default_allocation_mode: str = Field(
        default="mode_a",
        sa_column=Column(Text, nullable=False, server_default="'mode_a'"),
    )
    source_of_truth_config: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    settling_visual_enabled: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    daily_refresh_window_days: int = Field(
        default=7,
        sa_column=Column(Integer, nullable=False, server_default=text("7")),
    )
    llm_byok_key_ref: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "encrypted_secrets.id",
                name="clients_llm_byok_key_ref_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
    )
    llm_byok_fallback_enabled: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
