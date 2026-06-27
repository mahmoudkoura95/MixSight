"""CampaignLabelRule — per-client (optionally per-market) label assignment. Per §7.5.

Rules evaluated in `priority` order; first match wins. Rule types:
`regex` (match on campaign name), `prefix_match` (simpler regex), `lookup_table`
(AM-maintained mapping), `explicit_assignment` (AM-clicked).
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


class CampaignLabelRule(SQLModel, table=True):
    __tablename__ = "campaign_label_rules"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="campaign_label_rules_organization_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="campaign_label_rules_client_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="campaign_label_rules_market_id_fk"),
            nullable=True,
        ),
    )
    rule_type: str = Field(sa_column=Column(Text, nullable=False))
    rule_config: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    label_assignments: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    priority: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, server_default=text("0"))
    )
    active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
