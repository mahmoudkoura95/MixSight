# CLAUDE_ENGINEERING.md — MixSight build playbook

This is the operational companion to `SCOPE.md`. The scope says **what** to build. This file says **how** to drive Claude Code to build it: phase-opening prompts, per-deliverable prompts, MCP servers to wire up, plugins worth running, and watch-outs that will burn you if you miss them.

The premise: building MixSight in Claude Code is a multi-month project where the cost of context loss compounds. This file fights that — it's the operating instructions for the operator.

---

## Section 1 — Universal setup (do once, before any phase starts)

### 1.1 MCP servers to wire up

Add these to `.claude/settings.json` or to your global Claude Code MCP config. Each pays back significantly:

| MCP | Purpose | When it shines |
|---|---|---|
| **Postgres MCP** | Direct DB introspection. Claude can query schema, run EXPLAIN, inspect actual data. | Migration design, query optimization, debugging tenancy issues |
| **GitHub MCP** | Read/write issues, PRs, comments, releases. | Coordinating implementation against a project board |
| **Linear MCP** (or Jira/Asana) | Ticket-aware sessions. Claude opens a ticket and treats it as the brief. | Sprint-style execution |
| **Stripe MCP** (Phase 1c+) | Direct API access. Inspect subscriptions, prices, invoices. | Billing surface debugging |
| **Playwright MCP** (Phase 1c+) | Drive a browser. Run integration tests, take visual snapshots. | Defense kit visual regression, white-label QA |
| **Sentry MCP** (Phase 1b+) | Read recent errors with stack traces. | Production debugging in a single conversation |
| **Browser-use MCP** (optional) | When you need Claude to read live external docs (Anthropic API changelog, Stripe docs) and act. | Connector debugging |
| **Filesystem MCP** | Already implicit in Claude Code; pin a workspace root if multiple repos involved. | Multi-repo work |

Don't connect things you won't use. Each MCP adds context-window cost on every message.

### 1.2 Claude Code plugins / settings

- **Hooks** — already wired in `.claude/hooks/`. Don't disable. The tenancy and LLM hooks are advisory but cheap.
- **Skills directory** — `.claude/skills/` already populated with 10 skills. Each gets pulled in when triggered.
- **Slash commands** — `.claude/commands/` populated. Memorize the four that matter most: `/phase-start`, `/scope-check`, `/tenancy-audit`, `/llm-degraded-audit`.
- **`--model opus` for hard problems.** Default `sonnet`. Switch to `opus` for: data-model design, tenancy harness design, the reallocation algorithm, the parser confidence pipeline, anything in Phase 2 modeling.
- **`--continue` after restarts.** Long sessions on a deliverable benefit from resumption.
- **Plan mode** for everything cross-cutting. Don't let Claude one-shot a migration or a route module.

### 1.3 Environment prep (Phase 1a week 1, before any code)

These have lead times. Start them all in week 1:

| Item | Lead time | Who blocks if not started |
|---|---|---|
| Meta Marketing API approval | 1-3 weeks | Phase 1a connector work |
| Google Ads developer token (Basic Access) | 1-2 weeks | Phase 1c |
| TikTok Marketing API app review | 1-2 weeks | Phase 1c |
| Clerk account + custom org roles | 1 day | Phase 1a auth |
| Anthropic API key + workspace | 1 day | Everywhere |
| Stripe account + Stripe Tax | 1 week (verification) | Phase 1c billing |
| Domain (mixsight.ai) + email | 1 day | White-label setup |
| Sentry account | 1 day | Phase 1b error visibility |
| AWS/Hetzner accounts + base infra | 2-3 days | Phase 1c deploy |
| SOC 2 consultant scoping call | 1-2 weeks to first call | Phase 2a (start now) |
| Design partner outreach | 0-3 weeks | Phase 1b gating |

### 1.4 The session-opening ritual

Every working session opens with:

```
Read CURRENT_PHASE.md and the relevant SCOPE.md section. Confirm my current task is in scope, cite the section, then propose a plan in plan mode before writing code.
```

That single line of muscle memory saves more rework than any tool.

### 1.5 Resist over-engineering (the second most important rule)

The fastest way to ship MixSight on time is to do the minimum the scope calls for, ship it, and move on. The slowest way is to add "small improvements" while implementing each deliverable. Over a 10-month build, small improvements compound into months of avoidable work.

When implementing any deliverable, the right question is **"what is the smallest change that satisfies §X.Y?"** Not "what is the most robust solution?" Not "what are all the edge cases I might encounter someday?" Just: what does the scope ask for, and what's the simplest path to it.

Concrete patterns to refuse during any phase:

