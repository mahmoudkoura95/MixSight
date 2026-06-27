# Current Phase

```
PHASE: 1a
WEEK: 3 (complete — 2026-06-26)
SUB_DELIVERABLE: CSV ingestion + single-client pacing view + within-market reallocation (per ADR-003)  ✓
PREVIOUS_SUB_DELIVERABLE: Full §7.4 schema + RecommendationLog + real Clerk webhook dispatch + Week 1 code-review carry-overs  ✓ (Week 2)
NEXT_SUB_DELIVERABLE: Template-based plan CSV upload + static defense kit (templated narrative) + CSV-specific empty states + Monday-morning upload reminder + Phase 1a internal-acceptance demo (Week 4)
DESIGN_PARTNER_COMMITTED: true
DESIGN_PARTNER: Brave Bison Agency
PILOT_CLIENT: New Balance EMEA
PILOT_MARKET: UK (Week 3 single-market focus; multi-market UI is Phase 1b per §7.20)
PILOT_CHANNEL: Meta (Week 3 single-channel per §7.3; native Meta Ads Manager CSV parser first per ADR-003)
DESIGN_PARTNER_COMMIT_DATE: 2026-06-21
DESIGN_PARTNER_FIRST_ACCESS: Phase 1b Week 1 (per ADR-004, on real NB EMEA data)
INGESTION_MODEL: CSV-first (see ADR-003)
PYTHON_PKG_MGR: uv (see ADR-004)
CLERK_UX: Clerk Elements custom components (see ADR-004)
DEPLOYED_INFRA: deferred to Phase 1c (see ADR-004)
```

## Phase 1a Week 3 — IN PROGRESS (kicked off 2026-06-26)

**Plan citation:** §7.3 Phase 1a (mod ADR-003), §7.10 reallocation, §7.14 connector protocol, §7.18 empty states, §7.19 tenancy. Out-of-scope §7.20, risks §7.21.

### Day 1-2 — Week 2 /code-review HIGH carry-overs (gate before any §7.4 mutation path ships)

- [x] AuditLog `organization_id` resolution for 18 entities — `0008_denormalize_organization_id` migration + SQLModel updates. Resolver in `audit/hooks.py` unchanged (already `getattr(target, "organization_id", None)`); NOT NULL constraint forces caller-side discipline. Coverage: static introspection test (`test_every_mutable_table_carries_organization_id`) + integration (Plan via Client).
- [x] Full JIT user provisioning in `current_user` — `_jit_provision_user` upserts Organization (by `clerk_organization_id`) + User (by `clerk_user_id`) from JWT claims inline. Placeholder email/org-name overwritten by webhook on arrival. 401 fallback when JWT carries no `org_id`. Coverage: 3 tests in `test_jit_and_clock_skew.py` (basic JIT, shared-org reuse, org-find idempotency).
- [x] Stale-event clock-skew fix — `0009_clerk_last_event_at` adds `clerk_last_event_at timestamptz NULL` to Organization + User. `is_stale_event` signature now `(stored_clerk_event_at, incoming_clerk_event_at)` — Clerk-clock to Clerk-clock. Handler callsites in organization/user/membership updated to read+write the new column. Coverage: regression test for the close-together-with-server-drift bug + sanity check that genuinely stale events still drop. Quality bar green after both Day 1 + Day 2: mypy strict 53 files, ruff clean, alembic full round-trip, 30/30 pytest (was 23 pre-week).

### Day 3 — CSV ingestion (§7.14 Protocol first impl per ADR-003)

