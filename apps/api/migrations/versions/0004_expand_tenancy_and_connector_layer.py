"""expand tenancy + connector layer

Revision ID: 0004_connector_layer
Revises: 0003_create_audit_log
Create Date: 2026-06-25

Week 2 / Day 2-3 of Phase 1a. Expands the Week 1 minimum entities to their
full §7.4 field set and lays the §7.14 connector substrate (EncryptedSecret,
MarketConfig, ConnectorAuth, AdAccountMapping, ConnectorAuthEvent).

§7.4 fields added to existing entities — Organization (clerk_organization_id,
billing_customer_id, plan_tier, deletion_status, grace_period_ends_at,
settling_visual_default, notification_preferences); Client (reporting_currency,
default_allocation_mode, source_of_truth_config, settling_visual_enabled,
daily_refresh_window_days, llm_byok_key_ref, llm_byok_fallback_enabled);
Market (organization_id denormalized, local_currency, reallocation_constraint,
local_timezone); UserClientAccess (organization_id denormalized).

The `organization_id` denormalization on Market + UserClientAccess closes
the Week 1 /code-review finding about AuditLog rows being unscopeable per
tenant for these entities. Backfill SELECTs populate the columns from the
existing FK chain before flipping to NOT NULL — works on both empty (CI)
and populated (dev) databases.

Enum-ish fields ship as Text rather than Postgres ENUM types to avoid the
ALTER-TYPE friction §6.2 implies. The user_role ENUM from migration 0002
stays as-is for backwards compatibility.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_connector_layer"
down_revision: str | None = "0003_create_audit_log"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # encrypted_secrets (no FKs; created first so other tables can FK it)
    # ------------------------------------------------------------------
    op.create_table(
        "encrypted_secrets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("key_version", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("accessed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "encrypted_secrets_key_version_idx",
        "encrypted_secrets",
        ["key_version"],
    )

    # ------------------------------------------------------------------
    # Expand organizations
    # ------------------------------------------------------------------
    op.add_column(
        "organizations",
        sa.Column("clerk_organization_id", sa.Text(), nullable=True),
    )
    op.create_unique_constraint(
        "organizations_clerk_organization_id_unique",
        "organizations",
        ["clerk_organization_id"],
    )
    op.add_column("organizations", sa.Column("billing_customer_id", sa.Text(), nullable=True))
    op.add_column(
        "organizations",
        sa.Column(
            "plan_tier",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'starter'"),
        ),
    )
    op.add_column(
        "organizations",
        sa.Column(
            "deletion_status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("grace_period_ends_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column(
            "settling_visual_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "organizations",
        sa.Column(
            "notification_preferences",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    # ------------------------------------------------------------------
    # Expand clients
    # ------------------------------------------------------------------
    op.add_column("clients", sa.Column("reporting_currency", sa.Text(), nullable=True))
    op.add_column(
        "clients",
        sa.Column(
            "default_allocation_mode",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'mode_a'"),
        ),
    )
    op.add_column(
        "clients",
        sa.Column(
            "source_of_truth_config",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "clients",
        sa.Column(
            "settling_visual_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "clients",
        sa.Column(
            "daily_refresh_window_days",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("7"),
        ),
    )
    op.add_column(
        "clients",
        sa.Column(
            "llm_byok_key_ref",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "encrypted_secrets.id",
                name="clients_llm_byok_key_ref_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
    )
    op.add_column(
        "clients",
        sa.Column(
            "llm_byok_fallback_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # ------------------------------------------------------------------
    # Expand markets — full §7.4 + organization_id denormalization
    # ------------------------------------------------------------------
    op.add_column("markets", sa.Column("local_currency", sa.Text(), nullable=True))
    op.add_column("markets", sa.Column("reallocation_constraint", sa.Text(), nullable=True))
    op.add_column("markets", sa.Column("local_timezone", sa.Text(), nullable=True))
    op.add_column(
        "markets",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        "UPDATE markets SET organization_id = clients.organization_id "
        "FROM clients WHERE clients.id = markets.client_id"
    )
    op.alter_column("markets", "organization_id", nullable=False)
    op.create_foreign_key(
        "markets_organization_id_fk",
        "markets",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_index("markets_organization_id_idx", "markets", ["organization_id"])

    # ------------------------------------------------------------------
    # Expand user_client_access — organization_id denormalization
    # ------------------------------------------------------------------
    op.add_column(
        "user_client_access",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        "UPDATE user_client_access "
        "SET organization_id = users.organization_id "
        "FROM users WHERE users.id = user_client_access.user_id"
    )
    op.alter_column("user_client_access", "organization_id", nullable=False)
    op.create_foreign_key(
        "user_client_access_organization_id_fk",
        "user_client_access",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_index(
        "user_client_access_organization_id_idx",
        "user_client_access",
        ["organization_id"],
    )

    # ------------------------------------------------------------------
    # market_configs — per-market attribution settings + GA4 property
    # ------------------------------------------------------------------
    op.create_table(
        "market_configs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "markets.id",
                name="market_configs_market_id_fk",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "attribution_settings",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("ga4_property_id", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("market_id", name="market_configs_market_id_unique"),
    )

    # ------------------------------------------------------------------
    # connector_auth — org-level OAuth credential per platform
    # ------------------------------------------------------------------
    op.create_table(
        "connector_auth",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", name="connector_auth_organization_id_fk"),
            nullable=False,
        ),
        sa.Column("platform", sa.Text(), nullable=False),
        sa.Column(
            "oauth_token_ref",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "encrypted_secrets.id",
                name="connector_auth_oauth_token_ref_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "refresh_token_ref",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "encrypted_secrets.id",
                name="connector_auth_refresh_token_ref_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "accessible_accounts",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'active'")),
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
        sa.UniqueConstraint(
            "organization_id", "platform", name="connector_auth_org_platform_unique"
        ),
    )
    op.create_index(
        "connector_auth_organization_id_idx",
        "connector_auth",
        ["organization_id"],
    )

    # ------------------------------------------------------------------
    # ad_account_mappings — (client, market) → platform ad account
    # ------------------------------------------------------------------
    op.create_table(
        "ad_account_mappings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="ad_account_mappings_market_id_fk"),
            nullable=False,
        ),
        sa.Column("platform", sa.Text(), nullable=False),
        sa.Column(
            "connector_auth_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "connector_auth.id",
                name="ad_account_mappings_connector_auth_id_fk",
            ),
            nullable=False,
        ),
        sa.Column("external_account_id", sa.Text(), nullable=False),
        sa.Column("account_label", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
    op.create_index(
        "ad_account_mappings_market_platform_idx",
        "ad_account_mappings",
        ["market_id", "platform"],
    )
    op.create_index(
        "ad_account_mappings_connector_auth_id_idx",
        "ad_account_mappings",
        ["connector_auth_id"],
    )

    # ------------------------------------------------------------------
    # connector_auth_events — credential-lifecycle + CSV ingestion log
    # ------------------------------------------------------------------
    op.create_table(
        "connector_auth_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "organizations.id",
                name="connector_auth_events_organization_id_fk",
            ),
            nullable=False,
        ),
        sa.Column("platform", sa.Text(), nullable=False),
        sa.Column(
            "connector_auth_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "connector_auth.id",
                name="connector_auth_events_connector_auth_id_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error_code", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "connector_auth_events_organization_id_idx",
        "connector_auth_events",
        ["organization_id", "occurred_at"],
    )
    op.create_index(
        "connector_auth_events_connector_auth_id_idx",
        "connector_auth_events",
        ["connector_auth_id"],
    )


def downgrade() -> None:
    # Drop new tables first (FK fan-out from existing tables to these)
    op.drop_index(
        "connector_auth_events_connector_auth_id_idx",
        table_name="connector_auth_events",
    )
    op.drop_index(
        "connector_auth_events_organization_id_idx",
        table_name="connector_auth_events",
    )
    op.drop_table("connector_auth_events")

    op.drop_index(
        "ad_account_mappings_connector_auth_id_idx",
        table_name="ad_account_mappings",
    )
    op.drop_index(
        "ad_account_mappings_market_platform_idx",
        table_name="ad_account_mappings",
    )
    op.drop_table("ad_account_mappings")

    op.drop_index("connector_auth_organization_id_idx", table_name="connector_auth")
    op.drop_table("connector_auth")

    op.drop_table("market_configs")

    # Drop denormalized columns + their indexes
    op.drop_index(
        "user_client_access_organization_id_idx",
        table_name="user_client_access",
    )
    op.drop_constraint(
        "user_client_access_organization_id_fk",
        "user_client_access",
        type_="foreignkey",
    )
    op.drop_column("user_client_access", "organization_id")

    op.drop_index("markets_organization_id_idx", table_name="markets")
    op.drop_constraint("markets_organization_id_fk", "markets", type_="foreignkey")
    op.drop_column("markets", "organization_id")
    op.drop_column("markets", "local_timezone")
    op.drop_column("markets", "reallocation_constraint")
    op.drop_column("markets", "local_currency")

    # Drop Client expansion columns
    op.drop_column("clients", "llm_byok_fallback_enabled")
    op.drop_constraint("clients_llm_byok_key_ref_fk", "clients", type_="foreignkey")
    op.drop_column("clients", "llm_byok_key_ref")
    op.drop_column("clients", "daily_refresh_window_days")
    op.drop_column("clients", "settling_visual_enabled")
    op.drop_column("clients", "source_of_truth_config")
    op.drop_column("clients", "default_allocation_mode")
    op.drop_column("clients", "reporting_currency")

    # Drop Organization expansion columns
    op.drop_column("organizations", "notification_preferences")
    op.drop_column("organizations", "settling_visual_default")
    op.drop_column("organizations", "grace_period_ends_at")
    op.drop_column("organizations", "deletion_status")
    op.drop_column("organizations", "plan_tier")
    op.drop_column("organizations", "billing_customer_id")
    op.drop_constraint(
        "organizations_clerk_organization_id_unique",
        "organizations",
        type_="unique",
    )
    op.drop_column("organizations", "clerk_organization_id")

    # Finally drop encrypted_secrets (nothing references it now)
    op.drop_index("encrypted_secrets_key_version_idx", table_name="encrypted_secrets")
    op.drop_table("encrypted_secrets")
