"""Coverage tests for the §7.4 AuditLog SQLAlchemy event hook.

Mutates one entity (Organization) through the ORM and asserts an AuditLog
row exists with the right `entity_type`, `entity_id`, `action`, `before`,
`after`. The same contract applies to every tracked entity — adding a new
model means adding it to `register_audit_hooks` in `main.py` + asserting
coverage here.

Each test runs inside a SAVEPOINT via the `db_session` fixture in
`conftest.py`; nothing persists across tests.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mixsight.models import AuditLog, Organization


@pytest.mark.asyncio
async def test_audit_log_organization_create(db_session: AsyncSession) -> None:
    org = Organization(name="Audit hook create test")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    stmt = select(AuditLog).where(AuditLog.entity_id == org.id).order_by(AuditLog.occurred_at)
    rows = list((await db_session.execute(stmt)).scalars().all())

    assert len(rows) == 1
    audit = rows[0]
    assert audit.entity_type == "organizations"
    assert audit.action == "created"
    assert audit.before is None
    assert audit.after is not None
    assert audit.after["name"] == "Audit hook create test"
    # Organization audits itself: organization_id == its own id
    assert audit.organization_id == org.id


@pytest.mark.asyncio
async def test_audit_log_organization_update(db_session: AsyncSession) -> None:
    org = Organization(name="Audit hook update test — before")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    org.name = "Audit hook update test — after"
    await db_session.commit()

    stmt = (
        select(AuditLog)
        .where(AuditLog.entity_id == org.id, AuditLog.action == "updated")
        .order_by(AuditLog.occurred_at)
    )
    rows = list((await db_session.execute(stmt)).scalars().all())

    assert len(rows) == 1
    audit = rows[0]
    assert audit.entity_type == "organizations"
    assert audit.before is not None
    assert audit.after is not None
    assert audit.before["name"] == "Audit hook update test — before"
    assert audit.after["name"] == "Audit hook update test — after"


@pytest.mark.asyncio
async def test_audit_log_organization_soft_delete_is_update(
    db_session: AsyncSession,
) -> None:
    """Soft delete (setting `deleted_at`) emits action=updated per the skill."""
    org = Organization(name="Audit hook soft-delete test")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    org.deleted_at = datetime.now(UTC)
    await db_session.commit()

    stmt = (
        select(AuditLog)
        .where(AuditLog.entity_id == org.id, AuditLog.action == "updated")
        .order_by(AuditLog.occurred_at)
    )
    rows = list((await db_session.execute(stmt)).scalars().all())

    assert len(rows) == 1
    audit = rows[0]
    assert audit.after is not None
    assert audit.after.get("deleted_at") is not None


@pytest.mark.asyncio
async def test_audit_log_organization_restore(db_session: AsyncSession) -> None:
    """Clearing `deleted_at` back to NULL emits action='restored', not 'updated'."""
    org = Organization(name="Audit hook restore test")
    org.deleted_at = datetime.now(UTC)
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    org.deleted_at = None
    await db_session.commit()

    stmt = (
        select(AuditLog)
        .where(AuditLog.entity_id == org.id, AuditLog.action == "restored")
        .order_by(AuditLog.occurred_at)
    )
    rows = list((await db_session.execute(stmt)).scalars().all())

    assert len(rows) == 1
    audit = rows[0]
    assert audit.entity_type == "organizations"
    assert audit.before is not None
    assert audit.after is not None
    assert audit.before["deleted_at"] is not None
    assert audit.after["deleted_at"] is None


@pytest.mark.asyncio
async def test_audit_log_organization_hard_delete(db_session: AsyncSession) -> None:
    org = Organization(name="Audit hook hard-delete test")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    org_id = org.id

    await db_session.delete(org)
    await db_session.commit()

    stmt = select(AuditLog).where(AuditLog.entity_id == org_id, AuditLog.action == "deleted")
    rows = list((await db_session.execute(stmt)).scalars().all())

    assert len(rows) == 1
    audit = rows[0]
    assert audit.entity_type == "organizations"
    assert audit.before is not None
    assert audit.before["name"] == "Audit hook hard-delete test"
    assert audit.after is None
