"""SQLAlchemy event hooks that write to AuditLog on every mutation.

Per §7.4: every create / update / delete on a tracked entity emits an
`AuditLog` row in the same transaction. Hook attaches to mapper-level
`after_insert`, `after_update`, `after_delete` events for each model
listed in `register_audit_hooks`.

Append-only entities (per the audit-log skill: `AuditLog`,
`ConnectorAuthEvent`, `ConnectorPull`, `RecommendationLog`, `ForecastRun`)
are excluded — they have their own audit semantics.

Bypass paths (raw SQL outside Alembic, `bulk_*` mappings, direct DBAPI
cursors) do not trigger this hook. If a bulk path is genuinely needed,
emit the AuditLog rows explicitly in the same transaction + document the
deviation in `DECISIONS.md` per the audit-log skill.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import event, insert
from sqlalchemy.engine import Connection
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Mapper

from mixsight.audit.context import get_actor_user_id, get_request_id
from mixsight.models.audit_log import AuditLog

# SQLModel exposes `__table__` at runtime via its metaclass; mypy doesn't see it.
_AUDIT_TABLE = AuditLog.__table__  # type: ignore[attr-defined]


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict | list):
        return value  # JSONB roundtrip handles nested
    return str(value)


def _serialize(target: Any) -> dict[str, Any]:
    """Dump a SQLModel instance to a JSON-safe dict (full snapshot)."""
    raw = target.model_dump(mode="json")
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def _change_diff(target: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return `(before, after)` dicts of fields that changed on this flush."""
    inspector = inspect(target)
    before: dict[str, Any] = {}
    after: dict[str, Any] = {}
    for attr in inspector.attrs:
        history = attr.history
        if not history.has_changes():
            continue
        old = history.deleted[0] if history.deleted else None
        new = history.added[0] if history.added else None
        before[attr.key] = _json_safe(old)
        after[attr.key] = _json_safe(new)
    return before, after


def _resolve_organization_id(target: Any) -> UUID | None:
    """Resolve which Organization owns this row.

    Every §7.4 mutable entity now has a denormalized `organization_id`
    column (Week 1 did Market + UserClientAccess; Week 3 / migration 0008
    did the remaining 18 — see CURRENT_PHASE.md Week 2 → 3 carry-over).
    The resolver therefore reads one attribute; FK chains are not walked
    here. Callers that insert these entities must SET `organization_id`
    explicitly — the NOT NULL constraint enforces that discipline at the
    DB layer.
    """
    if type(target).__name__ == "Organization":
        return target.id  # type: ignore[no-any-return]
    return getattr(target, "organization_id", None)


def _on_insert(_mapper: Mapper[Any], connection: Connection, target: Any) -> None:
    if isinstance(target, AuditLog):
        return
    connection.execute(
        insert(_AUDIT_TABLE).values(
            organization_id=_resolve_organization_id(target),
            actor_user_id=get_actor_user_id(),
            entity_type=target.__tablename__,
            entity_id=target.id,
            action="created",
            before=None,
            after=_serialize(target),
            request_id=get_request_id(),
        )
    )


def _on_update(_mapper: Mapper[Any], connection: Connection, target: Any) -> None:
    if isinstance(target, AuditLog):
        return
    before, after = _change_diff(target)
    action = "updated"
    # Restore = deleted_at transitioning from set → null.
    if (
        "deleted_at" in after
        and after["deleted_at"] is None
        and before.get("deleted_at") is not None
    ):
        action = "restored"
    connection.execute(
        insert(_AUDIT_TABLE).values(
            organization_id=_resolve_organization_id(target),
            actor_user_id=get_actor_user_id(),
            entity_type=target.__tablename__,
            entity_id=target.id,
            action=action,
            before=before,
            after=after,
            request_id=get_request_id(),
        )
    )


def _on_delete(_mapper: Mapper[Any], connection: Connection, target: Any) -> None:
    if isinstance(target, AuditLog):
        return
    connection.execute(
        insert(_AUDIT_TABLE).values(
            organization_id=_resolve_organization_id(target),
            actor_user_id=get_actor_user_id(),
            entity_type=target.__tablename__,
            entity_id=target.id,
            action="deleted",
            before=_serialize(target),
            after=None,
            request_id=get_request_id(),
        )
    )


def register_audit_hooks(models: list[type[Any]]) -> None:
    """Attach the hook to each model. Idempotent."""
    for model in models:
        if model is AuditLog:
            continue
        if not event.contains(model, "after_insert", _on_insert):
            event.listen(model, "after_insert", _on_insert)
        if not event.contains(model, "after_update", _on_update):
            event.listen(model, "after_update", _on_update)
        if not event.contains(model, "after_delete", _on_delete):
            event.listen(model, "after_delete", _on_delete)