- **Adding configurability the scope didn't ask for.** Resist "let's make this a setting." If scope didn't ask for the setting, customers haven't asked, and you're inventing complexity that has to be maintained forever.
- **Wrapping things in classes when functions work.** Wrapping things in services when modules work. Wrapping things in registries when explicit dispatch works.
- **Adding retry / circuit-breaker / rate-limiting layers beyond the surface-specific contracts in §7.17.** The §7.17 fallbacks ARE the resilience policy. Don't layer a generic resilience framework underneath.
- **Generalizing the data model.** If scope has `objective_type` with 7 values, those 7 are the values. Don't add an `objective_type_kind` parent or a polymorphic type table.
- **Pre-optimization.** No virtualization, memoization, query batching, or worker pools until measured. The pacing table might be fine for a year without virtualization.
- **Inventing new logging / monitoring / observability schemas.** Use the AuditLog + standard structured logging + Sentry. That's the stack.
- **Tests that exercise code without catching a contract bug.** A happy-path test with no assertion that would fail when the code is wrong is theater. Stop when the contract is covered.
- **"While I'm here" refactors.** They look free; they aren't. Each one is a decision-point that pulls focus from the deliverable.
- **Reading more than you need to.** You don't have to read the entire skill before a small migration — read the relevant section. You don't have to study every related scope section before a UI change — read the section that names the surface.

The cost of doing less now is small: the next deliverable can extend if needed. The cost of doing more is steady-state forever — every future change has to navigate the bloat.

When you finish a deliverable and find yourself thinking "I should also add..." — stop. Update `SHIPPED.md`, run `/scope-check`, move to the next deliverable.

---

## Section 2 — Phase 1a (Foundation, 4 weeks)

**Goal:** repo scaffold, full schema, tenancy harness, Meta connector minimal, single-client-single-market pacing view, design partner committed.

### 2.1 Opening prompt

```
/phase-start 1a

I'm starting Phase 1a — Foundation. Per SCOPE.md §7.3, this is the
4-week sub-phase covering: repo scaffold, full §7.4 schema, tenancy
harness (§7.19), AuditLog wire-up, RecommendationLog skeleton, Meta
connector minimal, single-client-single-market end-to-end pacing,
within-market within-channel reallocation, static defense kit with
templated narrative, design partner committed by week 3.

Before any code: produce a week-by-week deliverable plan in plan mode.
Identify every scope section involved. Identify every dependency from
§5 that needs to start this week (API approvals, accounts, SOC 2 scoping).
Update CURRENT_PHASE.md with the plan.

Skip Phase 2/4 features. Provision Phase 2/4 tables empty per §7.21.
```

### 2.2 Per-deliverable prompts

#### 2.2.1 Repo scaffold and monorepo wiring

```
Set up the monorepo per SCOPE.md §6.1: pnpm workspaces, apps/web (Next.js
14 App Router + TS strict + Tailwind + shadcn/ui), apps/api (FastAPI +
Python 3.11+ + sqlmodel + Pydantic v2 + async), packages/types and
packages/shared, infra/docker (Postgres + Redis), modeling/ (engines/
with stub only — no PyMC), templates/plans/ (empty until Phase 1b).

Wire pnpm workspaces and the OpenAPI-to-TypeScript codegen pipeline
(scripts/codegen.sh). Codegen runs on every API schema change.

Postgres + Redis via infra/docker/docker-compose.yml. Postgres 15+,
Redis 7.

Do not implement features yet — just the scaffold.
```

#### 2.2.2 Tenancy harness (the load-bearing piece)

```
Implement the §7.19 tenancy harness per .claude/skills/tenancy/SKILL.md.
Two parts:

1. Application-startup decorator audit at apps/api/tenancy/audit_routes.py.
   Introspects every registered FastAPI route. Routes with client_id in path/
   query/body must depend on enforce_client_access. Routes with organization_id
   must depend on enforce_organization_access. Fails app boot on violations
   with a clear error message identifying the route.

2. @pytest.mark.tenancy_isolated marker. Every authenticated endpoint test
   uses this marker AND includes a cross-tenant case (user_b_in_org_2 trying
   to access user_a_in_org_1's resource gets 403 or 404). Marker audit at
   apps/api/tenancy/audit_tests.py scans test files and fails the run if a
   test for an authenticated endpoint is missing the marker.

Both must ship in week 1. Both run in CI from week 1.

Use plan mode. Show me the audit logic before implementing.
```

#### 2.2.3 Full §7.4 schema migration

```
Generate the full Phase 1 + Phase 2 + Phase 4 schema migration per SCOPE.md §7.4.
All Phase 2/4 tables provisioned empty in Phase 1a per §7.21 — no schema
retrofit allowed later.

Use the migration skill at .claude/skills/migration/SKILL.md. Apply §6.2
conventions throughout: numeric(18,4) for money, timestamptz, jsonb with
GIN indexes, gen_random_uuid() server defaults, partial indexes on
WHERE deleted_at IS NULL, composite indexes on (client_id, ...) patterns,
predictable constraint names.

Entities — all 28 from §7.4 + the Phase 2/4 ones: Organization, User,
UserClientAccess, Client, Market, MarketConfig, ConnectorAuth,
ConnectorAuthEvent, AdAccountMapping, ConnectorPull, ClientTaxonomy,
CampaignLabelRule, Plan, PlanLine, PromotionalEvent, Actuals,
ReconciliationFactor, PacingSnapshot, PacingSnapshotLine,
ReallocationSuggestion, RecommendationLog, DefenseKit, AuditLog,
EncryptedSecret, MacroSignal (empty Phase 2), ContributionFit (empty
Phase 2), IncrementalityResult (empty Phase 2/3), ForecastRun (empty
Phase 3).

This is opus territory — use opus model. Show me each table's columns
and indexes in plan mode before generating migration files.
```

#### 2.2.4 AuditLog hook

