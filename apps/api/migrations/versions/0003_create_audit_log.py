"""create audit_log

Revision ID: 0003_create_audit_log
Revises: 0002_create_tenancy_schema
Create Date: 2026-06-22

§7.4 AuditLog: append-only mutation history. 7-year retention with
anonymization at customer deletion per §6.6 (cleanup + scrubbing logic
lands Phase 2+).

Neither `organization_id` nor `actor_user_id` is a foreign key. Both are
forensic identifiers we want to preserve even after the referenced rows
are hard-deleted (the audit trail outlives the entity it audits). FK on
organization_id would also fire-and-fail in the same transaction that
hard-deletes an Organization — the audit hook can't insert a row pointing
at a row the same transaction is about to remove.

Indexes per §7.4 entity-specific rules:
- `(organization_id, occurred_at)` for tenant-scoped time queries
- `(entity_type, entity_id)` for entity history lookups
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_create_audit_log"
down_revision: str | None = "0002_create_tenancy_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_type", sa.Text(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("before", postgresql.JSONB, nullable=True),
        sa.Column("after", postgresql.JSONB, nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("request_id", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
    )
    op.create_index(
        "audit_log_organization_occurred_idx",
        "audit_log",
        ["organization_id", "occurred_at"],
    )
    op.create_index(
        "audit_log_entity_idx",
        "audit_log",
        ["entity_type", "entity_id"],
    )


def downgrade() -> None:
    op.drop_index("audit_log_entity_idx", table_name="audit_log")
    op.drop_index("audit_log_organization_occurred_idx", table_name="audit_log")
    op.drop_table("audit_log")
