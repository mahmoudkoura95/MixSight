"""Market — geographic market within a Client. Per §7.4.

`organization_id` is denormalized from `Client` so the §7.4 AuditLog hook
can stamp tenant-scope without a cross-table lookup during flush (Week 1
/code-review carry-over). `local_timezone` (IANA) drives the daily pull
cron timing per §7.14.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
    updated_at_column,
)


class Market(SQLModel, table=True):
    __tablename__ = "markets"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="markets_client_id_fk"),
            nullable=False,
        ),
    )
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="markets_organization_id_fk"),
            nullable=False,
        ),
    )
    code: str = Field(sa_column=Column(Text, nullable=False))
    local_currency: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    reallocation_constraint: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    local_timezone: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    updated_at: datetime = Field(default=None, sa_column=updated_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