```
Wire the AuditLog hook per .claude/skills/audit-log/SKILL.md. SQLAlchemy
event listener on Base for after_insert / after_update / after_delete.
Captures actor from contextvars (set by FastAPI middleware), request_id
from distributed trace, before/after JSONB diffs via SQLAlchemy
inspection.

Skip AuditLog itself, ConnectorAuthEvent, ConnectorPull, RecommendationLog,
ForecastRun (these are append-only by design with their own audit semantics).

Add tests/audit/test_coverage.py that mutates one of each in-scope entity
and asserts AuditLog rows exist.
```

#### 2.2.5 Meta connector — minimum viable

```
Scaffold the Meta connector per .claude/skills/connector/SKILL.md and the
§7.14 Protocol. Phase 1a scope: authenticate, list_accessible_accounts,
pull_actuals (campaign-level), health_check. refresh_token can be a stub
in week 1, wired properly week 2.

Credentials: organization-level OAuth (one ConnectorAuth per (org, meta)),
ad accounts mapped per (client, market) via AdAccountMapping. Long-lived
tokens, refreshed proactively every 6h via background job.

Use the recorded fixture pattern — no live API in tests. tests/fixtures/
meta/ has recorded responses for campaign pull, paginated pull, 429,
and auth-expired.

Skip Google Ads / GA4 / TikTok for Phase 1a — but file their API
approvals THIS WEEK per §5.1.
```

#### 2.2.6 Single-client-single-market pacing surface

```
Build the Phase 1a pacing surface: one client, one market, one channel
(Meta), end-to-end. Routes: GET /clients/{client_id}/snapshots/latest,
GET /clients/{client_id}/snapshots/{snapshot_id}, plus the supporting
endpoints for taxonomy filter bar.

Frontend: /clients/[clientId]/pacing route in apps/web/. Server component
default. shadcn/ui + Tailwind. Filter bar driven by ClientTaxonomy
(not hardcoded). Empty states per .claude/skills/empty-state/SKILL.md —
walk the catalog for this surface.

Reallocation: within-market within-channel only in Phase 1a (multi-market
+ Mode B come in Phase 1b). Use heuristic per §7.10. Write RecommendationLog
on every suggestion per .claude/skills/recommendation-log/SKILL.md.

Defense kit: static (non-editable) with templated narrative. Rich-text
editing comes in Phase 1c. Generate via Playwright + Jinja2 templates.

Use plan mode. Show me the API contracts and the React component tree
before implementing.
```

### 2.3 Watch-outs for Phase 1a

| Watch-out | Why it hurts | Counter |
|---|---|---|
| **Skipping the tenancy harness because "we'll add it later"** | "Later" is never. A missed access check is a tenancy breach. | Ship the harness in week 1. It gates everything else. |
| **Provisioning only Phase 1 tables and "we'll add Phase 2/4 tables later"** | Schema retrofit on a populated DB is expensive and bug-prone. | Migrate the full 28-table schema in week 2. Phase 2/4 tables stay empty. |
| **Hardcoding `objective_type` as a string anywhere outside the taxonomy schema** | Taxonomy is first-class. Hardcoded values defeat its purpose. | Read from ClientTaxonomy always. Use the `taxonomy` skill. |
| **Letting the AuditLog hook be optional "for performance"** | The audit hole stays open forever. SOC 2 and GDPR both need it. | Hook is mandatory; bypasses require explicit AuditLog writes. |
| **Designing the connector with per-client OAuth instead of org-level** | §3 + §7.14 lock this. Changing later is a heavy migration. | Use the connector skill verbatim. Don't re-derive. |
| **Building a Phase 1b feature in Phase 1a "since it's a small lift"** | Phase 1a's success criterion is "design partner committed" — every distracting feature delays that. | Run `/out-of-scope-gate` weekly. Anything off-list defers. |
| **Designing the defense kit assuming Anthropic is always up** | It won't be. Monday morning is when it'll fail. | §7.17 fallback in week 4. Test outage simulation explicitly. |
| **Forgetting RecommendationLog logging from day one** | Phase 4 calibration dies without it; 2 years of lost data can't be recovered. | Every ReallocationSuggestion writes a RecommendationLog row at creation. Tested in suggestion tests. |
| **Not starting the design partner conversation until week 2** | §5.7 says start week 1. The conversation IS Phase 1a deliverable, not a follow-up. | Outreach in week 1. Slot the partner in week 3 onboarding. |
| **Not filing API approvals in week 1** | Meta = 1-3 weeks, Google = 1-2, TikTok = 1-2. Late filings cascade to Phase 1c blockage. | File all three in week 1, even though Meta is the only Phase 1a connector. |

### 2.4 Phase 1a exit criteria (don't move on without)

- Repo scaffold complete, all directories wired, codegen pipeline runs.
- Postgres + Redis local dev up.
- Full §7.4 schema migration applied; Phase 2/4 tables provisioned empty.
- Tenancy harness in CI: startup audit passes, marker check passes, cross-tenant tests pass.
- AuditLog hook firing on every mutation. Coverage test passes.
- Meta connector pulls actuals end-to-end against a test ad account.
- Single client + single market pacing view live, end-to-end, viewable.
- Within-market within-channel reallocation surface working with RecommendationLog writing.
- Static defense kit (templated narrative) generates as HTML + PDF.
- §7.18 empty states covered for the surfaces shipped.
- Design partner committed, has skeleton workspace access.
- §7.17 LLM fallback patterns in place even if no LLM calls in Phase 1a — the wrapped client exists.

