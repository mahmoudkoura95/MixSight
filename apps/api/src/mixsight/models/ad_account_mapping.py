"""AdAccountMapping — `(client, market) → platform ad account`. Per §7.14.

The §7.14 credential model: organization-level auth + per-(client, market)
ad account mapping. One platform ad account can map to multiple
(client, market) tuples (rare but allowed — agency may run two MixSight
workspaces against one Meta Ads account).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class AdAccountMapping(SQLModel, table=True):
    __tablename__ = "ad_account_mappings"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="ad_account_mappings_organization_id_fk"),
            nullable=False,
        ),
    )
    market_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("markets.id", name="ad_account_mappings_market_id_fk"),
            nullable=False,
        ),
    )
    platform: str = Field(sa_column=Column(Text, nullable=False))
    connector_auth_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey(
                "connector_auth.id",
                name="ad_account_mappings_connector_auth_id_fk",
            ),
            nullable=False,
        ),
    )
    external_account_id: str = Field(sa_column=Column(Text, nullable=False))
    account_label: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
