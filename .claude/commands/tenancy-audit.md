---
description: Run the §7.19 tenancy harness. Verify every endpoint with client_id enforces access, and every authenticated endpoint test has the cross-tenant case. Should pass before every commit.
---

Run the tenancy harness audit per SCOPE.md §7.19.

## Part 1 — Static route audit

1. **Boot the API in audit mode.** Run the startup decorator audit:

   ```bash
   cd apps/api && python -m tenancy.audit_routes
   ```

   This script introspects every FastAPI route and verifies:
   - Routes with `client_id` in path, query, or body have `enforce_client_access` in their dependency chain.
   - Routes with `organization_id` have `enforce_organization_access`.
   - Background-triggered routes that have implicit tenancy from `current_user` are flagged for review (these are the harder dynamic class — caught by integration tests below).

2. **If any route fails the audit:** the script outputs the offending route path and method. Fix each before continuing. Routes that fail the audit cannot merge — app startup will refuse.

## Part 2 — Integration test pattern

1. **Run the cross-tenant test suite:**

   ```bash
   cd apps/api && pytest -m tenancy_isolated -v
   ```

   The `@pytest.mark.tenancy_isolated` marker requires every authenticated endpoint test to include a cross-tenant case using fixtures `user_a_in_org_1` and `user_b_in_org_2`. If `user_b` does not get 403 (or 404 if we're hiding existence) on resources owned by `user_a`, the test fails.

2. **Run the marker enforcement check:**

   ```bash
   cd apps/api && python -m tenancy.audit_tests
   ```

   This scans test files for authenticated endpoint tests and verifies each is decorated with `@pytest.mark.tenancy_isolated`. Missing decorators fail the audit.

## Part 3 — Spot checks

For any endpoint added in the current branch:

1. Open the route file. Confirm `Depends(enforce_client_access)` (or `enforce_organization_access`) is in the function signature.
2. Open the corresponding test file. Confirm `@pytest.mark.tenancy_isolated` is on every authenticated test.
3. Confirm the test includes a `user_b_in_org_2` case asserting 403 or 404.

## Output

Produce a verdict:

- ✓ All routes pass static audit. All tests pass marker audit. All cross-tenant assertions pass. Safe to commit.
- ✗ N routes failing static audit / M tests missing markers / K assertions failing. **Do not commit until resolved.**

Tenancy is the single most expensive bug class to retrofit. The harness exists to make a missed check impossible to merge. Treat its output as binary, not advisory.