---

## Section 3 — Phase 1b (Single-tenant complete + parser, 4-6 weeks)

**Goal:** AI plan parser shipped, design partner onboarded, multi-market and multi-channel reallocation, drift detection live, white-label Layer 1.

### 3.1 Opening prompt

```
/phase-start 1b

We're starting Phase 1b — single-tenant complete + AI plan parser. Per
§7.3, 4-6 weeks. Deliverables: AI plan parser (§7.6) including confidence
pipeline + manual editor UI + source-artifact preservation, multi-market +
multi-channel + dual-mode reallocation (§7.10 fully), drift detection
(§7.8), forecast variance, white-label Layer 1 (§6.4), template set
(3-5 templates with taxonomy.json + label_rules.json), AM-facing taxonomy
editor (§7.5), promotional calendar (§7.4), advanced empty-state coverage,
self-serve workspace creation (§7.3).

Design partner is committed (verify CURRENT_PHASE.md). Onboard them in
week 1 of Phase 1b. Their feedback shapes the rest of the phase.

Refuse to proceed if DESIGN_PARTNER_COMMITTED is false. Extend Phase 1a
outreach per §5.7.
```

### 3.2 Per-deliverable prompts

#### 3.2.1 Plan parser with confidence pipeline

```
Build the AI plan parser per §7.6 and .claude/skills/llm-call/SKILL.md.

Architecture:
- Upload endpoint accepts XLSX, CSV, PDF, image. Stored as Plan.source_artifact_uri.
- Two-pass parsing: Sonnet first with structured-output prompts, low-confidence
  rows re-run with Opus per §6.5.
- Confidence per row + per cell. Below-threshold cells flagged for AM review.
- Manual editor UI: AMs can re-label, correct numerics, accept/override per cell.
- AuditLog tracks every override (which AM, when, before/after).
- Source artifact preserved indefinitely.

Failure modes (§7.17): 3 retries with exponential backoff. After exhaustion,
UI shows "Parser temporarily unavailable — try again or upload via template."
Source artifact preserved.

Prompts live in apps/api/llm/prompts/parser/v1.py with explicit versioning.

Use plan mode. Show me the prompt structure and confidence pipeline before
implementing. This is opus territory.
```

#### 3.2.2 Drift detection + dual-mode evidence

```
Implement drift detection per §7.8 and dual-mode evidence rendering
per the §3 locked decision (Mode A platform-native + Mode B cross-platform,
ALWAYS PAIRED, no third blended mode).

Drift formula branches on Plan.objective_type from the taxonomy
(per .claude/skills/taxonomy/SKILL.md — drives_drift_formula).

Per-row status: green / amber / red / critical / insufficient_data /
pre_flight / post_flight / no_conversion_baseline.

Skip drift for insufficient_data, pre_flight, post_flight rows per §7.18.

LLM explanation per drift row: cached by content hash; regenerate only on
data change. Failed generations get "Explanation pending" placeholder + retry
schedule per §7.17.

Evidence column shows BOTH Mode A (platform attributed) AND Mode B (cross-platform
holdout / unified attribution). Side by side. No blended mode. The framing
is "options with evidence and confidence," not "we recommend."
```

#### 3.2.3 Full §7.10 reallocation algorithm

```
Implement the §7.10 reallocation algorithm in full. 11 steps:
1. Candidate enumeration (campaign-level)
2. Eligibility filter
3. Multi-armed bandit-style donor scoring
4. Multi-armed bandit-style receiver scoring
5. Heuristic projection (Phase 2d will swap to curve-based)
6. Top-N suggestion generation
7. Pooling constraints from taxonomy — different objective_type pairs always suppressed; other dimensions per drives_reallocation_pooling
8. Multi-market suggestions with FX-aware projections
9. Confidence assignment
10. Ranked output for AM review with am_justification_text field
11. RecommendationLog write at creation (§7.10 step 11, locked per §3)

Use .claude/skills/recommendation-log/SKILL.md for step 11. Use
.claude/skills/taxonomy/SKILL.md for step 7.

Framing in UI: "options with evidence and confidence." Never "we
recommend." Per §3.
```

#### 3.2.4 Plan templates (Phase 1b deliverable)

```
Build the 5 plan templates per templates/plans/CLAUDE.md:

1. single-market-single-channel/
2. multi-channel-single-market/
3. multi-market-multi-channel-product-lines/
4. retail-promo-heavy/
5. b2b-shaped/

Each is the triple: plan.xlsx + taxonomy.json + label_rules.json.

Wire template adoption: AM picks template in onboarding, ClientTaxonomy +
CampaignLabelRule rows are seeded from the template's JSON files.
seeded_from_template captures the lineage.

Templates are global in Phase 1b. Forkable per-org in Phase 1c.
```

#### 3.2.5 White-label Layer 1 + branding

