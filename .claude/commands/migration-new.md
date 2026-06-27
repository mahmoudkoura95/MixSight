---
description: Scaffold a new Alembic migration following §6.2 conventions. Invokes the migration skill. Use this rather than running alembic directly.
argument-hint: <description> (e.g., "add_macro_signal_indexes")
---

Scaffold a new Alembic migration: `$ARGUMENTS`.

1. **Load the migration skill** at `.claude/skills/migration/SKILL.md`. Follow its conventions exactly.

2. **Verify scope.** Which scope section authorizes this migration? Cite it. If you can't cite one, stop and ask the user — migrations are not casual.

3. **Verify phase.** Read `CURRENT_PHASE.md`. Is this migration appropriate for the active phase? If it touches a table from a later phase but the table was already provisioned empty in Phase 1a per §7.21, that's fine — you're adding columns/indexes, not creating new tables.

4. **Run alembic autogenerate** if the migration follows from a model change:

   ```bash
   cd apps/api && alembic revision --autogenerate -m "$ARGUMENTS"
   ```

   If it's a manual migration (e.g., backfill, custom SQL), use:

   ```bash
   cd apps/api && alembic revision -m "$ARGUMENTS"
   ```

5. **Review the generated migration against §6.2 defaults:**
   - UUIDs via `gen_random_uuid()` — server default, not Python.
   - Monetary columns: `numeric(18, 4)`. **Never `float`.**
   - Percentage / ratio columns: `numeric(8, 4)`.
   - FX rate columns: `numeric(20, 10)`.
   - Timestamp columns: `timestamp with time zone`. Stored UTC.
   - JSONB columns: `jsonb`, not `json`. GIN index if filtered.
   - Soft delete: `deleted_at timestamptz` nullable with partial index `WHERE deleted_at IS NULL`.
   - Every FK gets an index.
   - Every `(client_id, ...)` query pattern gets a composite index.
   - Constraint names follow `{table}_{column}_{type}`.

6. **Verify special-entity rules:**
   - `Actuals`: UNIQUE constraint on `(client_id, market_id, channel, campaign_external_id, date, source)`.
   - `AuditLog`: append-only. No update path. Indexes on `(organization_id, occurred_at)` and `(entity_type, entity_id)`.
   - `EncryptedSecret`: indexes on `key_version` for rotation queries.
   - `ConnectorAuth`: unique constraint on `(organization_id, platform)`.
   - `RecommendationLog`: indexes for calibration queries on `(client_id, recommendation_source, recommended_at)`.

7. **Document deviations.** If a default in §6.2 doesn't apply for this migration, add a comment in the migration file explaining why. Predictable conventions matter more than concise ones.

8. **Generate the downgrade.** Every `upgrade()` has a working `downgrade()`. Test it locally:

   ```bash
   cd apps/api && alembic upgrade head && alembic downgrade -1 && alembic upgrade head
   ```

9. **Run tests** affected by the schema change.

10. **Update `DECISIONS.md`** if this migration represents a model decision (new table semantics, new constraint logic, deviation from defaults).

Stop and confirm before applying to any environment other than local.
