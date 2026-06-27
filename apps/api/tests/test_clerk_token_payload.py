"""Unit coverage for Clerk session-token parsing (§7.19 auth).

Clerk's modern session token packs the active organization into a compact
`o` claim (`{id, rol, slg}`) instead of the legacy flat `org_id` / `org_role`.
The backend reads `org_id` / `org_role` for tenancy + JIT provisioning, so the
payload model must lift the `o` claim — otherwise every signed-in request
loses its org context and tenancy fails. Regression for the live bug where
the pacing surface 404'd because `payload.org_id` was always None.
"""

from __future__ import annotations

from mixsight.auth.clerk import ClerkTokenPayload
from mixsight.webhooks.handlers.common import map_clerk_role

_BASE = {"sub": "user_1", "iss": "https://test.clerk", "exp": 2_000_000_000, "iat": 1_700_000_000}


def test_compact_o_claim_is_hoisted_to_org_id_and_role() -> None:
    payload = ClerkTokenPayload.model_validate(
        {**_BASE, "o": {"id": "org_abc", "rol": "admin", "slg": "brave-bison"}}
    )
    assert payload.org_id == "org_abc"
    assert payload.org_role == "admin"


def test_legacy_flat_org_claims_still_work() -> None:
    payload = ClerkTokenPayload.model_validate(
        {**_BASE, "org_id": "org_legacy", "org_role": "org:admin"}
    )
    assert payload.org_id == "org_legacy"
    assert payload.org_role == "org:admin"


def test_no_org_claim_leaves_org_id_none() -> None:
    payload = ClerkTokenPayload.model_validate(_BASE)
    assert payload.org_id is None
    assert payload.org_role is None


def test_map_clerk_role_handles_both_prefixed_and_compact_forms() -> None:
    # Session-token `o.rol` form (un-prefixed)
    assert map_clerk_role("admin") == "admin"
    assert map_clerk_role("account_manager") == "account_manager"
    # Webhook form (org:-prefixed)
    assert map_clerk_role("org:admin") == "admin"
    assert map_clerk_role("org:account_manager") == "account_manager"
    # Unknown / missing → least-privileged default
    assert map_clerk_role("org:billing") == "account_manager"
    assert map_clerk_role(None) == "account_manager"
