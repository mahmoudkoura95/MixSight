"""EncryptedSecret — Fernet-encrypted blob with `key_version` for rotation.

Per §7.4 + §6.6: every OAuth token, refresh token, and BYOK API key is
stored as an `EncryptedSecret` row referenced by FK from the owning table
(`ConnectorAuth.oauth_token_ref`, `Client.llm_byok_key_ref`, etc.). Master
key from environment via Fernet. Never log the ciphertext or the resolved
plaintext.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from mixsight.models.base import SQLModel, pk_column


class EncryptedSecret(SQLModel, table=True):
    __tablename__ = "encrypted_secrets"

    id: uuid.UUID = Field(default=None, sa_column=pk_column())
    organization_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", name="encrypted_secrets_organization_id_fk"),
            nullable=False,
        ),
    )
    ciphertext: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    key_version: int = Field(sa_column=Column(Integer, nullable=False))
    purpose: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    accessed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