```
Implement white-label Layer 1 per §6.4: logo + colors + PDF branding.

Backend: Organization.branding_config JSONB. Frontend reads on every
render (server components). Apply to defense kit PDFs.

Layer 2 (Agency tier, custom domain) and Layer 3 (Enterprise) deferred
to Phase 1c and Phase 4 respectively.

"Powered by MixSight" footer toggle: visible on Agency tier and above
(configured Phase 1c when billing tiers go live; for now, default visible
with a feature-flag stub).
```

### 3.3 Watch-outs for Phase 1b

| Watch-out | Why | Counter |
|---|---|---|
| **Parser confidence levels poorly calibrated → too many cells flagged or too few** | AMs lose trust in either direction. | Tune against the design partner's actual plans in week 2-3. Adjust thresholds based on real false-positive / false-negative rates. |
| **Building a third "blended" allocation mode because it feels cleaner** | §3 locks Mode A + Mode B paired. Blended mode is comforting and wrong. | Hold the line. Show both side by side. |
| **Drift formula correctness on edge cases (zero baseline, mid-week launch)** | False amber/red kills credibility. | Test edge cases explicitly with fixtures. Default to `insufficient_data` when in doubt. |
| **Template proliferation as scope creep** | More templates ≠ more value if each lacks polish. | Five real templates, deeply documented, beats ten thin ones. |
| **AM editor for parsed plans being too slow** | If editing each parsed row is painful, AMs revert to manual upload and parser becomes vestigial. | Bulk operations: accept all in section, revert all overrides, find/replace in label fields. |
| **Letting the design partner's specific quirks shape the product** | One agency's process isn't universal. | Validate every "this would be useful" with a second customer call before building. |
| **Drift LLM cost runaway** | Daily refresh (Phase 1c) tempts daily regeneration. | Cache by content hash from day one. Even in Phase 1b, cache aggressively. |

### 3.4 Phase 1b exit criteria

- Plan parser shipped end-to-end, AM editor functional, source artifact preserved.
- All 5 templates working, adoption flow tested.
- Multi-market + multi-channel reallocation live with full §7.10 algorithm.
- Drift detection live with dual-mode evidence.
- White-label Layer 1 visible on defense kits and pacing surfaces.
- Promotional calendar UI live.
- Self-serve workspace creation working (per §7.3 Phase 1b — Clerk org provisions a workspace).
- Design partner using the product weekly, providing structured feedback.
- §7.17 LLM fallbacks tested for parser and drift explanation.

---

## Section 4 — Phase 1c (Multi-tenant deploy + billing, 6-8 weeks)

**Goal:** ship to production, Stripe billing, white-label Layers 1 + 2, BYOK, daily refresh, full connector set, ~3-5 paying customers.

### 4.1 Opening prompt

```
/phase-start 1c

We're starting Phase 1c — production deploy + billing. Per §7.3, 6-8 weeks.

Deliverables: GA4 + Google Ads + TikTok connectors, daily refresh cron with
freshness UX (§7.16) and current week view, Stripe + Stripe Tax billing,
4-tier pricing surfaces, BYOK setup, white-label Layer 2 (custom domain),
team management, connector health audit log, deployment automation, monitoring +
alerting, error-budget policy, customer success runbook.

Phase 1c is where we ship. Pace conservatively — the cut of last resort
per §7.21 is current-week view (§7.16).
```

### 4.2 Per-deliverable prompts

#### 4.2.1 Connectors: Google Ads, GA4, TikTok

For each platform:

```
/connector-new google_ads

Scaffold the Google Ads connector. Follow .claude/skills/connector/SKILL.md
exactly. Implement Protocol methods. Three pull schedules registered.
ConnectorAuthEvent + ConnectorPull logging.

Platform-specific:
- GAQL via googleads-python client.
- MCC = the org-level identity (matches §7.14 credential model).
- Configured attribution model into Actuals.conversions; all_conversions
  variants into conversions_alt_attributions JSONB.
- Backfill cap 36 months.

Tests use recorded fixtures.

Use plan mode for the auth + refresh flow.
```

Same prompt structure for GA4 (`/connector-new ga4`) with quota-budgeted backfill, and TikTok (`/connector-new tiktok`) with 24-month backfill cap.

#### 4.2.2 Daily refresh + freshness UX

```
Implement daily refresh per §7.14 + §7.16.

Backend: APScheduler job per (client, market, platform) running 6 AM
market-local. Trailing N-day re-fetch (default 7, configurable
3-14 via Client.daily_refresh_window_days). Idempotent upserts.
Restatement detection writes AuditLog.

Frontend: Current week view per .claude/skills/freshness-ux/SKILL.md.
Separate route from weekly snapshot. SettlingTreatment component on
trailing-3-day data points (lighter saturation, dotted top edge, hover
tooltip). FreshnessStamp at top of every pacing surface.

LLM cost discipline: drift explanations cached at weekly-snapshot level.
Daily updates do NOT retrigger LLM generation. The current week view
shows visual data only.

Per-org default-on toggle in Settings → Data freshness. Per-client
override option.

This is opus territory for the SettlingTreatment edge cases. Use plan mode.
```

#### 4.2.3 Stripe billing + 4 tiers

