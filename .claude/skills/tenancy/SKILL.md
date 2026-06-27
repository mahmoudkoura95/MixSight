---
name: tenancy
description: Use this skill whenever creating a new FastAPI route, background job, or test that touches client_id or organization_id in the MixSight project. Triggers include "new endpoint," "new route," "FastAPI router," "background job," "authenticated test," "tenancy," or any work that returns or mutates tenant-scoped data. Implements the SCOPE.md §7.19 tenancy harness: every endpoint with client_id must call enforce_client_access; every authenticated test must have the cross-tenant case via @pytest.mark.tenancy_isolated. A single missed access check is a tenancy breach — the harness exists to make missing one impossible to merge. Use this skill BEFORE writing any new endpoint.
---

# Tenancy skill

Multi-tenancy is enforced at the application layer (FastAPI dependency injection), not Postgres RLS. That choice (§3, locked) means a single missed `enforce_client_access` call is a tenancy breach. The §7.19 harness exists to make missing one impossible.

## The pattern

Every endpoint with `client_id` looks like this:

```python
from fastapi import APIRouter, Depends
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.deps import get_db, current_user
from app.tenancy import enforce_client_access
from app.models import User, PacingSnapshot

router = APIRouter()

@router.get("/clients/{client_id}/snapshots/{snapshot_id}")
async def get_snapshot(
    client_id: UUID,
    snapshot_id: UUID,
    _: None = Depends(enforce_client_access),  # MANDATORY
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
) -> PacingSnapshotResponse:
    # Safe to query — tenancy verified
    ...
```

For organization-level endpoints, use `enforce_organization_access`:

```python
@router.get("/organizations/{organization_id}/connectors")
async def list_connectors(
    organization_id: UUID,
    _: None = Depends(enforce_organization_access),  # MANDATORY
    ...
):
    ...
```

## Role-aware enforcement

Per §6.3 and §7.19, two roles exist:

- `admin` — full access to organization settings, billing, all clients in org, connector management, taxonomy, team management. Can perform reauth.
- `account_manager` — access to assigned clients only. Can edit plans and taxonomy for assigned clients. Can flag connector reauth needed (visible in connector health surface) but **cannot perform reauth**.

For endpoints that require admin role specifically:

```python
@router.post("/organizations/{organization_id}/connectors/{platform}/reauth")
async def reauth_connector(
    organization_id: UUID,
    platform: str,
    _: None = Depends(enforce_organization_access),
    __: None = Depends(require_role("admin")),  # Admin-only operation
    ...
):
    ...
```

## The harness — Part 1: startup decorator audit

`apps/api/tenancy/audit_routes.py` runs at app startup and introspects every registered route. For each route:

- If `client_id` is in path, query, or body → assert `enforce_client_access` is in the dependency chain.
- If `organization_id` is in path, query, or body → assert `enforce_organization_access` is in the dependency chain.
- If both → both are required.

Routes that fail the audit fail app startup with a clear error: "Route `GET /clients/{client_id}/snapshots/{snapshot_id}` takes a `client_id` parameter but does not depend on `enforce_client_access`. Add `Depends(enforce_client_access)` to the function signature."

## The harness — Part 2: integration test pattern

Every authenticated endpoint test is decorated with `@pytest.mark.tenancy_isolated` and includes a cross-tenant case:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.tenancy_isolated
@pytest.mark.asyncio
async def test_get_snapshot(
    client: AsyncClient,
    user_a_in_org_1,
    user_b_in_org_2,
    snapshot_in_org_1,
):
    # Happy path: user_a can read their own org's snapshot
    response = await client.get(
        f"/clients/{snapshot_in_org_1.client_id}/snapshots/{snapshot_in_org_1.id}",
        headers={"Authorization": f"Bearer {user_a_in_org_1.token}"},
    )
    assert response.status_code == 200

    # Cross-tenant case: user_b cannot
    response = await client.get(
        f"/clients/{snapshot_in_org_1.client_id}/snapshots/{snapshot_in_org_1.id}",
        headers={"Authorization": f"Bearer {user_b_in_org_2.token}"},
    )
    assert response.status_code in (403, 404)  # 404 if we hide existence
```

`apps/api/tenancy/audit_tests.py` scans test files for authenticated-endpoint tests and verifies each has the marker. Missing the marker fails the test run.

## Background jobs

Background jobs don't have a `client_id` in a path, but they have **implicit tenancy** from `user_id` or `organization_id`. Same enforcement rule applies:

```python
async def regenerate_drift_explanation(snapshot_id: UUID, triggered_by_user_id: UUID, db: AsyncSession):
    user = await db.get(User, triggered_by_user_id)
    snapshot = await db.get(PacingSnapshot, snapshot_id)
    # Same enforcement as a route would do
    enforce_client_access_for_user(user, snapshot.client_id)
    ...
```

The startup audit can't catch background jobs (no route signature) — these are caught by the integration test pattern. Every background job has a test that mutates a fixture resource and asserts a cross-tenant trigger fails.

## Clerk role sync (§7.19)

Clerk is the authentication source of truth; our DB is the authorization source of truth.

- Custom organization roles `admin` and `account_manager` configured in Clerk dashboard (override Clerk's default `org:admin` / `org:member`).
- Webhook subscriptions on `organizationMembership.created`, `.updated`, `.deleted` upsert to our `User` and `UserClientAccess` tables.
- JWT carries role as a custom claim for fast checks.
- Mutations and sensitive operations re-check the DB (the JWT may be slightly stale during the Clerk-update / webhook-delivery window).
- Webhook handler uses `event_id` + event timestamp to reject stale or out-of-order events for the same entity.

## Common mistakes

1. **Adding a new endpoint without `Depends(enforce_client_access)`** → startup audit catches it. Don't bypass by routing through a wrapper that strips the check.
2. **Writing an authenticated test without the cross-tenant case** → marker audit catches it. Don't add the marker without writing the case.
3. **Calling DB queries directly with a `client_id` from request body** → the audit catches it at startup. If `client_id` is in the body schema, the dep is required.
4. **Background job triggered by user input that doesn't re-check tenancy** → covered by integration test for the job, not by startup audit. Write the test.
5. **Trusting JWT role claims for sensitive operations** → re-check the DB. JWT can be stale during webhook delivery.

## Workflow when adding a new route

1. Identify the resource. What's its tenant ownership? (`Organization` → `Client` → `Market` hierarchy.)
2. Pick `enforce_client_access` (if client-scoped) or `enforce_organization_access` (if org-scoped).
3. Add the dependency in the function signature.
4. Write the test with `@pytest.mark.tenancy_isolated` and a cross-tenant case.
5. Run `pytest -m tenancy_isolated` to confirm.
6. Run `python -m tenancy.audit_routes` to confirm startup audit passes.
7. Commit.

Tenancy is the most expensive bug class to retrofit. The harness exists to make a miss impossible — don't work around it.
