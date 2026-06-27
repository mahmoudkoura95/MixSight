"""Meta-tests for the §7.19 tenancy harness.

Verifies that `audit_routes` catches missing access-check dependencies on
routes that take `client_id` / `organization_id` parameters, and passes on
routes that have the deps wired correctly.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from mixsight.tenancy import (
    TenancyAuditError,
    audit_routes,
    enforce_client_access,
    enforce_organization_access,
)


# Module-level so `get_type_hints` can resolve string annotations from
# `from __future__ import annotations` against this module's namespace.
class _CreateSnapshotBody(BaseModel):
    client_id: UUID
    note: str


class _CreateSnapshotBodySimple(BaseModel):
    client_id: UUID


def test_audit_catches_missing_client_access_dep() -> None:
    app = FastAPI()

    @app.get("/clients/{client_id}/snapshots")
    async def list_snapshots(client_id: UUID) -> dict[str, str]:
        return {"client_id": str(client_id)}

    with pytest.raises(TenancyAuditError, match="enforce_client_access"):
        audit_routes(app)


def test_audit_passes_when_client_access_dep_present() -> None:
    app = FastAPI()

    @app.get("/clients/{client_id}/snapshots")
    async def list_snapshots(
        client_id: UUID,
        _: None = Depends(enforce_client_access),
    ) -> dict[str, str]:
        return {"client_id": str(client_id)}

    audit_routes(app)  # must not raise


def test_audit_catches_missing_organization_access_dep() -> None:
    app = FastAPI()

    @app.get("/organizations/{organization_id}/connectors")
    async def list_connectors(organization_id: UUID) -> dict[str, str]:
        return {"organization_id": str(organization_id)}

    with pytest.raises(TenancyAuditError, match="enforce_organization_access"):
        audit_routes(app)


def test_audit_passes_when_organization_access_dep_present() -> None:
    app = FastAPI()

    @app.get("/organizations/{organization_id}/connectors")
    async def list_connectors(
        organization_id: UUID,
        _: None = Depends(enforce_organization_access),
    ) -> dict[str, str]:
        return {"organization_id": str(organization_id)}

    audit_routes(app)  # must not raise


def test_audit_passes_on_route_without_tenant_params() -> None:
    """Sanity: routes without tenant identifiers are not gated."""
    app = FastAPI()

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    audit_routes(app)  # must not raise


def test_audit_collects_all_violations() -> None:
    """Both `client_id` and `organization_id` violations surface together."""
    app = FastAPI()

    @app.get("/clients/{client_id}")
    async def get_client(client_id: UUID) -> dict[str, str]:
        return {"client_id": str(client_id)}

    @app.get("/organizations/{organization_id}")
    async def get_org(organization_id: UUID) -> dict[str, str]:
        return {"organization_id": str(organization_id)}

    with pytest.raises(TenancyAuditError) as excinfo:
        audit_routes(app)
    msg = str(excinfo.value)
    assert "enforce_client_access" in msg
    assert "enforce_organization_access" in msg


def test_audit_catches_missing_dep_when_client_id_in_pydantic_body() -> None:
    """§7.19 covers path, query, OR body — Pydantic body-model fields too."""
    app = FastAPI()

    @app.post("/snapshots")
    async def create_snapshot(body: _CreateSnapshotBody) -> dict[str, str]:
        return {"client_id": str(body.client_id)}

    with pytest.raises(TenancyAuditError, match="enforce_client_access"):
        audit_routes(app)


def test_audit_passes_when_dep_present_for_pydantic_body() -> None:
    app = FastAPI()

    @app.post("/snapshots")
    async def create_snapshot(
        body: _CreateSnapshotBodySimple,
        _: None = Depends(enforce_client_access),
    ) -> dict[str, str]:
        return {"client_id": str(body.client_id)}

    audit_routes(app)  # must not raise