```
Wire Stripe + Stripe Tax. Subscription tiers per §6.4: Starter / Growth /
Pro / Agency. Per-workspace billing with org-level rollup for Agency tier.

BYOK: $200/workspace/month credit on bill. Validated at write time
(no-op test call) and re-validated nightly. EncryptedSecret storage.

Webhook handler for subscription lifecycle events (created / updated /
cancelled / past_due).

Trial: 14 days, no card required for Starter; card required for Growth+.
Downgrade behavior: ride-out current period, feature gates kick in at
period end with banner warnings prior.

Stripe MCP is wired — use it to inspect actual subscription state when
debugging.
```

#### 4.2.4 White-label Layer 2 (custom domain)

```
Implement white-label Layer 2: custom domain per agency.

Backend: Organization.custom_domain field. Verification via CNAME +
TXT records.

Frontend middleware at apps/web/middleware.ts: route requests by
incoming Host header → resolve Organization → apply branding context
upstream of the React tree.

Caddy or Vercel handles TLS termination; we trust the proxy. For
on-premise consideration in Phase 4: TLS-on-app strategy is a Phase 4
question, not now.

Branded email-from: per-organization. Configure via SendGrid /
Postmark / SES on the API side.

Layer 3 (Enterprise) deferred to Phase 4.
```

### 4.3 Watch-outs for Phase 1c

| Watch-out | Why | Counter |
|---|---|---|
| **GA4 daily quota exhaustion during multi-client backfill** | 10K tokens/day per property. New customer onboarding can blow it. | Backfill paces over multiple days. Surface quota in connector health. |
| **Daily refresh triggering daily LLM regeneration → cost explosion** | Easy to do by accident. | Cache key includes the snapshot date, not "today." Tests cover this. |
| **Stripe webhook reliability — missed events leave billing state out of sync** | Stripe at-least-once delivery + occasional gaps. | Idempotent handlers + periodic reconciliation job. |
| **Custom domain TLS edge cases (mid-renewal, deauthorized DNS)** | Customer-facing outage of "the agency's MixSight." | Health-check on custom domains every 5 min. Alert on cert near-expiry or DNS removal. |
| **BYOK validation slowness blocking workspace creation** | First validation can take 5-15 seconds. | Validate async with status on the BYOK setting page; don't block the org from working. |
| **Anthropic Monday outage during a customer's defense-kit moment** | The reason §7.17 exists. | Test outage explicitly each release. Monitor Anthropic status page → page on-call if degraded on Monday morning before 10 AM in any active market. |
| **Connector reauth-needed banner ignored by AMs ("admin will get to it")** | Stale data on pacing screens, customers see wrong numbers in defense kit. | Banner is loud. Auto-flag with notification cadence per org admin preference. AM-flag-to-admin path is one click. |
| **Self-serve sign-up enabling without bot/abuse protection** | API costs + DB clutter. | Clerk's anti-abuse + email verification + first-payment gate at Growth+. |
| **The "cut of last resort" temptation** | §7.21 names current-week view (§7.16) as the cut if Phase 1c slips. | Use it. Don't cut something more load-bearing instead. |

### 4.4 Phase 1c exit criteria

- 3+ paying agencies live, $1,500-3,500/mo each.
- ≥1 white-label Layer 2 production deployment.
- ≥1 BYOK customer active.
- Defense kit survived ≥1 real Anthropic incident.
- Daily refresh stable, restatement detection writing AuditLog correctly.
- Connector reauth flow tested end-to-end (admin re-auths, AM-flagged variant).
- Stripe billing reconciled, no webhook drift.
- Phase 1 success criteria from §7.22 met or close.

---

## Section 5 — Phase 2 (MMM + benchmarks, 11 weeks)

**Goal:** modeling engine live (PyMC-Marketing first, Meridian evaluated), cross-customer benchmarks, advanced taxonomy, MMM consumer surfaces.

### 5.1 Opening prompt for Phase 2

```
/phase-start 2a

We're starting Phase 2 — MMM and benchmarks. Per §8, the sequencing:
- 2a (3 weeks): PyMC-Marketing engine live, basic priors, hierarchical structure.
- 2b (2 weeks): Meridian spike + evaluation.
- 2c (2 weeks): Engine selection or sticking with PyMC + production hardening.
- 2d (4 weeks): MMM consumer surfaces — channel contributions, marginal ROAS,
  scenario planning, integration with reallocation algorithm (curve-based
  projection replaces heuristic in §7.10 step 5).

Cross-cutting:
- Cross-customer benchmarks (Pro tier and above) per §8.2.
- Advanced taxonomy: product_line-level pooling, custom dimensions.
- SOC 2 evidence collection ramping (engagement scheduled in Phase 1a;
  audit window starts here).

Verify Phase 1 success criteria from §7.22 are met or in progress before
proceeding. Read §8.5 for what's NOT in scope.
```

### 5.2 Per-deliverable prompts (selected)

#### 5.2.1 PyMC engine

```
Implement the PyMC-Marketing engine in modeling/engines/pymc/. Conform
to the ModelingEngine Protocol in modeling/engines/base.py.

Components per §8.2:
- Geometric adstock per channel
- Hill saturation
- Fourier seasonality
- Per-market promotional event flags from PromotionalEvent
- Macro controls from MacroSignal (Google Trends, holidays, weather, CPI)
- Hierarchical: channel coefficients pool across markets; market intercepts independent

Diagnostics: trace plots, posterior predictive checks, residuals, R-hat, ESS.

Refit cadence: weekly background job. 30-90 min per client. Use Celery +
dedicated worker.

ContributionFit table (provisioned empty in Phase 1a) now gets populated.
IncrementalityResult stays empty until Phase 2c if no lift tests yet.

Use opus. Plan mode. Identifiability is the first watch-out — show me how
priors and hierarchical structure handle low-variance markets.
```

