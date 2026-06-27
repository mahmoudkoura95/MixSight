# /week-end — Mandatory weekly close ritual

Run at the end of every Phase 1a/1b/1c week and at every sub-phase boundary. **Do not mark a week "complete" in `CURRENT_PHASE.md` without walking this checklist.** If any step fails, fix the root cause and re-run from the failing step.

## Step 1 — Full quality bar (must exit 0)

### `apps/api`
- `cd apps/api && uv run ruff check src tests`
- `cd apps/api && uv run ruff format --check src tests`
- `cd apps/api && uv run mypy src`
- `cd apps/api && uv run pytest -v`
- `cd apps/api && uv run alembic upgrade head && uv run alembic downgrade base && uv run alembic upgrade head` — migration round-trip

### `apps/web`
- `pnpm --filter @mixsight/web typecheck`
- `pnpm --filter @mixsight/web lint`
- `pnpm --filter @mixsight/web build`

### Workspace
- `pnpm install --frozen-lockfile` — lockfile is current

## Step 2 — Boot + behavioral smoke test

Bring the stack up locally and exercise the surfaces shipped this week.

- `make up` (or `pnpm db:up`) — postgres + redis healthy.
- `make api` — FastAPI on :8000. Confirm startup logs show `startup.invariants_ok`. `curl http://localhost:8000/healthz` returns `{"status":"ok",...}`.
- `make web` — Next.js on :3000. Visit `/` while signed out → redirects to `/sign-in`. The sign-in page renders with the navy/teal brand. No console errors.
- Run through every NEW user-facing surface that shipped this week. UI work without a real browser pass is not "complete."

### Demoability check (signed-in happy path)

A surface that boots but that no signed-in user can reach with data is not actually demoable. Prove the happy path end-to-end, not just that the server starts:

- With the local demo harness configured (`SEED_CLERK_ORG_ID` = your Clerk org id, then `uv run python scripts/seed_nb_emea.py`, then `NEXT_PUBLIC_DEMO_PACING_PATH` = the path the seed prints), sign in and follow the home-page link.
- Confirm the pacing surface renders **with seeded data** — table rows, drift, status badges, reallocation options — not a 404 or an empty state. A 404 here means the signed-in org doesn't own the seed data (tenancy/seed-org misalignment).

If you cannot test a surface in a browser (no display, headless env, etc.), say so explicitly — never claim success on a UI surface without a browser pass.

## Step 3 — Code review

Invoke `/code-review` on the week's diff (or working tree if not yet in git). For each finding, decide: fix now, defer with an ADR, or note as accepted risk.

Focus areas to verify the review covers (these are the §7.x correctness guard rails that retrofit expensively):

- **Tenancy (§7.19).** Every new endpoint with `client_id`/`organization_id` calls `enforce_*_access`. Every authenticated endpoint test carries `@pytest.mark.tenancy_isolated` and includes the cross-tenant case.
- **AuditLog (§7.4).** Every new mutation path flows through the SQLAlchemy event hook in `apps/api/src/mixsight/audit/hooks.py`. New tracked entities are listed in `register_audit_hooks` (`apps/api/src/mixsight/main.py`) and covered in `apps/api/tests/test_audit_log_hook.py`.
- **LLM (§7.17).** Every new `client.messages.create` path has a documented fallback per its surface. Defense kit never blocks on LLM.
- **RecommendationLog (§7.10 step 11).** Every new `ReallocationSuggestion` writes a `RecommendationLog` row at creation.
- **Migrations (§6.2).** Every new migration follows the conventions: UUIDs via `gen_random_uuid()`, `numeric(18,4)` for money / `numeric(8,4)` for percentages / `numeric(20,10)` for FX, `timestamptz` always, `jsonb` never `json`, soft-delete partial indexes on hot query paths, `{table}_{column}_{type}` constraint naming.
- **Money + time.** No `float` columns for money. No `timestamp without time zone`.
- **Secrets.** No API keys, OAuth tokens, BYOK keys, or PII logged. BYOK keys never persisted outside `EncryptedSecret`.
- **Empty states (§7.18).** Every new pacing surface, chart, or list view declares its empty state explicitly.
- **Scope drift.** Anything not traceable to a `SCOPE.md` section gets flagged — either cite the section, write an ADR, or remove.

## Step 4 — Update the ledgers

- Update `CURRENT_PHASE.md` to reflect actuals: which deliverables checked off, blockers, notes, and next sub-deliverable.
- Append a `### Week N — YYYY-MM-DD → YYYY-MM-DD` block to `SHIPPED.md` under the current phase: **Shipped per spec**, **Shipped beyond spec** (extension; cite ADR), **Deferred to later phase**, **Cut from scope** (cite ADR), **Surprises**.
- If any decisions came up that weren't pre-decided in `SCOPE.md §3`, write an ADR via `/adr` before closing the week.

## Step 5 — Sign off

Only after Steps 1–4 are green, flip `WEEK: N (complete)` in `CURRENT_PHASE.md` and surface a one-paragraph wrap-up to the user with the headline result + open questions. Wait for the user's go-ahead before invoking `/phase-start` (or moving to the next week's sub-deliverable).

## What this ritual is not

- It is **not** a substitute for the §7.4 / §7.19 / §7.17 contract tests that run on every commit. Those gate every change; this ritual gates every week.
- It is **not** a place to add new features. If Step 3 surfaces something that wants more work, that's Week N+1 scope, not Week N closing.
