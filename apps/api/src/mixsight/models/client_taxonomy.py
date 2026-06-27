"""ClientTaxonomy — per-client dimension schema. Per §7.5.

Versioned per client. `dimensions` JSONB stores the full taxonomy schema
(see §7.5 default seeded shape). `seeded_from_template` UUID is filled in
when adopting a `PlanTemplate` (Phase 1b §7.7) — column is nullable UUID
without FK until the `plan_templates` table exists.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    pk_column,
    updated_at_column,
)


class ClientTaxonomy(SQLModel, table=True):
    __tablename__ = "client_taxonomies"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="client_taxonomies_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="client_taxonomies_client_id_fk"),
            nullable=False,
        ),
    )
    dimensions: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    seeded_from_template: uuid.UUID | None = Field(
        default=None, sa_column=Column(UUID(as_uuid=True), nullable=True)
    )
    version: int = Field(
        default=1, sa_column=Column(Integer, nullable=False, server_default=text("1"))
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
