"""create tenancy schema (users, clients, markets, user_client_access)

Revision ID: 0002_create_tenancy_schema
Revises: 0001_create_organizations
Create Date: 2026-06-22

Phase 1a Week 1 minimum §7.4 entities needed to exercise the tenancy harness
(§7.19) and the AuditLog hook (§7.4). Field set per entity is minimum —
full §7.4 schema (currencies, allocation_mode, BYOK refs, etc.) lands Week 2.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_create_tenancy_schema"
down_revision: str | None = "0001_create_organizations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- users ----------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", name="users_organization_id_fk"),
            nullable=False,
        ),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM("admin", "account_manager", name="user_role"),
            nullable=False,
        ),
        sa.Column("clerk_user_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("clerk_user_id", name="users_clerk_user_id_unique"),
    )
    op.create_index("users_organization_id_idx", "users", ["organization_id"])
    op.create_index(
        "users_active_idx",
        "users",
        ["organization_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # --- clients --------------------------------------------------------
    op.create_table(
        "clients",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", name="clients_organization_id_fk"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("clients_organization_id_idx", "clients", ["organization_id"])
    op.create_index(
        "clients_active_idx",
        "clients",
        ["organization_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # --- markets --------------------------------------------------------
    op.create_table(
        "markets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="markets_client_id_fk"),
            nullable=False,
        ),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("markets_client_id_idx", "markets", ["client_id"])
    op.create_index(
        "markets_active_idx",
        "markets",
        ["client_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # --- user_client_access --------------------------------------------
    op.create_table(
        "user_client_access",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", name="user_client_access_user_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="user_client_access_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "client_id", name="user_client_access_unique"),
    )
    op.create_index("user_client_access_user_id_idx", "user_client_access", ["user_id"])
    op.create_index("user_client_access_client_id_idx", "user_client_access", ["client_id"])


def downgrade() -> None:
    op.drop_index("user_client_access_client_id_idx", table_name="user_client_access")
    op.drop_index("user_client_access_user_id_idx", table_name="user_client_access")
    op.drop_table("user_client_access")

    op.drop_index("markets_active_idx", table_name="markets")
    op.drop_index("markets_client_id_idx", table_name="markets")
    op.drop_table("markets")

    op.drop_index("clients_active_idx", table_name="clients")
    op.drop_index("clients_organization_id_idx", table_name="clients")
    op.drop_table("clients")

    op.drop_index("users_active_idx", table_name="users")
    op.drop_index("users_organization_id_idx", table_name="users")
    op.drop_table("users")
    # The named ENUM type lingers after drop_table; tear it down explicitly.
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