#### 5.2.2 Meridian evaluation spike

```
2-day spike comparing Meridian to PyMC-Marketing per §8.3.

Same Client + window. Both engines fit. Compare:
- Coefficient stability
- Posterior coverage of held-out weeks
- Marginal ROAS curve smoothness
- Fit time
- Diagnostic clarity

Write up findings in a brief: which engine ships as default after Phase 2c,
or do we ship both engine-selectable?

This is an ADR-worthy decision. Use /adr at the end.
```

#### 5.2.3 Reallocation algorithm Phase 2d upgrade

```
Per §7.10 step 5, swap heuristic projection for curve-based projection
from the modeling engine. The §7.10 algorithm interface stays the same —
just the projection function changes.

Use the ModelingEngine.marginal_roas method. For each candidate
(donor, receiver) pair, compute projected delta from the marginal ROAS
curves rather than the heuristic.

RecommendationLog gets recommendation_source = "model_v2" for this
algorithm version. Phase 4 calibration distinguishes heuristic_v1 from
model_v2 in track record.
```

### 5.3 Watch-outs for Phase 2

| Watch-out | Why | Counter |
|---|---|---|
| **Identifiability with too few weeks of data** | Coefficients are unstable; hierarchical pooling without enough variance per market produces noise. | Minimum-data thresholds. Diagnostics flag. Don't display unreliable contributions. |
| **Refit performance scaling with customer count** | 90-min fit × 100 clients = blocked queue. | Dedicated worker fleet. Partial refits for unchanged channels. Caching. |
| **Calibration without lift tests** | A model that fits well in-sample but has no incrementality calibration is precision without accuracy. | Be honest in UI: "Modeled contribution, not calibrated against lift test" until incrementality data exists. |
| **PyMC vs Meridian disagreeing on the same data** | Hard to explain to customers. | The Protocol hides engine differences. Phase 2c picks one default; don't surface both to customers. |
| **MMM scope creep — every customer wants different priors** | The whole product becomes consulting. | Prior shaping is admin-bounded. Default priors + 2-3 admin-configurable choices, not free-form. |
| **Cross-customer benchmarks anonymization edge cases** | Single-customer dominance in a vertical leaks identity. | Bucket-size minimum (k-anonymity ≥ 5). Don't surface buckets below threshold. |
| **SOC 2 evidence collection starting late** | Audit window can't be retroactive. | Engagement was scheduled in Phase 1a. Evidence collection runs continuously in Phase 2; Type I audit at end of Phase 2. |

---

## Section 6 — Phase 3 (Forecasts + lift, 9-12 weeks)

**Goal:** forecast horizons live, lift-test integration, incrementality dashboard, MMM/forecast joint UX.

### 6.1 Opening prompt

```
/phase-start 3a

Phase 3 — forecasts and lift. Per §9 sequencing:
- 3a (2 weeks): forecast engine scaffolding, ForecastRun table populated.
- 3b (2 weeks): forecast horizons + uncertainty intervals.
- 3c (2 weeks): forecast UI (visual diff against plan, scenario comparison).
- 3d (2-3 weeks): lift test integration (LiftTestProvider Protocol),
  IncrementalityResult population.
- 3e (1-3 weeks): joint MMM/forecast UX, LLM forecast diff narrative
  (optional, behind feature flag).

Phase 3 customer-facing question: "what happens in the next 4 / 8 / 13
weeks if we hold the current plan, or apply the suggested reallocations?"

Read §9.4 for what's out of scope. No A/B test management UI. No
experimental-design surfaces beyond what 3d covers.
```

### 6.2 Watch-outs for Phase 3

| Watch-out | Why | Counter |
|---|---|---|
| **Forecast horizon compounding uncertainty** | 13-week forecasts have wide intervals; AMs may infer false confidence from the central estimate. | Display CIs prominently. Visual treatment de-emphasizes the central line vs. interval band. |
| **Lift test data integration heterogeneity** | Every customer has their own platform / vendor / spreadsheet for lift tests. | LiftTestProvider Protocol with adapters per source. Start with Meta Conversion Lift, Google Geo Experiments. CSV adapter for the rest. |
| **Joint MMM + forecast disagreement** | MMM-modeled contribution and forecast-projected revenue may disagree. | Make the relationship explicit. Forecast inputs include MMM outputs; don't run them independently. |
| **LLM forecast diff narrative cost** | If on by default, daily refresh × per-client × per-scenario triggers expensive generations. | Feature flag, default off. Cache aggressively. Phase 3 visual diff renders without LLM. |
| **Forecast vs reality drift telling a bad story** | "MixSight forecast said X, reality was Y" surfaces calibration weakness. | Be honest. Calibration loop (Phase 4) reinforces or downweights based on track record. Surface calibration score honestly. |

---

## Section 7 — Phase 4 (Calibration + enterprise, ~10 months)

