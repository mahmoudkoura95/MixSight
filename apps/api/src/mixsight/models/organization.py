"""Organization — top of the tenancy tree (the agency). Per §7.4.

`clerk_organization_id` is the link between Clerk's Organization (the auth
truth) and ours (the authorization truth). Webhook handlers (Day 4) upsert
on this. Unique nullable so Phase 1a-era seed orgs without a Clerk match
still validate.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    name: str = Field(sa_column=Column(Text, nullable=False))
    branding_config: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    clerk_organization_id: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True, unique=True),
    )
    billing_customer_id: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    plan_tier: str = Field(
        default="starter",
        sa_column=Column(Text, nullable=False, server_default="'starter'"),
    )
    deletion_status: str = Field(
        default="active",
        sa_column=Column(Text, nullable=False, server_default="'active'"),
    )
    grace_period_ends_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    settling_visual_default: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    notification_preferences: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="'{}'::jsonb"),
    )
    # Clerk-clock timestamp of the most recently-applied webhook event.
    # Read by `is_stale_event` to compare Clerk-to-Clerk (avoids the server-
    # vs-Clerk clock-skew false-positive). Nullable — first event applies.
    clerk_last_event_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