- [x] `apps/api/src/mixsight/connectors/csv/` module shipped — `meta_ads_manager.py` (parser), `service.py` (orchestration), `routes.py` (FastAPI router). Other Protocol methods (authenticate / list_ad_accounts / health_check / backfill) land when first exercised; today only `pull_actuals`-equivalent is live.
- [x] **Meta Ads Manager native CSV parser** — case-insensitive header match, currency extracted from spend column header, schema vs body errors raise distinct exceptions mapped to ConnectorAuthEvent types. Normalized template parser deferred to Week 4.
- [x] Actuals CSV upload endpoint at `POST /clients/{client_id}/markets/{market_id}/csv/actuals` — per-row ORM upsert on §7.14 unique key so audit hook fires per row (bulk SQL bypass-and-manual-AuditLog deferred until perf measured).
- [x] `ConnectorAuthEvent` types wired: `csv_uploaded` (success), `csv_parse_failed` (body error), `schema_mismatch` (header / currency mismatch), `partial_ingestion` (zero-row CSV). No migration needed — event_type column is Text.
- [x] `ConnectorPull` row per upload — `pull_type="csv_upload"` (new value added to the conceptual enum; column is Text so no migration). Status `success` / `failed` / `partial` captured.
- [x] All endpoints depend on `enforce_client_access` per §7.19. New `authenticated_client_a` / `authenticated_client_b` conftest fixtures use httpx ASGITransport + request-time `current_user` override + `get_db` override so route writes share the test SAVEPOINT. Cross-tenant test (user_b POSTing to user_a's client → 404) ships with `@pytest.mark.tenancy_isolated`.

**Quality bar after Day 3:** mypy strict 58 files clean (was 53), ruff lint + format clean, alembic full round-trip clean, pytest 45/45 (was 30; +10 parser unit + 4 service integration + 1 endpoint).

### Day 4-5 — Pacing view + reallocation + week-end

- [x] `PacingSnapshot` + `PacingSnapshotLine` server-side compute from Plan + Actuals — `apps/api/src/mixsight/pacing/service.py`. In-week rollup for drift + separate 14-day-lookback distinct-day count for the §7.10 step 1 sufficiency check (decoupled so the snapshot week's 7-day ceiling doesn't permanently gate every line).
- [x] Single-client (NB EMEA) single-market (UK) pacing view in `apps/web/src/app/clients/[clientId]/markets/[marketId]/pacing/page.tsx` — server-rendered table + §7.16 freshness stamp + inline EmptyState component (extraction to `packages/shared` deferred until second pacing surface needs it).
- [x] §7.10 reallocation algo steps 1-11 — `apps/api/src/mixsight/pacing/reallocation.py`. `scope='within_market_within_channel'`, donor/receiver thresholds at ±5%, receiver headroom × 1.3 per step 4, confidence heuristic for Phase 1a (MMM-derived ships Phase 2). Cross-objective pairs suppressed (no shared delta scale).
- [x] RecommendationLog row at every ReallocationSuggestion creation — `_RECOMMENDATION_SOURCE='heuristic_v1'`, explicit test (`test_reallocation_writes_suggestion_and_recommendation_log`).
- [x] Empty-state coverage for the pacing surface — `no_active_plan`, `no_spend_in_market`, `insufficient_data`, partial-week banner. Full §7.18 catalog walk (incl. CSV-specific never-uploaded / parse-failed / schema-mismatch) lands Week 4 alongside template-plan-CSV UI.
- [x] `apps/api/scripts/seed_nb_emea.py` — idempotent rich generator: 1 Org (Brave Bison) + 1 Client (NB EMEA) + 1 Market (UK/GBP) + 1 active Plan + 6 PlanLines + 84 Actuals (14 days × 6 campaigns) shaped so reallocation has visible donor/receiver pairs.
- [x] `/week-end` ritual — see "Week 3 close" block below.

### Week 3 close (2026-06-26)

**Quality bar:** mypy strict 62 src files clean, ruff lint + format clean (incl. `scripts/`), pytest 51/51 (was 30 at start of week — +21 across Day 1-5), alembic full down/up round-trip clean, `apps/web` typecheck + lint + build clean (3 routes: `/`, `/sign-in/[[...sign-in]]`, `/sign-up/[[...sign-up]]`, `/clients/[clientId]/markets/[marketId]/pacing`).

**Boot smoke:** API on :8000 returns 200 on `/healthz`. Seed script runs end-to-end against running DB (84 actuals upserted into the seed org/client/market). Idempotent — re-running upserts every row by natural key.

**Migrations shipped this week:**
- `0008_denormalize_organization_id` — 18-entity org_id denormalization for AuditLog tenant scoping.
- `0009_clerk_last_event_at` — Clerk-clock-only stale-event guard.

### Week 3 → Week 4 carry-overs (self-flagged, no formal /code-review run)

**MEDIUM (Week 4 if time allows, deferred from Week 2 + flagged again):**
- [ ] Concurrent webhook race → IntegrityError → 500 → Clerk retry (also affects JIT provisioning race). Fix with `INSERT ... ON CONFLICT DO NOTHING` and re-query.
- [x] EncryptedSecret ciphertext written into AuditLog before/after. **Fixed in the 2026-06-27 review pass** via `__audit_scrub__` field set on the model + redaction in the audit hook's `_serialize` / `_change_diff`. Audit row still records the create/update/delete; the value is `[redacted]`. Coverage: 2 tests in `test_audit_log_hook.py`.
- [ ] Tenancy audit silent degrade — `_route_parameter_names` catches all `get_type_hints` errors; narrow the except + log a warning on fallback.

**NEW MEDIUM (from this week's code):**
- [ ] CSV ingestion uses per-row ORM upsert so audit hook fires per row. For Phase 1a's ~hundreds-of-rows weekly CSVs that's fine; when Phase 1b API connectors push thousands of rows daily, switch to bulk `INSERT ... ON CONFLICT` + manual AuditLog writes per the audit-log skill bypass guidance.
- [ ] No test covers the "JWT carries no `org_id`" 401 fallback path through `_jit_provision_user`. Add when the second authenticated endpoint lands.

**NEW LOW:**
- [ ] Pacing service's status combiner takes the worst of (spend_status, kpi_status). UX call worth surfacing — green spend + critical KPI rolls up as "critical" today; AM may want richer "kpi-critical" distinction in Phase 1b.
- [ ] `apps/web` dev server may need a restart after Day 5 routes were added (hot-reload sometimes doesn't pick up new dynamic-param routes — `pnpm build` confirms the route is registered).
- [x] Service-layer type ignores on `record: object` in `connectors/csv/service._upsert_actuals_row` — **fixed in the 2026-06-27 review pass**: typed as `MetaActualsRecord` (no real import cycle existed), all 12 `# type: ignore` removed.
- [ ] `EmptyState` component inlined in pacing page; extract to `packages/shared/` when second pacing surface (current-week view, Phase 1c) needs it.
- [ ] Frontend env var `NEXT_PUBLIC_API_BASE_URL` defaults to `http://localhost:8000`; document in `apps/web/.env.example` once deployed-infra decision lands (Phase 1c per ADR-004).

**No formal `/code-review` run this week — user-initiated per CLAUDE.md.** Flag at next session if the carry-over list above needs `/code-review --effort high` validation.

### Code-review + clarity refactor pass (2026-06-27)

User-initiated full review + refactor of the Weeks 1-3 surface. Repo put under git for the first time (baseline on `origin/main`; this pass on branch `refactor/code-review-pass`). Scope citations kept per CLAUDE.md; only stale dev-narrative + cryptic names trimmed.

**Correctness bugs fixed (with tests):**
- Reallocation ranked KPI-reducing moves as top "options" — `reallocation.py` ranked by `abs(delta)`, so a negative projected delta (receiver efficiency below donor) surfaced high and rendered as `≈ +-N`. Now non-positive deltas are dropped. Test: `test_reallocation_skips_negative_projected_delta`.
- `_score_confidence` took an unused `amount` arg whose docstring claimed a signal the code never used — removed; docstring corrected.
- Reallocation rationale hardcoded `£` regardless of market — now prefixes the market's ISO currency code (resolved from `Market.local_currency`).
- CSV upload to a market not under the client returned 422 `csv_currency_mismatch` (misleading) — now a proper 404 via new `MarketNotUnderClientError`; no spurious `schema_mismatch` ConnectorAuthEvent. Test: `test_market_not_under_client_raises_404_error_with_no_event`.
- Duplicate-snapshot race: the pacing view + reallocation view load in parallel and both generate-on-demand, creating two snapshots for one week. New `get_or_create_snapshot` serialises the create with a transaction-level Postgres advisory lock (double-checked); both routes go through it.

**Clarity / jargon (citations preserved):**
- `main.py` docstring rewritten (it still described a "Week 1 skeleton" that boots without the audit/tenancy wiring it now installs).
- `connectors/csv/service._upsert_actuals_row` typed as `MetaActualsRecord` (see carry-over above).
- `pacing/service.py`: dropped the single-field `_CampaignHistory` wrapper for `dict[str, int]`; replaced the `max(..., key=tuple.index)` worst-status trick with a small `_STATUS_SEVERITY` map + `_worse_status`.
- `reallocation.py`: cryptic `lwp` local renamed to `line`.
- `apps/web/src/lib/api.ts`: dropped "(Day 2 work)" dev-narrative.

**Quality bar green:** ruff (lint+format), mypy strict (62 files), pytest **55 passed** (51 + 4 new), web typecheck + lint.

**Not addressed (still open carry-overs):** webhook concurrent-insert race, tenancy-audit silent degrade, the "JWT carries no org_id" 401 test, CSV per-row→bulk upsert (by design for Phase 1a), `EmptyState` extraction.

### Week 3 active decisions (locked 2026-06-26)

- **Market:** UK (per CURRENT_PHASE.md note + user confirm).
- **Channel:** Meta Ads Manager native CSV parser first (per §7.3 + ADR-003 + user confirm).
- **Fixtures:** Rich generator at `scripts/seed_nb_emea.py` (user confirm — pays off for Week 4 demo + later backfill testing).

### Active blockers (Week 3)

- None at kickoff. The HIGH carry-overs are sequenced first, not blocking — they ARE Day 1-2 work.

---

## Phase 1a Week 2 — DONE (2026-06-24 → 2026-06-25)

### Day 1 — Week 1 code-review carry-overs

- [x] Async-wrap `PyJWKClient.get_signing_key_from_jwt(...)` in `asyncio.to_thread`
- [x] Pure-ASGI request-context middleware sets `actor_user_id` + `request_id` contextvars per request
- [x] Tenancy audit recursively inspects Pydantic body models via `get_type_hints` (handles `from __future__ import annotations`)
- [x] JIT user provisioning — **placeholder only** (improved 401 + structured log). Full upsert deferred again (see Week 3 carry-overs below).
- [x] Transaction-rollback fixture (SAVEPOINT per test) in `apps/api/tests/conftest.py`

### Days 2-3 — §7.4 full schema (4 migrations, 22 new SQLModels)

- [x] `0004_connector_layer` — Organization/Client/Market/UserClientAccess expanded with full §7.4 fields (incl. `clerk_organization_id`, denormalized `organization_id` on Market + UCA). NEW: EncryptedSecret, MarketConfig, ConnectorAuth, AdAccountMapping, ConnectorAuthEvent.
- [x] `0005_taxonomy_plans` — ClientTaxonomy, CampaignLabelRule, Plan, PlanLine.
- [x] `0006_actuals_pacing` — Actuals (+ §7.14 idempotency UNIQUE), PacingSnapshot, PacingSnapshotLine, ReconciliationFactor, ReallocationSuggestion, RecommendationLog.
- [x] `0007_artifacts_futures` — DefenseKit, PromotionalEvent, ConnectorPull. Phase 2/4 empties: MacroSignal, ContributionFit, IncrementalityResult, ForecastRun.
- [x] Every Phase 1 mutable entity registered with `register_audit_hooks`; append-only entities (RecommendationLog, ConnectorPull, ForecastRun, ConnectorAuthEvent, AuditLog) explicitly excluded per audit-log skill.
- [x] Migration round-trip clean — full `downgrade base` → `upgrade head` round-trip across all 7 migrations.

### Day 4 — Real Clerk webhook dispatch

- [x] Per-event handlers: `organization.{created,updated,deleted}`, `user.{created,updated,deleted}`, `organizationMembership.{created,updated,deleted}`.
- [x] Out-of-order protection via `is_stale_event` (event_updated_at vs entity.updated_at) — see Week 3 carry-over for the clock-skew issue.
- [x] Coverage tests against realistic Clerk fixture payloads (9 new tests, bypassing svix to call dispatch directly with the SAVEPOINT fixture).
- [x] Idempotent upserts keyed by `clerk_organization_id` / `clerk_user_id`.
- [x] Role mapping: `org:admin` → `admin`, `org:account_manager` → `account_manager`, unknown → log warning + default to `account_manager`.

### Day 5 — `/week-end` ritual

- [x] Quality bar: mypy strict (53 src files clean), ruff (lint + format clean), pytest (23/23 passing), alembic full down/up round-trip green, apps/web typecheck + lint + build green.
- [x] Boot smoke: FastAPI on :8000, `curl /healthz` returns ok with `x-request-id` header confirming Day 1 middleware fires.
- [x] `/code-review --effort high` — 13 findings, triaged below.
- [x] Ledger updates: this file + `SHIPPED.md` Week 2 block.

## Week 2 → Week 3 carry-overs from `/code-review`

**HIGH severity (fix early in Week 3 — before any business mutation path ships):**
- [ ] AuditLog `organization_id` resolution still returns NULL for 15+ entities (Plan, PlanLine, Actuals, PacingSnapshot, ReallocationSuggestion, RecommendationLog, DefenseKit, ClientTaxonomy, CampaignLabelRule, ReconciliationFactor, MarketConfig, AdAccountMapping, EncryptedSecret, PromotionalEvent, MacroSignal, ContributionFit, IncrementalityResult). Week 1 fixed Market + UCA only — same denormalization pattern needs to extend to the rest, OR `_resolve_organization_id` widens with explicit per-entity rules.
- [ ] Full JIT user provisioning in `current_user` — schema dependency (`clerk_organization_id`) shipped Day 2; implementation still deferred. Closes the §7.19 eventual-consistency race for sign-ups that beat the webhook.
- [ ] Stale-event clock-skew: `is_stale_event` compares Clerk-clock event timestamps to server-clock entity `updated_at`; structural false-positive rejects legitimate close-together updates. Fix: add `clerk_last_event_at` to Organization + User, compare Clerk-clock to Clerk-clock.

**MEDIUM severity (Week 3 if time allows):**
- [ ] Concurrent webhook race → IntegrityError → 500 → Clerk retry. Fix with `INSERT ... ON CONFLICT DO NOTHING`.
- [ ] EncryptedSecret ciphertext written into AuditLog before/after — extends key-compromise blast radius. Fix: exclude EncryptedSecret from `register_audit_hooks` OR add `__audit_scrub__` field allowlist.
- [ ] Tenancy audit silent degrade — `_route_parameter_names` catches all `get_type_hints` errors. Narrow the except + log a warning on fallback.

**LOW severity (track + defer):**
- [ ] Membership restore doesn't update email; stale email may persist through a delete/rejoin cycle if user.updated arrived during the soft-delete window.
- [ ] Organization JIT-create from update payload uses server now() as created_at, not the original Clerk created_at.
- [ ] Organization.handle_deleted skips the §7.4-implied grace_period workflow — goes directly active → deleted. Acceptable until Phase 1c billing.
- [ ] Test fixtures use wall-clock `time.time()` — clock-skew brittleness. Migrate to monotonic counter or frozen-time fixture in Week 3 conftest.
- [ ] x-request-id header reflected verbatim — log-injection risk. Add UUID-format validation.
- [ ] Webhook handler doesn't wrap each handler in a SAVEPOINT — partial writes get rolled back on close which is fine, but Clerk retries see noisy logs.

**Fixed in-week (during /code-review):**
- [x] `from mixsight.webhooks.handlers import dispatch` import ambiguity (function vs module). Trimmed `__init__.py` re-export; `clerk.py` now imports `from .dispatch import dispatch` explicitly.

## Phase 1a Week 1 deliverables — DONE

- [x] Monorepo scaffold per §6.1 — `apps/web`, `apps/api`, `apps/api/connectors`, `packages/types`, `packages/shared`, `modeling/engines`, `templates/plans`, `infra/docker`, `scripts`
- [x] Sub-CLAUDE.md files at every sub-directory
- [x] Postgres 15 + Redis 7 via `infra/docker/docker-compose.yml`
- [x] FastAPI skeleton in `apps/api/` — Python 3.11+, sqlmodel, Pydantic v2, async, `/healthz` endpoint, deps via `uv` per ADR-004
- [x] Alembic configured (async-only via `run_sync`, no psycopg) + migrations skill validated end-to-end
- [x] Clerk integration on web side using **Clerk Elements** (custom sign-in/sign-up components matching `apps/site` brand) per ADR-004
- [x] FastAPI JWT validation against Clerk JWKS (`apps/api/src/mixsight/auth/`) + Clerk webhook stub at `/webhooks/clerk`
- [x] **Tenancy harness — startup decorator audit** per §7.19 (`apps/api/src/mixsight/tenancy/audit.py`, wired into FastAPI lifespan)
- [x] **Tenancy harness — `@pytest.mark.tenancy_isolated` marker** per §7.19 (registered in `pyproject.toml`, enforced via `conftest.py` collection hook)
- [x] **AuditLog table + SQLAlchemy event hook** per §7.4 (`apps/api/src/mixsight/audit/hooks.py`, registered for Organization/User/UserClientAccess/Client/Market)
- [x] AuditLog coverage tests (created/updated/soft-deleted/hard-deleted on Organization)
- [x] Minimum §7.4 entity migrations: Organization, User, UserClientAccess, Client, Market
- [x] GitHub Actions CI workflow at `.github/workflows/ci.yml` (verifies on first push)
- [x] Local quality bar green: mypy strict (24 src files), ruff (lint + format), pytest (11 tests)

## Phase 1a remaining deliverables (Weeks 2-4, see SCOPE.md §7.3 modified per ADR-003)

- [ ] **Week 2:** Full §7.4 schema migration (all Phase 1 entities + Phase 2/4 tables provisioned empty per locked decision)
- [ ] **Week 2:** RecommendationLog skeleton, ConnectorAuth + AdAccountMapping schemas provisioned (empty for CSV clients)
- [ ] **Week 2:** Real Clerk webhook dispatch (`organization.created`, `user.created`, `organizationMembership.*`) replaces the Day 4 stub
- [ ] **Week 2 — from Week 1 `/code-review` carry-over:**
  - [ ] Tenancy audit body-shaped gap: recursively inspect Pydantic body models for `client_id`/`organization_id` fields (§7.19 spec: 'path, query, OR body')
  - [ ] JIT user provisioning on first authenticated request — closes the JWT-valid-but-row-missing race per §7.19 'eventual-consistency window' guidance
  - [ ] Denormalize `organization_id` onto Market + UserClientAccess so AuditLog rows for those entities are tenant-scoped
  - [ ] Wrap `PyJWKClient.get_signing_key_from_jwt(...)` in `asyncio.to_thread` per apps/api/CLAUDE.md 'async everywhere' rule
  - [ ] FastAPI middleware sets `actor_user_id` + `request_id` contextvars on every request (so AuditLog stops storing NULLs)
  - [ ] Transaction-rollback fixture in conftest.py (SAVEPOINT per test) — replaces the current accumulation pattern
- [ ] **Week 3:** CSV ingestion (Meta Ads Manager + Google Ads + GA4 native parsers; normalized template fallback) per ADR-003 — implements §7.14 Connector Protocol
- [ ] **Week 3:** Drag-drop CSV upload UI on the pacing page
- [ ] **Week 3:** `ConnectorAuthEvent` event types for CSV: `csv_uploaded`, `csv_parse_failed`, `schema_mismatch`, `partial_ingestion`
- [ ] **Week 3:** Single-client (NB EMEA, single EMEA market) + single-channel end-to-end pacing view per §7.3
- [ ] **Week 3:** Within-market within-channel reallocation per §7.10
- [ ] **Week 4:** Template-based plan CSV upload (§7.3 "Plan ingestion via CSV upload (template-based)") — pairs with defense kit which needs a Plan to render against. **AI plan parser stays Phase 1b per §7.6 + §7.20.**
- [ ] **Week 4:** Static (non-editable) defense kit with templated narrative per §7.13
- [ ] **Week 4:** Empty-state handling per §7.18 — including CSV-specific: never-uploaded, partial-week-uploaded, parse-failed, schema-mismatch
- [ ] **Week 4:** Monday-morning CSV upload reminder email (system-prompted; trigger is human)
- [ ] **Week 4:** Phase 1a internal-acceptance demo against synthetic NB EMEA fixtures
- [x] Design partner committed (Brave Bison Agency, pilot: New Balance EMEA) — 2026-06-21

## Phase 1a → 1b handoff (not end-of-1a)

- [ ] Brave Bison's first product access at **Phase 1b Week 1** (per ADR-004) — against real New Balance EMEA CSV exports. Phase 1a weekly feedback rides on founder screen-share demos until then.

## Parallel track (non-blocking)

- [ ] File Meta + Google Ads + TikTok API approval applications per §5.1 (4–6 weeks lead time; ready for Phase 1b/1c API connectors)
- [x] Clerk account created, custom org roles `admin`/`account_manager` configured per §7.19
- [ ] Anthropic API key provisioned (not used until Week 4 / Phase 1b drift explanations)
- [ ] `app.mixsight.ai` DNS configured ahead of Phase 1c deployed-infra decision

## Active blockers

(none — Week 3 in progress; see Week 3 active blockers section above)

## Notes

- **Multi-market tension to resolve in Week 2-3 kickoff:** NB EMEA is multi-market; Phase 1a starts with one EMEA market (likely UK; confirm with Brave Bison AM). CSV pipeline ingests multi-market rows from day one; only the UI is constrained.
- **First impression discipline (per ADR-004):** Brave Bison sees nothing until Phase 1b Week 1 against real data. Weekly 30-min feedback calls happen anyway via screen-share.
- **CI not yet exercised on a remote.** `.github/workflows/ci.yml` exists; first push to GitHub will validate. Local-equivalent checks all green.
- **AuditLog FKs.** Neither `organization_id` nor `actor_user_id` on `audit_log` is a foreign key — the audit trail outlives the entities it audits (anonymization, hard-deletes). Stored as plain UUIDs.

## Out of scope for current phase (do not build, see SCOPE.md §7.20)

- AI plan parser (Phase 1b)
- Multi-market UI surfaces (Phase 1b) — CSV pipeline ingests multi-market rows but only one market visualizes in Phase 1a
- Mode B / cross-platform allocation (Phase 1b)
- API-based connectors for any platform (Phase 1b/1c — but file API approvals now per Parallel track above)
- Daily refresh cron (Phase 1c) — CSV uploads are weekly-cadence-by-design in Phase 1a
- Deployed infra / hosting provider decision (Phase 1c per ADR-004)
- White-label (Phase 1c)
- BYOK (Phase 1c)
- Billing (Phase 1c)
- Anything from Phase 2-5

Update this file at the end of every week and at every sub-phase boundary.
