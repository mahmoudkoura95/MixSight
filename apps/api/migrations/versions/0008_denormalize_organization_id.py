"""denormalize organization_id for audit-log tenant scoping

Revision ID: 0008_denormalize_org_id
Revises: 0007_artifacts_futures
Create Date: 2026-06-26

Week 3 / Day 1 of Phase 1a. Closes the Week 2 /code-review HIGH carry-over:
AuditLog `organization_id` resolution returned NULL for 15+ entities because
the resolver in `mixsight.audit.hooks._resolve_organization_id` only reads
the direct `organization_id` attribute, and most §7.4 entities had none.

Approach mirrors Week 1's Market + UserClientAccess denormalization in
migration 0004: add nullable `organization_id` column → backfill via the
existing FK chain → flip to NOT NULL → add FK + index. Parents are denorm'd
before children so child backfills can JOIN through parent org_id.

Entities covered (per the carry-over list in CURRENT_PHASE.md):
  encrypted_secrets, market_configs, ad_account_mappings, client_taxonomies,
  campaign_label_rules, plans, plan_lines, actuals, pacing_snapshots,
  pacing_snapshot_lines, reconciliation_factors, reallocation_suggestions,
  recommendation_log, defense_kits, promotional_events, macro_signals,
  contribution_fits, incrementality_results.

EncryptedSecret has no inbound FK to an org; backfill traverses the
referencing tables (ConnectorAuth token refs + Client BYOK ref). In CI +
dev the table is empty so backfill is a no-op; for any future populated
deployment the SELECTs cover both reference paths. NOT NULL is enforced
after backfill — secrets MUST belong to an org from this point forward.

The audit hook resolver itself needs no code change — `getattr(target,
"organization_id", None)` already works once the column is present. Caller
code that inserts these entities must SET `organization_id` explicitly.
That discipline is enforced naturally by the NOT NULL constraint.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_denormalize_org_id"
down_revision: str | None = "0007_artifacts_futures"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# (table_name, backfill_sql_template) — parents listed before children so
# child backfills can JOIN through parents that already have org_id.
# `{t}` is substituted with the table name (lets the template stay terse).
#
# Each backfill SELECT picks the shortest tenant-resolution path the
# entity has. Where multiple paths exist (e.g. PlanLine could traverse
# via plan_id or market_id), we pick the one that matches §7.4 ownership
# semantics: PlanLine belongs to a Plan; Actuals/PacingSnapshot/etc.
# belong to a Client directly.
_BACKFILLS: list[tuple[str, str]] = [
    # via clients.organization_id
    (
        "client_taxonomies",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "campaign_label_rules",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "plans",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "actuals",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "pacing_snapshots",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "reconciliation_factors",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "recommendation_log",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "promotional_events",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "contribution_fits",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    (
        "incrementality_results",
        "UPDATE {t} SET organization_id = c.organization_id "
        "FROM clients c WHERE c.id = {t}.client_id",
    ),
    # via markets.organization_id (Week 1 denormalization)
    (
        "market_configs",
        "UPDATE {t} SET organization_id = m.organization_id "
        "FROM markets m WHERE m.id = {t}.market_id",
    ),
    (
        "ad_account_mappings",
        "UPDATE {t} SET organization_id = m.organization_id "
        "FROM markets m WHERE m.id = {t}.market_id",
    ),
    (
        "macro_signals",
        "UPDATE {t} SET organization_id = m.organization_id "
        "FROM markets m WHERE m.id = {t}.market_id",
    ),
    # Children of parents we just denorm'd above
    (
        "plan_lines",
        "UPDATE {t} SET organization_id = p.organization_id FROM plans p WHERE p.id = {t}.plan_id",
    ),
    (
        "pacing_snapshot_lines",
        "UPDATE {t} SET organization_id = s.organization_id "
        "FROM pacing_snapshots s WHERE s.id = {t}.snapshot_id",
    ),
    (
        "reallocation_suggestions",
        "UPDATE {t} SET organization_id = s.organization_id "
        "FROM pacing_snapshots s WHERE s.id = {t}.snapshot_id",
    ),
    (
        "defense_kits",
        "UPDATE {t} SET organization_id = s.organization_id "
        "FROM pacing_snapshots s WHERE s.id = {t}.snapshot_id",
    ),
]


# EncryptedSecret handled separately — two reference paths, neither a
# direct FK from the secret itself.
_ENCRYPTED_SECRET_BACKFILLS = [
    # Via ConnectorAuth (oauth + refresh token refs)
    "UPDATE encrypted_secrets SET organization_id = ca.organization_id "
    "FROM connector_auth ca "
    "WHERE encrypted_secrets.id IN (ca.oauth_token_ref, ca.refresh_token_ref) "
    "AND encrypted_secrets.organization_id IS NULL",
    # Via Client (BYOK key ref)
    "UPDATE encrypted_secrets SET organization_id = c.organization_id "
    "FROM clients c WHERE c.id IS NOT NULL "
    "AND encrypted_secrets.id = c.llm_byok_key_ref "
    "AND encrypted_secrets.organization_id IS NULL",
]


def _denormalize(table: str, backfill_sql: str) -> None:
    op.add_column(
        table,
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(backfill_sql.format(t=table))
    op.alter_column(table, "organization_id", nullable=False)
    op.create_foreign_key(
        f"{table}_organization_id_fk",
        table,
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_index(f"{table}_organization_id_idx", table, ["organization_id"])


def upgrade() -> None:
    # EncryptedSecret first — its backfill JOINs ConnectorAuth + Client,
    # both of which already have organization_id from earlier migrations,
    # so order doesn't conflict with the rest.
    op.add_column(
        "encrypted_secrets",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    for stmt in _ENCRYPTED_SECRET_BACKFILLS:
        op.execute(stmt)
    op.alter_column("encrypted_secrets", "organization_id", nullable=False)
    op.create_foreign_key(
        "encrypted_secrets_organization_id_fk",
        "encrypted_secrets",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_index(
        "encrypted_secrets_organization_id_idx",
        "encrypted_secrets",
        ["organization_id"],
    )

    # Everything else follows the standard `_denormalize` pattern. Ordered
    # so parents (plans, pacing_snapshots) are done before children
    # (plan_lines, pacing_snapshot_lines, etc.).
    for table, sql in _BACKFILLS:
        _denormalize(table, sql)


def downgrade() -> None:
    # Reverse order so children come down before parents.
    for table, _ in reversed(_BACKFILLS):
        op.drop_index(f"{table}_organization_id_idx", table_name=table)
        op.drop_constraint(f"{table}_organization_id_fk", table, type_="foreignkey")
        op.drop_column(table, "organization_id")

    op.drop_index("encrypted_secrets_organization_id_idx", table_name="encrypted_secrets")
    op.drop_constraint(
        "encrypted_secrets_organization_id_fk",
        "encrypted_secrets",
        type_="foreignkey",
    )
    op.drop_column("encrypted_secrets", "organization_id")
