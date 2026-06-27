"""add clerk_last_event_at for Clerk-clock-only stale-event guard

Revision ID: 0009_clerk_last_event_at
Revises: 0008_denormalize_org_id
Create Date: 2026-06-26

Week 3 / Day 2 of Phase 1a. Closes the Week 2 /code-review HIGH carry-over
about stale-event clock-skew.

The Week 2 implementation compared Clerk-clock event timestamps to
server-clock entity `updated_at` values inside `is_stale_event`. Any drift
between the two clocks (NTP slop, server timezone wrong, queued webhook
deliveries arriving in a burst) could mark a legitimate close-together
event as stale and silently drop it.

Fix: record the Clerk-clock timestamp from the most recently-applied event
in a new column, then compare Clerk-clock to Clerk-clock. New columns are
nullable so existing rows pre-migration accept their first event
unconditionally; once set, subsequent events compare against the stored
Clerk timestamp.

Only Organization and User receive the column for now — those are the
entities with webhook-driven mutations in Phase 1a. Future webhook-managed
entities (e.g., UserClientAccess if Clerk grows per-resource grants) will
add their own column following this pattern.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_clerk_last_event_at"
down_revision: str | None = "0008_denormalize_org_id"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("clerk_last_event_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("clerk_last_event_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "clerk_last_event_at")
    op.drop_column("organizations", "clerk_last_event_at")
