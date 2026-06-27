"""Shared model base + column factories.

Per §6.2: every table has a UUID PK from `gen_random_uuid()`, timestamptz
`created_at` / `updated_at` / `deleted_at`, and a partial index on
`deleted_at IS NULL` for the hot query path.

These factories return a fresh `Column` instance on each call so each table
gets its own SQLAlchemy object — SA doesn't allow column reuse across tables.
Migrations duplicate these conventions in raw form; the factories cover the
ORM side.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import SQLModel

__all__ = [
    "SQLModel",
    "created_at_column",
    "deleted_at_column",
    "pk_column",
    "updated_at_column",
]


def pk_column() -> Column[Any]:
    return Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )


def created_at_column() -> Column[Any]:
    return Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


def updated_at_column() -> Column[Any]:
    return Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def deleted_at_column() -> Column[Any]:
    return Column(DateTime(timezone=True), nullable=True)
