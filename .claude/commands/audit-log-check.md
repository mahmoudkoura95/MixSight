---
description: Verify every mutation path writes to AuditLog via the SQLAlchemy event hook. Catches handwritten SQL or bulk operations that bypass the hook.
---

Run an audit-log coverage check.

Per SCOPE.md §7.4, every mutation writes to `AuditLog`. The mechanism is a SQLAlchemy event hook registered at app startup (`apps/api/audit/hooks.py`). The hook is not optional — if you find yourself bypassing it for a specific mutation, that's a code smell, not a workaround.

## Part 1 — Find potential bypasses

```bash
# Raw SQL outside Alembic
rg -n "text\(|execute\(['\"]" apps/api/ --type py | rg -v "alembic|migrations|tests/"

# Bulk operations that may skip ORM hooks
rg -n "bulk_insert_mappings|bulk_save_objects|bulk_update_mappings" apps/api/ --type py

# Direct DBAPI cursor use
rg -n "engine\.execute|connection\.execute" apps/api/ --type py
```

For each match: confirm that the mutation either (a) goes through ORM with the hook firing, or (b) writes an explicit AuditLog entry alongside.

## Part 2 — Verify hook registration

```bash
rg -n "event\.listen|listens_for" apps/api/audit/ --type py
```

The hook should be registered for:
- `before_insert`, `before_update`, `before_delete` on `Base` (or the SQLModel parent).
- Captures: actor from request scope, request_id from middleware, before/after via `inspect(target).attrs`.
- Skips: `AuditLog` itself (no recursion), `ConnectorAuthEvent` (its own audit trail), event tables that are append-only by design.

## Part 3 — Spot-check entity coverage

For each Phase 1 entity in §7.4, verify a mutation produces an AuditLog row:

```bash
cd apps/api && pytest tests/audit/test_coverage.py -v
```

The coverage test should mutate one of each entity type and assert an AuditLog row exists with the right `entity_type`, `entity_id`, `action`, `before`, `after`.

Entities to cover (Phase 1):
- Organization, User, Client, Market, MarketConfig
- ConnectorAuth, AdAccountMapping
- ClientTaxonomy, CampaignLabelRule
- Plan, PlanLine
- Actuals (note: pull-driven; AuditLog only on revisions per §7.14)
- PacingSnapshot, PacingSnapshotLine
- ReconciliationFactor
- ReallocationSuggestion, RecommendationLog
- DefenseKit
- PromotionalEvent

## Part 4 — Retention semantics

Verify retention:
- AuditLog rows older than 7 years: scheduled cleanup job exists (Phase 2a+).
- On customer deletion (§6.6): anonymization replaces actor_user_id and customer-identifying fields in `before`/`after` JSONB with deterministic hashes.

## Output

| Entity | Hook firing? | Retention covered? |
|---|---|---|

Plus a verdict:
- ✓ All mutation paths covered. Hook registered. Retention policy in place.
- ✗ N entities missing coverage / M bypass paths found / retention not configured.

The audit log is the foundation for SOC 2 (Phase 2), GDPR right-to-be-forgotten, and the recommendation-calibration loop in Phase 4. Holes today are expensive tomorrow.
