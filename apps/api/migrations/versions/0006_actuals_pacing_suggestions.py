"""create actuals + pacing + suggestions tables

Revision ID: 0006_actuals_pacing
Revises: 0005_taxonomy_plans
Create Date: 2026-06-25

§7.4 + §7.14 + §7.10. The Actuals UNIQUE constraint on
(client_id, market_id, channel, campaign_external_id, date, source) is the
§7.14 idempotency contract: every connector pull is an upsert on this key.

§6.2 numeric conventions: money = numeric(18, 4), percentages = numeric(8, 4),
FX = numeric(20, 10), confidence scores = numeric(8, 4).

RecommendationLog ships from day one of Phase 1a per the locked decision —
every ReallocationSuggestion writes a row at creation, so the Phase 4
calibration UI has data when it launches (§7.10 step 11).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_actuals_pacing"
down_revision: str | None = "0005_taxonomy_plans"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- actuals -------------------------------------------------------
    op.create_table(
        "actuals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="actuals_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="actuals_market_id_fk"),
            nullable=False,
        ),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("campaign_external_id", sa.Text(), nullable=False),
        sa.Column("campaign_label", sa.Text(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("spend_local", sa.Numeric(18, 4), nullable=False),
        sa.Column("spend_reporting", sa.Numeric(18, 4), nullable=True),
        sa.Column("impressions", sa.BigInteger(), nullable=True),
        sa.Column("clicks", sa.BigInteger(), nullable=True),
        sa.Column("conversions", sa.Numeric(18, 4), nullable=True),
        sa.Column("conversions_value", sa.Numeric(18, 4), nullable=True),
        sa.Column(
            "conversions_alt_attributions",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "labels",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("pull_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pull_window_start", sa.Date(), nullable=True),
        sa.Column("pull_window_end", sa.Date(), nullable=True),
        sa.Column("fx_rate_used", sa.Numeric(20, 10), nullable=True),
        sa.Column(
            "archived_at_source",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
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
        sa.UniqueConstraint(
            "client_id",
            "market_id",
            "channel",
            "campaign_external_id",
            "date",
            "source",
            name="actuals_unique_pull",
        ),
    )
    op.create_index(
        "actuals_client_market_date_idx",
        "actuals",
        ["client_id", "market_id", "date"],
    )
    op.create_index("actuals_labels_gin", "actuals", ["labels"], postgresql_using="gin")

    # --- pacing_snapshots ----------------------------------------------
    op.create_table(
        "pacing_snapshots",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="pacing_snapshots_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="pacing_snapshots_market_id_fk"),
            nullable=False,
        ),
        sa.Column("week_ending", sa.Date(), nullable=False),
        sa.Column("allocation_mode", sa.Text(), nullable=False),
        sa.Column("fx_rate_used", sa.Numeric(20, 10), nullable=True),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "is_partial_week",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_index(
        "pacing_snapshots_client_week_idx",
        "pacing_snapshots",
        ["client_id", "week_ending"],
    )

    # --- pacing_snapshot_lines -----------------------------------------
    op.create_table(
        "pacing_snapshot_lines",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "snapshot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "pacing_snapshots.id",
                name="pacing_snapshot_lines_snapshot_id_fk",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "plan_line_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plan_lines.id", name="pacing_snapshot_lines_plan_line_id_fk"),
            nullable=False,
        ),
        sa.Column("actual_spend_to_date", sa.Numeric(18, 4), nullable=True),
        sa.Column("planned_spend_to_date", sa.Numeric(18, 4), nullable=True),
        sa.Column("spend_drift_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("actual_kpi_to_date", sa.Numeric(18, 4), nullable=True),
        sa.Column("planned_kpi_to_date", sa.Numeric(18, 4), nullable=True),
        sa.Column("kpi_drift_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("drift_explanation_text", sa.Text(), nullable=True),
        sa.Column(
            "drift_explanation_status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column(
            "evidence_payload",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("objective_type", sa.Text(), nullable=False),
        sa.Column(
            "labels",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.create_index(
        "pacing_snapshot_lines_snapshot_id_idx",
        "pacing_snapshot_lines",
        ["snapshot_id"],
    )

    # --- reconciliation_factors ----------------------------------------
    op.create_table(
        "reconciliation_factors",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="reconciliation_factors_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="reconciliation_factors_market_id_fk"),
            nullable=False,
        ),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("week_ending", sa.Date(), nullable=False),
        sa.Column("ga4_to_platform_ratio", sa.Numeric(18, 6), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "client_id",
            "market_id",
            "channel",
            "week_ending",
            name="reconciliation_factors_unique_week",
        ),
    )

    # --- reallocation_suggestions --------------------------------------
    op.create_table(
        "reallocation_suggestions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "snapshot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "pacing_snapshots.id",
                name="reallocation_suggestions_snapshot_id_fk",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "donor_line_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plan_lines.id", name="reallocation_suggestions_donor_line_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "receiver_line_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plan_lines.id", name="reallocation_suggestions_receiver_line_id_fk"),
            nullable=False,
        ),
        sa.Column("proposed_amount_local", sa.Numeric(18, 4), nullable=False),
        sa.Column("proposed_amount_reporting", sa.Numeric(18, 4), nullable=True),
        sa.Column("projected_delta", sa.Numeric(18, 4), nullable=True),
        sa.Column("projected_delta_units", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(8, 4), nullable=True),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column(
            "taxonomy_pooling_compliance",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("rationale_text", sa.Text(), nullable=True),
        sa.Column(
            "included_in_defense_kit",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("am_justification_text", sa.Text(), nullable=True),
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
        "reallocation_suggestions_snapshot_idx",
        "reallocation_suggestions",
        ["snapshot_id"],
    )

    # --- recommendation_log --------------------------------------------
    op.create_table(
        "recommendation_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="recommendation_log_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "suggestion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "reallocation_suggestions.id",
                name="recommendation_log_suggestion_id_fk",
            ),
            nullable=False,
        ),
        sa.Column(
            "recommended_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("predicted_delta", sa.Numeric(18, 4), nullable=True),
        sa.Column("predicted_confidence", sa.Numeric(8, 4), nullable=True),
        sa.Column("recommendation_source", sa.Text(), nullable=False),
        sa.Column(
            "implemented",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("implemented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("implemented_amount", sa.Numeric(18, 4), nullable=True),
        sa.Column("observed_outcome", sa.Numeric(18, 4), nullable=True),
        sa.Column("outcome_window_end", sa.Date(), nullable=True),
        sa.Column("calibration_score", sa.Numeric(8, 4), nullable=True),
    )
    op.create_index(
        "recommendation_log_client_source_idx",
        "recommendation_log",
        ["client_id", "recommendation_source", "recommended_at"],
    )


def downgrade() -> None:
    op.drop_index("recommendation_log_client_source_idx", table_name="recommendation_log")
    op.drop_table("recommendation_log")

    op.drop_index("reallocation_suggestions_snapshot_idx", table_name="reallocation_suggestions")
    op.drop_table("reallocation_suggestions")

    op.drop_table("reconciliation_factors")

    op.drop_index("pacing_snapshot_lines_snapshot_id_idx", table_name="pacing_snapshot_lines")
    op.drop_table("pacing_snapshot_lines")

    op.drop_index("pacing_snapshots_client_week_idx", table_name="pacing_snapshots")
    op.drop_table("pacing_snapshots")

    op.drop_index("actuals_labels_gin", table_name="actuals")
    op.drop_index("actuals_client_market_date_idx", table_name="actuals")
    op.drop_table("actuals")
