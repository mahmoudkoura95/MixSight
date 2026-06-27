"""Startup route audit per §7.19.

Walks every registered `APIRoute` at app startup. For each route whose
signature accepts a `client_id` parameter, asserts `enforce_client_access`
is somewhere in the dependency chain; same for `organization_id` →
`enforce_organization_access`.

Routes that fail the audit fail app boot with a `TenancyAuditError` naming
the offending route and the missing dep. A single missed access check is
a tenancy breach — the audit makes missing one impossible to merge.

The audit cannot catch background jobs (no route signature) — those rely
on the integration-test pattern (§7.19 part 2, see `tests/conftest.py`).
"""

from __future__ import annotations

import inspect
from typing import Annotated, Any, get_args, get_origin, get_type_hints

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from pydantic import BaseModel

from mixsight.tenancy.access import enforce_client_access, enforce_organization_access


class TenancyAuditError(RuntimeError):
    """Raised when one or more routes fail the §7.19 tenancy audit."""


def _has_dependency(dependant: Dependant, target: Any) -> bool:
    """Recursively check if `target` callable is anywhere in the dep tree."""
    if dependant.call is target:
        return True
    return any(_has_dependency(sub, target) for sub in dependant.dependencies)


def _unwrap_annotated(annotation: Any) -> Any:
    """Strip `Annotated[T, ...]` down to T; pass other annotations through."""
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        if args:
            return args[0]
    return annotation


def _route_parameter_names(route: APIRoute) -> set[str]:
    """Names of every parameter (path, query, body) the endpoint accepts.

    Per §7.19: tenancy enforcement applies when `client_id` / `organization_id`
    appears in path, query, OR body. A Pydantic body model's field names are
    treated as parameter names — a route with `body: CreateSnapshotBody` where
    the body declares `client_id` is gated the same as `client_id: UUID`.

    `get_type_hints` resolves string annotations created by
    `from __future__ import annotations` back into real classes; without
    that, `inspect.isclass(...)` sees only the unresolved string.
    """
    sig = inspect.signature(route.endpoint)
    try:
        hints = get_type_hints(route.endpoint, include_extras=True)
    except Exception:
        hints = {}
    names: set[str] = set()
    for param_name in sig.parameters:
        names.add(param_name)
        annotation = hints.get(param_name, sig.parameters[param_name].annotation)
        annotation = _unwrap_annotated(annotation)
        if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            names.update(annotation.model_fields.keys())
    return names


def audit_routes(app: FastAPI) -> None:
    errors: list[str] = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        params = _route_parameter_names(route)
        method = next(iter(route.methods or ()), "?")

        if "client_id" in params and not _has_dependency(route.dependant, enforce_client_access):
            errors.append(
                f"Route {method} {route.path} takes a `client_id` parameter "
                f"but does not depend on `enforce_client_access`. "
                f"Add `Depends(enforce_client_access)` to the function signature."
            )

        if "organization_id" in params and not _has_dependency(
            route.dependant, enforce_organization_access
        ):
            errors.append(
                f"Route {method} {route.path} takes an `organization_id` parameter "
                f"but does not depend on `enforce_organization_access`. "
                f"Add `Depends(enforce_organization_access)` to the function signature."
            )

    if errors:
        raise TenancyAuditError("§7.19 tenancy audit failed:\n  - " + "\n  - ".join(errors))
