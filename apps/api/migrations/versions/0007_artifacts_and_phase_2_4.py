"""create artifacts + provision Phase 2/4 tables empty

Revision ID: 0007_artifacts_futures
Revises: 0006_actuals_pacing
Create Date: 2026-06-25

Phase 1 artifacts: `DefenseKit`, `PromotionalEvent`, `ConnectorPull`.

Phase 2/4 tables provisioned empty per the locked decision ("all Phase 2/4
tables provisioned (empty) in Phase 1a — no schema retrofit later"):
`MacroSignal`, `ContributionFit`, `IncrementalityResult`, `ForecastRun`.

Per the audit-log skill, `ConnectorPull` and `ForecastRun` are append-only
and excluded from the §7.4 AuditLog SQLAlchemy event hook.

`ContributionFit.input_model_fit_id` (referenced by ForecastRun) and
`ForecastRun.input_plan_version` are stored without FK constraints — they
become real FKs in Phase 2/3 when the corresponding write paths land.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_artifacts_futures"
down_revision: str | None = "0006_actuals_pacing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- defense_kits --------------------------------------------------
    op.create_table(
        "defense_kits",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "snapshot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pacing_snapshots.id", name="defense_kits_snapshot_id_fk"),
            nullable=False,
        ),
        sa.Column("render_mode", sa.Text(), nullable=False),
        sa.Column("narrative_text", sa.Text(), nullable=True),
        sa.Column(
            "narrative_status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column(
            "included_suggestion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "reallocation_suggestions.id",
                name="defense_kits_included_suggestion_id_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column("generated_pdf_uri", sa.Text(), nullable=True),
        sa.Column(
            "am_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id",
                name="defense_kits_am_user_id_fk",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
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
    op.create_index("defense_kits_snapshot_id_idx", "defense_kits", ["snapshot_id"])

    # --- promotional_events --------------------------------------------
    op.create_table(
        "promotional_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="promotional_events_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="promotional_events_market_id_fk"),
            nullable=True,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("expected_impact_notes", sa.Text(), nullable=True),
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
        "promotional_events_client_idx",
        "promotional_events",
        ["client_id", "start_date"],
    )

    # --- connector_pulls -----------------------------------------------
    op.create_table(
        "connector_pulls",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="connector_pulls_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="connector_pulls_market_id_fk"),
            nullable=False,
        ),
        sa.Column("platform", sa.Text(), nullable=False),
        sa.Column("pull_window_start", sa.Date(), nullable=False),
        sa.Column("pull_window_end", sa.Date(), nullable=False),
        sa.Column("pull_type", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("rows_fetched", sa.BigInteger(), nullable=True),
        sa.Column("rows_upserted", sa.BigInteger(), nullable=True),
        sa.Column("rows_revised", sa.BigInteger(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "attempted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "connector_pulls_client_market_idx",
        "connector_pulls",
        ["client_id", "market_id", "attempted_at"],
    )

    # --- macro_signals (Phase 2 populated) -----------------------------
    op.create_table(
        "macro_signals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="macro_signals_market_id_fk"),
            nullable=False,
        ),
        sa.Column("signal_type", sa.Text(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(20, 6), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column(
            "captured_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "macro_signals_market_signal_date_idx",
        "macro_signals",
        ["market_id", "signal_type", "date"],
    )

    # --- contribution_fits (Phase 2) -----------------------------------
    op.create_table(
        "contribution_fits",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="contribution_fits_client_id_fk"),
            nullable=False,
        ),
        sa.Column("model_version", sa.Text(), nullable=False),
        sa.Column("engine", sa.Text(), nullable=False),
        sa.Column("fit_date", sa.Date(), nullable=False),
        sa.Column("training_window_start", sa.Date(), nullable=False),
        sa.Column("training_window_end", sa.Date(), nullable=False),
        sa.Column("parameters_uri", sa.Text(), nullable=True),
        sa.Column(
            "diagnostics",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "contribution_fits_client_fit_date_idx",
        "contribution_fits",
        ["client_id", "fit_date"],
    )

    # --- incrementality_results (Phase 2/3) ----------------------------
    op.create_table(
        "incrementality_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="incrementality_results_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "market_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("markets.id", name="incrementality_results_market_id_fk"),
            nullable=True,
        ),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("test_type", sa.Text(), nullable=False),
        sa.Column("test_start", sa.Date(), nullable=False),
        sa.Column("test_end", sa.Date(), nullable=False),
        sa.Column("lift_estimate", sa.Numeric(8, 4), nullable=True),
        sa.Column("lift_ci_low", sa.Numeric(8, 4), nullable=True),
        sa.Column("lift_ci_high", sa.Numeric(8, 4), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "incrementality_results_client_channel_idx",
        "incrementality_results",
        ["client_id", "channel"],
    )

    # --- forecast_runs (Phase 3) ---------------------------------------
    op.create_table(
        "forecast_runs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", name="forecast_runs_client_id_fk"),
            nullable=False,
        ),
        sa.Column(
            "run_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("run_type", sa.Text(), nullable=False),
        sa.Column("input_plan_version", sa.Integer(), nullable=True),
        sa.Column("input_model_fit_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("input_external_signals_uri", sa.Text(), nullable=True),
        sa.Column(
            "output_trajectory",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("output_summary", sa.Text(), nullable=True),
    )
    op.create_index(
        "forecast_runs_client_run_at_idx",
        "forecast_runs",
        ["client_id", "run_at"],
    )


def downgrade() -> None:
    op.drop_index("forecast_runs_client_run_at_idx", table_name="forecast_runs")
    op.drop_table("forecast_runs")

    op.drop_index(
        "incrementality_results_client_channel_idx",
        table_name="incrementality_results",
    )
    op.drop_table("incrementality_results")

    op.drop_index("contribution_fits_client_fit_date_idx", table_name="contribution_fits")
    op.drop_table("contribution_fits")

    op.drop_index("macro_signals_market_signal_date_idx", table_name="macro_signals")
    op.drop_table("macro_signals")

    op.drop_index("connector_pulls_client_market_idx", table_name="connector_pulls")
    op.drop_table("connector_pulls")

    op.drop_index("promotional_events_client_idx", table_name="promotional_events")
    op.drop_table("promotional_events")

    op.drop_index("defense_kits_snapshot_id_idx", table_name="defense_kits")
    op.drop_table("defense_kits")
