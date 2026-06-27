"""UserClientAccess — explicit grant of (User → Client) access. Per §6.3.

`organization_id` is denormalized from `User` for the AuditLog tenant-scope
stamp (Week 1 /code-review carry-over) — same rationale as `Market`.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import (
    SQLModel,
    created_at_column,
    deleted_at_column,
    pk_column,
)


class UserClientAccess(SQLModel, table=True):
    __tablename__ = "user_client_access"
    __table_args__ = (UniqueConstraint("user_id", "client_id", name="user_client_access_unique"),)

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    user_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("users.id", name="user_client_access_user_id_fk"),
            nullable=False,
        ),
    )
    client_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("clients.id", name="user_client_access_client_id_fk"),
            nullable=False,
        ),
    )
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="user_client_access_organization_id_fk"),
            nullable=False,
        ),
    )
    created_at: datetime = Field(default=None, sa_column=created_at_column())
    deleted_at: datetime | None = Field(default=None, sa_column=deleted_at_column())
