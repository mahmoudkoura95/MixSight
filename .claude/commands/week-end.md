# /week-end — Mandatory weekly close ritual

Run at the end of every Phase 1a/1b/1c week and at every sub-phase boundary. **Do not mark a week "complete" in `CURRENT_PHASE.md` without walking this checklist.** If any step fails, fix the root cause and re-run from the failing step.

## Definition of Done — a week is NOT "complete" until ALL gates below pass

Flipping `WEEK: N (in progress)` → `WEEK: N (complete …)` in `CURRENT_PHASE.md` is **enforced by a hook** (`.claude/hooks/week-end-gate.mjs`, wired in `.claude/settings.json`): it blocks that edit until the mechanical bar has passed for week N (the `.claude/.week-end-pass` sentinel) **and** `SHIPPED.md` records the week's `/code-review`. Don't route around the hook — satisfy the gate.

**No deferring the code review or the refactor to "next week."** That is exactly how Week 3 shipped four auth bugs and un-refactored code into the following week. If a finding is genuinely out of scope, it gets an explicit carry-over with a reason in `CURRENT_PHASE.md` — never silence.

## Gate 1 — Mechanical quality bar (must PASS)

One command runs the full non-destructive bar and writes the sentinel the completion hook checks:

```
make up                                  # Postgres (pytest needs it)
bash scripts/week_end_gate.sh <week-number>
```

That runs: `apps/api` ruff (check + format) + mypy strict + pytest; `apps/web` typecheck + lint + build. On a full pass it writes `.claude/.week-end-pass`.

Run separately (destructive — disposable DB; CI also runs it on push), plus the lockfile check:

```
cd apps/api && uv run alembic upgrade head && uv run alembic downgrade base && uv run alembic upgrade head
pnpm install --frozen-lockfile
```

## Gate 2 — Behavioral + demoability smoke

Bring the stack up and exercise the surfaces shipped this week — not just that the server boots.

- `make api` — FastAPI on :8000. Startup logs show `startup.invariants_ok`. `curl http://localhost:8000/healthz` returns `{"status":"ok",...}`.
- `make web` — Next.js on :3000. Visit `/` signed out → redirects to `/sign-in`; the sign-in page renders. No console errors.
- **Demoability check (signed-in happy path).** A surface that boots but that no signed-in user can reach with data is not demoable. With the local demo harness configured (`SEED_CLERK_ORG_ID` = your Clerk org id, then `uv run python scripts/seed_nb_emea.py`, then `NEXT_PUBLIC_DEMO_PACING_PATH` = the printed path), sign in and follow the home-page link. Confirm the surface renders **with seeded data** — not a 404 or empty state. A 404 here means the signed-in org doesn't own the seed data (tenancy/seed-org misalignment).
- Walk every NEW user-facing surface that shipped this week. UI work without a real browser pass is not "complete." If you cannot test in a browser (headless env, etc.), say so explicitly — never claim success on a UI surface without a browser pass.

## Gate 3 — Code review (mandatory, non-deferrable)

Run `/code-review --effort high` on the week's diff (or working tree if not yet in git). **Triage every finding**: fix now, defer with an ADR, or note as an accepted risk with a reason. A week cannot be signed off with un-triaged findings. Record the run (finding count + triage) in `SHIPPED.md`.

Verify the review covers the §7.x correctness guard rails (they retrofit expensively):

- **Tenancy (§7.19).** Every new endpoint with `client_id`/`organization_id` calls `enforce_*_access`. Every authenticated endpoint test carries `@pytest.mark.tenancy_isolated` with the cross-tenant case.
- **AuditLog (§7.4).** Every new mutation flows through the SQLAlchemy event hook; new tracked entities are in `register_audit_hooks` and covered in `test_audit_log_hook.py`. Sensitive fields use `__audit_scrub__`.
- **LLM (§7.17).** Every new `client.messages.create` path has a documented surface fallback. Defense kit never blocks on LLM.
- **RecommendationLog (§7.10 step 11).** Every new `ReallocationSuggestion` writes a `RecommendationLog` row at creation.
- **Migrations (§6.2).** UUIDs via `gen_random_uuid()`, `numeric(18,4)` money / `numeric(8,4)` pct / `numeric(20,10)` FX, `timestamptz` always, `jsonb` never `json`, soft-delete partial indexes, `{table}_{column}_{type}` names.
- **Money + time.** No `float` for money. No `timestamp without time zone`. Compute week boundaries in one consistent basis (UTC) across seed + endpoints.
- **Secrets.** No API keys / tokens / PII logged. BYOK never persisted outside `EncryptedSecret`.
- **Empty states (§7.18).** Every new pacing surface, chart, or list declares its empty state.
- **Auth tokens.** Read Clerk's modern compact `o` org claim, not just legacy flat `org_id` (§7.19).
- **Scope drift.** Anything not traceable to a `SCOPE.md` section gets flagged — cite, ADR, or remove.

## Gate 4 — Refactor pass (mandatory)

Run `/simplify` on the week's diff and apply the cleanups (or defer specific ones with a reason). The diff you merge must read like the surrounding code: no stale dev-narrative comments, no cryptic names, no speculative abstraction, no dead `type: ignore`s. See root `CLAUDE.md` "Over-engineering patterns to actively resist." This is the gate that keeps the codebase from rotting one "we'll clean it up later" at a time.

## Gate 5 — Every new feature is tested

Enumerate everything contract-bearing shipped this week — each new endpoint, mutation, surface, algorithm, connector — and name the test that proves its contract:

- endpoint with `client_id` → cross-tenant test (`@pytest.mark.tenancy_isolated`)
- mutation → `AuditLog` coverage
- `ReallocationSuggestion` → `RecommendationLog` row
- algorithm → the edge that actually matters (e.g. negative projected delta, insufficient data, currency)
- LLM surface → the degraded / fallback path

**No new feature ships untested.** If a path genuinely can't be unit-tested (e.g. a concurrency race the SAVEPOINT fixture can't model), say so and record how it *was* verified (browser smoke, manual) — don't leave it silently uncovered.

## Gate 6 — Update the ledgers

- `CURRENT_PHASE.md`: deliverables checked off, blockers, carry-overs (with reasons), next sub-deliverable.
- `SHIPPED.md`: append a `### Week N — YYYY-MM-DD → YYYY-MM-DD` block — **Shipped per spec**, **Shipped beyond spec** (cite ADR), **Deferred** (target phase + reason), **Cut** (cite ADR), **Surprises**, and the **close ritual** record (quality bar result + `/code-review` finding count + refactor pass).
- New decisions not pre-decided in `SCOPE.md §3` → write an ADR via `/adr`.

## Sign off

Only after Gates 1–6 are green: flip `WEEK: N (complete …)` in `CURRENT_PHASE.md` — the hook allows it once the sentinel + `SHIPPED.md` entry exist — and surface a one-paragraph wrap-up with the headline result + open questions. Wait for the user's go-ahead before invoking `/phase-start` or moving to the next sub-deliverable.

## What this ritual is not

- It is **not** a substitute for the §7.4 / §7.19 / §7.17 contract tests that run on every commit. Those gate every change; this ritual gates every week.
- It is **not** a place to add new features. If a gate surfaces something that wants more work, that's Week N+1 scope (a tracked carry-over), not Week N closing.
