"""Actor + request-id context for AuditLog hooks.

Set by FastAPI middleware on every request (so the hook reads the right
values when a mutation flushes); set explicitly by background-job runners.
"""

from __future__ import annotations

import contextvars
from uuid import UUID

_actor_user_id_var: contextvars.ContextVar[UUID | None] = contextvars.ContextVar(
    "mixsight_actor_user_id", default=None
)
_request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "mixsight_request_id", default=None
)


def set_actor_user_id(user_id: UUID | None) -> None:
    _actor_user_id_var.set(user_id)


def get_actor_user_id() -> UUID | None:
    return _actor_user_id_var.get()


def set_request_id(request_id: str | None) -> None:
    _request_id_var.set(request_id)


def get_request_id() -> str | None:
    return _request_id_var.get()
