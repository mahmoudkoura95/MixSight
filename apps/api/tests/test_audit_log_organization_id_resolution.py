"""Coverage tests for the Week 3 / migration 0008 org_id denormalization.

The Week 2 /code-review HIGH carry-over was that `AuditLog.organization_id`
returned NULL for 15+ §7.4 entities. Week 3 Day 1 denormalized
`organization_id` onto all the affected tables; the resolver in
`mixsight.audit.hooks._resolve_organization_id` now reads one attribute
instead of walking FK chains.

Two tests cover the contract:

1. **Static introspection** — every mutable table in `SQLModel.metadata`
   carries an `organization_id` column unless explicitly exempted.
   This is the load-bearing test: a future engineer adding a new entity
   without the denormalization will fail this test loud, forcing the
   decision at code-review time rather than after silent NULL audits
   ship.

2. **Integration** — creating a Plan under an Organization emits an
   AuditLog row whose `organization_id` matches the Plan's org. Proves
   the resolver→column→audit-row wiring end-to-end. Plan is the
   representative case for the via-client traversal pattern that
   covers most §7.4 entities.

EncryptedSecret-specific coverage isn't separately needed: the static
test catches column presence, and the resolver pulls the same attribute
regardless of how the entity got its org_id.
"""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import mixsight.models  # noqa: F401 — populate SQLModel.metadata
from mixsight.models import AuditLog, Client, Organization, Plan
from mixsight.models.base import SQLModel

# Tables that legitimately do NOT carry a denormalized `organization_id`:
#  - audit_log: column is nullable; system events legitimately have no actor org.
#  - organizations: resolved via its own id by `_resolve_organization_id`.
#  - connector_pulls / forecast_runs: append-only entities excluded from the
#    audit-log hook per the audit-log skill — no denormalization required for
#    audit tenant scoping. (Could still benefit from org_id for query
#    convenience; deferred until a query needs it.)
_NO_ORG_ID_COLUMN: frozenset[str] = frozenset(
    {
        "audit_log",
        "organizations",
        "connector_pulls",
        "forecast_runs",
    }
)


def test_every_mutable_table_carries_organization_id() -> None:
    missing = [
        name
        for name, table in SQLModel.metadata.tables.items()
        if name not in _NO_ORG_ID_COLUMN and "organization_id" not in table.columns
    ]
    assert not missing, (
        "Tables missing the denormalized `organization_id` column required by "
        "the §7.4 AuditLog hook for tenant scoping: "
        f"{sorted(missing)}. Add it via an Alembic migration following the "
        "0008 pattern, or add the table to `_NO_ORG_ID_COLUMN` with a "
        "documented reason."
    )


@pytest.mark.asyncio
async def test_plan_audit_row_carries_denormalized_organization_id(
    db_session: AsyncSession,
) -> None:
    org = Organization(name="Audit hook org-id integration test")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    client = Client(organization_id=org.id, name="Audit hook test client")
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)

    plan = Plan(
        organization_id=org.id,
        client_id=client.id,
        source_method="csv_upload",
        period_start=date(2026, 7, 1),
        period_end=date(2026, 7, 31),
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)

    audit = (
        await db_session.execute(
            select(AuditLog).where(
                AuditLog.entity_id == plan.id,
                AuditLog.action == "created",
            )
        )
    ).scalar_one()
    assert audit.organization_id == org.id
    assert audit.entity_type == "plans"