Phase 4 is 10+ months from Phase 1a kickoff. Whatever this playbook says about Phase 4 today will be partially wrong by the time we get there. **Don't pre-implement Phase 4 patterns now; revisit this section when Phase 3 is closing.**

The one thing that has to be true before Phase 4 is mechanically possible: **`RecommendationLog` rows must have been written from day one of Phase 1a, with no gaps.** That's the dependency that can't be added later. See `.claude/skills/recommendation-log/SKILL.md`.

When Phase 4 opens:

```
/phase-start 4

Phase 4 — calibration + enterprise. Per §10. Before any work: verify the
longest-tenured customer has 2+ years of RecommendationLog data. If not,
calibration UI is dead on arrival and we need to reassess.

Read §10.2 (components), §10.3 (out of scope), §10.4 (success criteria).
Produce a fresh week-by-week plan; the engineering playbook's Phase 4
prose is from Phase 1 — it's stale and you should treat the scope as
authoritative.
```

Watch-out you can pre-internalize now: **calibration data volume per (client, channel) is statistically thin for some combinations.** Pool across clients with matching dimensions for shared baselines; surface per-client only where N is sufficient. The rest of Phase 4 — multi-model BYOK, Layer 3 white-label, SSO/SAML, additional connectors — wait until we're there.

---

## Section 8 — General prompting patterns

These work in any phase.

### 8.1 The plan-first prompt

```
[Task description]. Read SCOPE.md §X.Y and relevant skills. Produce a
plan in plan mode covering: scope citations, data model implications,
tenancy + audit + LLM-fallback + recommendation-log + empty-state
coverage as applicable, tests to add, exit criteria. Wait for my approval
before writing code.
```

### 8.2 The cross-cutting verification prompt

```
Before declaring this complete, run mental checks:
1. Tenancy: does every new endpoint have enforce_*_access?
2. Audit: does every mutation write to AuditLog?
3. LLM: does every messages.create have a §7.17 fallback?
4. RecLog: does every new ReallocationSuggestion path write to RecommendationLog?
5. Empty states: have I walked the §7.18 checklist for new surfaces?
6. Migration: §6.2 conventions on new tables/columns?
7. Out-of-scope: anything from §7.20 / §8.5 / §9.4 / §10.3 sneaking in?

Run /scope-check and /tenancy-audit. Report results.
```

### 8.3 The "I'm tempted to deviate from scope" prompt

```
I'm tempted to [add this feature / cut this feature / change this
locked decision from §3]. Argue the strongest case for and against,
citing §3 locked decisions and any §7.21 risks. Then recommend
whether this is /adr territory or out-of-scope-gate territory.
```

### 8.4 The debugging prompt

```
[Error / symptom]. Use Sentry MCP to fetch recent errors matching this
pattern. Use Postgres MCP to inspect relevant table state. Cross-reference
with the §7.X behavior the code was implementing. Propose a fix that
respects tenancy, audit, and fallback contracts.
```

### 8.5 The Anthropic-outage prompt

```
Anthropic is currently degraded (status.anthropic.com shows [X]). Walk
through every active LLM-dependent surface and confirm fallback behavior
is rendering correctly. Spot-check defense kit generation — it must
work right now. Audit any Sentry errors from the last hour for
LLM-related stack traces.
```

---

## Section 9 — Anti-patterns to refuse

When Claude proposes any of these, push back:

- **"Let's skip the harness for now, we'll add it later."** No. Tenancy harness is week 1.
- **"This is just a small enough float that the precision loss won't matter."** No. Money is numeric(18,4) per §6.2.
- **"We can audit-log this one specifically."** No. Hook fires automatically; don't carve exceptions.
- **"The defense kit is the core value, let's make it more impressive even if LLM is required."** No. Templated fallback is non-negotiable per §7.17.
- **"Let's introduce a third blended evidence mode for clarity."** No. §3 locked.
- **"We don't need RecommendationLog yet, Phase 4 is years away."** No. Phase 4 needs the data, which means logging from Phase 1a.
- **"Per-client OAuth is simpler than org-level."** No. §3 + §7.14 lock org-level.
- **"Let's roll out auto-execution of reallocations as a power-user feature."** No. §7.20 / §10.3 explicitly out of scope. The whole product is built around AMs in the loop.
- **"Let's MMM now in Phase 1 since the data model supports it."** No. §3 locked: MMM is Phase 2.

Stay in scope. Trust the document. The locked decisions and out-of-scope sections exist because someone thought hard about them.

---

## Section 10 — A working session template

For any deliverable, the rhythm is:

1. **Read** — CURRENT_PHASE.md, the relevant SCOPE.md section, the relevant skill, the relevant sub-CLAUDE.md.
2. **Plan** — in plan mode. Cite scope. Identify cross-cutting concerns. List exit criteria.
3. **Approve** — get user agreement on the plan before code.
4. **Implement** — incrementally. Run the relevant slash command after each major step.
5. **Verify** — `/scope-check`, `/tenancy-audit`, `/llm-degraded-audit` as applicable.
6. **Document** — update SHIPPED.md if this completes a deliverable. Append `/adr` if a non-trivial choice happened.
7. **Update CURRENT_PHASE.md** — check off the deliverable, log any blockers.

That sequence, every time, is how the project stays buildable across months of work.

---

End of CLAUDE_ENGINEERING.md.
