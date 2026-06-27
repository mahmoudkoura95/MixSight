---
name: audit-log
description: Use this skill whenever creating, modifying, or deleting an entity in the MixSight project, when implementing SQLAlchemy event hooks, when configuring audit retention or anonymization, or when surfacing audit history in the admin UI. Triggers include "audit log," "mutation," "track changes," "before/after," "compliance," "SOC 2," "GDPR," "deletion." Encodes the SCOPE.md §7.4 AuditLog entity pattern with SQLAlchemy event hooks that capture every mutation automatically. Use this skill BEFORE writing any code that mutates database state — every mutation writes to AuditLog, no exceptions, no workarounds.
---

# Audit log skill

Per §7.4 and §6.6, every mutation writes to `AuditLog`. 7-year retention. Anonymization at customer deletion. This is foundational for SOC 2 (Phase 2), GDPR right-to-be-forgotten, and recommendation calibration in Phase 4.

## The mechanism

A SQLAlchemy event hook in `apps/api/audit/hooks.py` listens on `before_insert`, `before_update`, `before_delete` for every model inheriting from `Base`. The hook is registered at app startup and is not optional.

```python
# apps/api/audit/hooks.py
from sqlalchemy import event
from sqlalchemy.inspection import inspect
from app.models.base import Base
from app.models.audit_log import AuditLog
from app.audit.context import current_actor, current_request_id


@event.listens_for(Base, "after_insert", propagate=True)
def _on_insert(mapper, connection, target):
    if isinstance(target, AuditLog):
        return  # No recursion
    if _skip(target):
        return
    connection.execute(AuditLog.__table__.insert().values(
        organization_id=_resolve_org_id(target),
        actor_user_id=current_actor(),
        entity_type=target.__tablename__,
        entity_id=target.id,
        action="created",
        before=None,
        after=_to_jsonb(target),
        request_id=current_request_id(),
    ))


@event.listens_for(Base, "after_update", propagate=True)
def _on_update(mapper, connection, target):
    if isinstance(target, AuditLog):
        return
    if _skip(target):
        return
    before = _resolve_before(target)
    connection.execute(AuditLog.__table__.insert().values(
        organization_id=_resolve_org_id(target),
        actor_user_id=current_actor(),
        entity_type=target.__tablename__,
        entity_id=target.id,
        action="updated",
        before=before,
        after=_to_jsonb(target),
        request_id=current_request_id(),
    ))


@event.listens_for(Base, "after_delete", propagate=True)
def _on_delete(mapper, connection, target):
    # Hard deletes only — soft delete fires as an update with `deleted_at` set
    if isinstance(target, AuditLog):
        return
    if _skip(target):
        return
    connection.execute(AuditLog.__table__.insert().values(
        organization_id=_resolve_org_id(target),
        actor_user_id=current_actor(),
        entity_type=target.__tablename__,
        entity_id=target.id,
        action="deleted",
        before=_to_jsonb(target),
        after=None,
        request_id=current_request_id(),
    ))
```

The actor and request_id come from a contextvars-based context set by FastAPI middleware on every request. For background jobs, the job runner sets the context explicitly.

## What gets skipped

`_skip(target)` returns `True` for:
- `AuditLog` itself (no recursion).
- `ConnectorAuthEvent` — own audit trail.
- `ConnectorPull` — append-only by design.
- `RecommendationLog` — append-only by design.
- `ForecastRun` — append-only by design.

Everything else is in scope.

## Fields per AuditLog row

Per §7.4:

| Field | Notes |
|---|---|
| `id` | UUID v4 |
| `organization_id` | resolved from target |
| `actor_user_id` | from request context; nullable for system events |
| `entity_type` | `target.__tablename__` |
| `entity_id` | UUID of the affected entity |
| `action` | `created` / `updated` / `deleted` / `restored` |
| `before` | JSONB, nullable on create |
| `after` | JSONB, nullable on delete |
| `occurred_at` | server default `now()` |
| `request_id` | from distributed trace context |
| `metadata` | JSONB extensibility for action-specific context |

`restored` is the action for un-soft-delete (setting `deleted_at` back to NULL).

## Bypass detection

A few patterns can bypass the ORM event hook:
- Raw SQL via `connection.execute("UPDATE ...")` outside Alembic.
- `Session.bulk_update_mappings`, `bulk_save_objects`, `bulk_insert_mappings`.
- Direct DBAPI cursor usage.
- Cascade deletes (handled — the hook fires for each cascaded row).

If you must bypass for performance, write the AuditLog row(s) explicitly in the same transaction. The bypass needs a code comment explaining why ("performance: bulk insert of N rows for catch-up backfill") and a corresponding entry in `DECISIONS.md`.

## Retention and anonymization (§6.6)

- **7-year retention.** Cleanup job in Phase 2a+: delete `AuditLog` rows with `occurred_at < now() - interval '7 years'`.
- **Anonymization at customer deletion.** When a customer is hard-deleted (30 days after cancellation), all `AuditLog` rows referencing their `organization_id` have `actor_user_id` replaced with a deterministic hash, and JSONB before/after fields scrubbed of identifying data.

```python
async def anonymize_org_audit_logs(org_id: UUID, session: AsyncSession):
    hash_salt = settings.ANONYMIZATION_SALT
    rows = await session.execute(
        update(AuditLog)
        .where(AuditLog.organization_id == org_id)
        .values(
            actor_user_id=None,
            before=func.jsonb_strip_keys(AuditLog.before, IDENTIFIABLE_KEYS),
            after=func.jsonb_strip_keys(AuditLog.after, IDENTIFIABLE_KEYS),
            metadata=func.jsonb_set(AuditLog.metadata, "{anonymized}", "true"),
        )
    )
```

`IDENTIFIABLE_KEYS` includes: `email`, `name`, `address`, billing details, IP addresses, anything PII.

## Audit log export (Phase 1c admin UI)

Per §7.4, admins can export the audit log for their organization. UI at `/settings/audit-log`. CSV bundle download. Use:

```python
@router.get("/organizations/{organization_id}/audit-log/export")
async def export_audit_log(
    organization_id: UUID,
    _: None = Depends(enforce_organization_access),
    __: None = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    # Stream CSV of AuditLog rows for org, filtered by date range
    ...
```

## Workflow

1. **You are mutating data.** The hook fires automatically. You don't need to write AuditLog rows by hand.
2. **You are doing a bulk operation.** The hook may not fire for the bulk path. Write the AuditLog rows explicitly in the same transaction.
3. **You are anonymizing a deleted customer.** Run `anonymize_org_audit_logs` as part of the deletion job.
4. **You are wondering whether to skip the hook.** Don't. The hook overhead is small; the audit hole is permanent.

## Testing

`tests/audit/test_coverage.py` mutates one of each entity type and asserts an AuditLog row exists with the right `entity_type`, `entity_id`, `action`, `before`, `after`. Run after any schema change.

## Common mistakes

1. Treating audit log as logging. It's not — it's persistence. Logs can be lost; audit log can't.
2. Skipping the hook "for now." There is no "for now" — the hole stays open forever.
3. Logging PII in `before` / `after`. Anonymization scrubs it but only after deletion; in steady state, PII lives in audit log for 7 years. That's OK because audit log is access-controlled, but be conscious about what fields you persist.
4. Forgetting that soft delete is an update, not a delete. The hook fires as `updated` with `deleted_at` set. `restored` is the un-soft-delete action.
5. Background jobs that don't set the actor context. The job runner does this — but if you're writing custom job-runner code, set the context explicitly.
