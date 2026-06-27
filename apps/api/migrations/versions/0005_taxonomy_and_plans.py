"""create taxonomy + plans tables

Revision ID: 0005_taxonomy_plans
Revises: 0004_connector_layer
Create Date: 2026-06-25

Week 2 / Day 2-3. ClientTaxonomy + CampaignLabelRule per §7.5; Plan + PlanLine
per §7.4.

`Plan.template_id` and `ClientTaxonomy.seeded_from_template` are nullable
UUIDs without FK constraints — the `PlanTemplate` table lands in Phase 1b
(§7.7), at which point a migration will add the FK constraints.

`PlanLine.objective_type` ships as Text rather than Postgres ENUM for the
same migration-friction reason as the rest of the connector layer; the
app-level validation accepts §7.5's seven values (conversions, traffic,
reach, engagement, video_views, app_installs, leads).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_taxonomy_plans"
down_revision: str | None = "0004_connector_layer"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- client_taxonomies ---------------------------------------------
    op.create_table(
        "client_taxonomies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="client_taxonomies_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "dimensions",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "seeded_from_template",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
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
    )
    op.create_index(
        "client_taxonomies_client_version_idx",
        "client_taxonomies",
        ["client_id", "version"],
    )
    op.create_index(
        "client_taxonomies_dimensions_gin",
        "client_taxonomies",
        ["dimensions"],
        postgresql_using="gin",
    )

    # --- campaign_label_rules ------------------------------------------
    op.create_table(
        "campaign_label_rules",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="campaign_label_rules_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="campaign_label_rules_market_id_fk"),
            nullable=True,
        ),
        sa.Column("rule_type", sa.Text(), nullable=False),
        sa.Column(
            "rule_config",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "label_assignments",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("0")),
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
        "campaign_label_rules_client_priority_idx",
        "campaign_label_rules",
        ["client_id", "priority"],
    )

    # --- plans ---------------------------------------------------------
    op.create_table(
        "plans",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="plans_client_id_fk"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("source_artifact_uri", sa.Text(), nullable=True),
        sa.Column("source_method", sa.Text(), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("currency_handling", sa.Text(), nullable=True),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "ingested_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id",
                name="plans_ingested_by_user_id_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column("change_summary", sa.Text(), nullable=True),
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
    op.create_index("plans_client_version_idx", "plans", ["client_id", "version"])

    # --- plan_lines ----------------------------------------------------
    op.create_table(
        "plan_lines",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plans.id", name="plan_lines_plan_id_fk", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="plan_lines_market_id_fk"),
            nullable=False,
        ),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("campaign_label", sa.Text(), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("planned_spend_local", sa.Numeric(18, 4), nullable=False),
        sa.Column("planned_spend_reporting", sa.Numeric(18, 4), nullable=True),
        sa.Column(
            "objective_type",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'conversions'"),
        ),
        sa.Column("kpi_target", sa.Numeric(18, 4), nullable=True),
        sa.Column("kpi_target_efficiency", sa.Numeric(18, 4), nullable=True),
        sa.Column(
            "labels",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("extraction_confidence", sa.Text(), nullable=True),
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
    op.create_index("plan_lines_plan_id_idx", "plan_lines", ["plan_id"])
    op.create_index("plan_lines_market_id_idx", "plan_lines", ["market_id"])
    op.create_index(
        "plan_lines_labels_gin",
        "plan_lines",
        ["labels"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("plan_lines_labels_gin", table_name="plan_lines")
    op.drop_index("plan_lines_market_id_idx", table_name="plan_lines")
    op.drop_index("plan_lines_plan_id_idx", table_name="plan_lines")
    op.drop_table("plan_lines")

    op.drop_index("plans_client_version_idx", table_name="plans")
    op.drop_table("plans")

    op.drop_index("campaign_label_rules_client_priority_idx", table_name="campaign_label_rules")
    op.drop_table("campaign_label_rules")

    op.drop_index("client_taxonomies_dimensions_gin", table_name="client_taxonomies")
    op.drop_index("client_taxonomies_client_version_idx", table_name="client_taxonomies")
    op.drop_table("client_taxonomies")
