# MixSight — Claude Code Operating Manual

This file is navigational, not encyclopedic. The canonical source of truth is `SCOPE.md`. Always cite a scope section number when proposing work.

---

## The single most important rule

**Do the minimum the scope section calls for, and stop.**

The scope is detailed because it was thought through. If something isn't asked for, it's because we don't want it yet. "While I'm here, I'll also add..." is the most expensive sentence in software.

When in doubt: fewer files, less abstraction, less configuration, smaller diffs.

### Over-engineering patterns to actively resist

- **Speculative configuration.** If scope says "default 7, configurable 3-14," ship that. Don't add a knob for the upper bound. Don't add an env var the scope doesn't ask for.
- **Speculative abstraction.** The §7.14 Connector Protocol has five methods. Don't add a sixth. The §6.3 role model has two roles. Don't add a third for flexibility. If you find yourself naming a new abstraction, check whether scope already names the thing.
- **Speculative resilience.** Caching, batching, queueing, custom retry policies — add when scope calls for them or measurement justifies them. The §7.17 surface-specific fallbacks ARE the resilience policy. Don't layer a second one underneath.
- **Test carpet-bombing.** Write the test that proves the contract: tenancy needs the cross-tenant case, AuditLog needs the coverage test, money needs the rounding test, defense kit needs the LLM-outage test. Most other unit tests duplicate what integration tests already prove. Stop when the contract is covered.
- **Defensive code for impossible cases.** `if foo is None` when `foo` can't be None is noise.
- **Premature performance work.** No virtualization, memoization, query batching, or worker pools until measured. The pacing table might be fine without virtualization for a long time.
- **"While I'm here" refactors.** Don't.
- **Inventing patterns not in scope** (a small DSL for X, a config schema for Y, a registry for Z). If scope doesn't name the thing, the thing probably doesn't need to exist yet.

### Skills and code examples are illustrative

The skills in `.claude/skills/` contain code patterns. They are **starting points**, not templates to paste. Adapt the pattern to your case; drop the parts that don't apply. The cited scope sections are the authoritative source — when a skill's code and the scope disagree, the scope wins. If a simpler form fits, use it.

### The always/never lists below

They are correctness guard rails. They prevent specific bug classes that retrofit expensively. Following them costs nearly nothing if you're writing straightforward code. If satisfying a rule requires new wrapper layers, you went sideways — stop and reconsider.

### When tempted to add something the scope doesn't call for

Write the smaller version first. Ship it. Ask whether more is needed. Usually it isn't.

---

## Current state

Read `CURRENT_PHASE.md` at the start of every session. Constrain proposals to the active phase. If a request would ship something from a later phase, say so before writing code.

---

## How to work in this repo

1. **Open every prompt with a scope citation.** "We're in Phase 1a per §7.3, implementing §7.4 ClientTaxonomy migration." No citation, no work.
2. **Use plan mode for anything cross-cutting.** Data model, tenancy, audit log, LLM calls, connector lifecycle. Self-contained UI work doesn't need it.
3. **Reach for skills before improvising.** See `.claude/skills/`. The skill is where the pattern lives; the cited scope section is the authoritative source.
4. **Run the slash commands as rituals.** `/phase-start`, `/scope-check`, `/out-of-scope-gate`, `/tenancy-audit`, `/llm-degraded-audit` — these are not optional polish.
5. **Close every week with `/week-end` — mandatory.** A week is **not "complete"** until every gate in its Definition of Done passes: mechanical quality bar, behavioral + demoability smoke, `/code-review` (findings triaged — **never deferred wholesale**), a `/simplify` refactor pass, a per-feature test gate (every new feature names its contract test), and ledger updates. Flipping `WEEK: N (complete)` in `CURRENT_PHASE.md` is **blocked by a hook** (`.claude/hooks/week-end-gate.mjs`) until the bar passes (`.claude/.week-end-pass` sentinel from `scripts/week_end_gate.sh`) and `SHIPPED.md` records the review. Don't route around the hook — satisfy the gate. Week 3's deferred review is the cautionary tale. Details in `.claude/commands/week-end.md`. Applies to every Phase 1a/1b/1c week and every sub-phase boundary.
6. **No feature ships untested; no week ships un-refactored.** Every new endpoint / mutation / surface / algorithm gets the test that proves its contract (the §7.19 tenancy harness already fails the suite without the cross-tenant case). Every week's diff gets the `/simplify` pass so the codebase doesn't rot one "clean it up later" at a time.
7. **Update the ledgers.** `DECISIONS.md` for ADRs; `SHIPPED.md` for actuals-vs-spec at end of each sub-phase.

---

## Locked decisions (do not relitigate — see SCOPE.md §3)

- Multi-client + multi-tenant from V1. Tenancy enforced at application layer, not Postgres RLS.
- Next.js App Router + FastAPI. No Streamlit.
- PostgreSQL from V1. SQLite is not an option.
- Connector credential model: **organization-level OAuth + per-(client, market) ad account mapping**. Not per-(client, market, platform). See §7.14.
- **Phase 1a ingestion: CSV upload (web UI drag-drop, AM-triggered weekly).** First implementation of the §7.14 Connector Protocol is a CSV parser, not an API client. API connectors (Meta/Google/GA4/TikTok) ship as additional §7.14 Protocol implementations in Phase 1b/1c when API approvals land and the partner grants access. See ADR-003.
- Dual-mode evidence column always paired (Mode A + Mode B). **No third "blended" mode.**
- Reallocation framing: "options with evidence and confidence." **Never "we recommend."**
- Defense kit **never blocks on LLM**. See §7.17.
- Recommendation logging from day one of Phase 1a. Phase 4 calibration depends on it.
- All Phase 2/4 tables provisioned (empty) in Phase 1a. No schema retrofit later.
- MMM ships Phase 2, not Phase 1. Engineering scope, not data scarcity.
- TikTok in Phase 1 connectors. DV360/TTD deferred to Phase 4+.

---

## Correctness guard rails

The lists below prevent specific bug classes that are expensive to fix later (tenancy breaches, audit-log holes, money rounding errors, blocked LLM critical paths). They are not features to build — they describe properties that fall out naturally when you follow the skill patterns. If you're writing extra code to "satisfy" a rule, something's off.

### Things every change should preserve

- Every endpoint with `client_id` calls `enforce_client_access`. See `.claude/skills/tenancy/`.
- Every mutation writes to `AuditLog`. See `.claude/skills/audit-log/`.
- Every LLM-dependent path has a documented fallback per §7.17. See `.claude/skills/llm-call/`.
- Every `ReallocationSuggestion` writes a `RecommendationLog` row at creation. See `.claude/skills/recommendation-log/`.
- Every connector implements the §7.14 Protocol. See `.claude/skills/connector/`.
- Every new migration follows §6.2 conventions. See `.claude/skills/migration/`.
- Every new surface walks the §7.18 empty-state catalog. See `.claude/skills/empty-state/`.

### Things to never do

- No `float` for money. Use `numeric(18, 4)`.
- No `timestamp without time zone`. Use `timestamptz`. Stored UTC, converted at edges.
- No `json` columns. Use `jsonb`.
- No endpoint with `client_id` that skips `enforce_client_access`.
- No LLM call without an explicit fallback for its surface.
- No `client.messages.create` on the defense kit critical path that can block. Templated narrative is the fallback.
- No Phase N+1 work while Phase N is open unless explicitly authorized.
- No BYOK key persisted outside `EncryptedSecret`. No logging of customer API keys or token volume.
- No reauth flow accessible to the `account_manager` role. Admins only.
- No retroactive re-labeling of historical actuals on taxonomy change.

---

## Repo layout (per §6.1)

```
mixsight/
├── apps/
│   ├── web/                Next.js 14+ App Router, TS strict, Tailwind, shadcn/ui
│   └── api/                FastAPI, Python 3.11+, sqlmodel, Pydantic v2, async
│       └── connectors/     Per-platform modules implementing §7.14 Protocol
├── packages/
│   ├── types/              TS client generated from OpenAPI spec
│   └── shared/             Cross-app constants, enums, validation
├── modeling/
│   └── engines/            Pluggable MMM engines (Phase 2)
├── templates/
│   └── plans/              Starter plan templates (Phase 1b)
├── infra/docker/           Postgres + Redis Compose for local dev
├── scripts/
└── .claude/                Skills, slash commands, hooks (see below)
```

Sub-CLAUDE.md files at: `apps/web/`, `apps/api/`, `apps/api/connectors/`, `modeling/`, `templates/plans/`. Each holds conventions specific to that surface. Read them when you enter that directory.

---

## Cross-cutting concerns and where they live

| Concern | Skill | Slash command | Hook |
|---|---|---|---|
| Tenancy enforcement (§7.19) | `tenancy/` | `/tenancy-audit` | `tenancy-check.sh` |
| Audit logging (§7.4) | `audit-log/` | — | `audit-log-check.sh` |
| LLM degraded operation (§7.17) | `llm-call/` | `/llm-degraded-audit` | `llm-fallback-check.sh` |
| Recommendation logging | `recommendation-log/` | — | — |
| Migration conventions (§6.2) | `migration/` | `/migration-new` | `migration-check.sh` |
| Connector contract (§7.14) | `connector/` | `/connector-new` | — |
| Empty states (§7.18) | `empty-state/` | `/empty-state-coverage` | — |
| Taxonomy (§7.5) | `taxonomy/` | — | — |
| Defense kit (§7.13) | `defense-kit/` | `/defense-kit-render` | — |
| Freshness UX (§7.16) | `freshness-ux/` | — | — |
| Phase discipline | — | `/phase-start`, `/scope-check`, `/out-of-scope-gate` | — |

---

## Stack quick reference

Per SCOPE.md §6.1 / §6.2:

- **Frontend:** Next.js 14+ App Router, TypeScript strict, Tailwind, shadcn/ui, TanStack Query.
- **Backend:** FastAPI, Python 3.11+, sqlmodel (SQLAlchemy 2.0), Pydantic v2, async throughout. Python deps managed via `uv` (lockfile committed; `pyproject.toml` is the source of truth). See ADR-004.
- **DB:** PostgreSQL 15+, Alembic migrations. See §6.2 for conventions.
- **Jobs:** APScheduler embedded in FastAPI for V1 local; Celery + Redis on deploy.
- **Auth:** Clerk on Next.js (Clerk Elements custom components, not hosted UI — see ADR-004); JWT validation middleware on FastAPI. See §7.19.
- **LLM:** Anthropic Python SDK. Sonnet default; Opus only for low-confidence parser fallback. BYOK passthrough.
- **Modeling (Phase 2):** Pluggable in `modeling/engines/`. PyMC-Marketing first; Meridian under evaluation.
- **PDF:** Playwright headless Chromium for defense kit.
- **Billing:** Stripe + Stripe Tax. Per-workspace BYOK credit as recurring line item.
- **Type sharing:** OpenAPI → TypeScript. Regenerate on every backend schema change.

Anything not listed above (charting library, virtualization library, structured-logging library, HTML templating engine) is **not pre-decided** — pick when the first use forces the choice, document in `DECISIONS.md` if non-obvious, then stick with that choice across the codebase. Don't introduce a second library in the same category.

---

## Reading order for a fresh session

1. `CURRENT_PHASE.md` — what week of which phase.
2. The scope section for the current deliverable.
3. The sub-CLAUDE.md for the directory you'll work in.
4. The relevant skill SKILL.md.

Skip duplication. The scope is canonical; this file points.

---

## Engineering playbook

For phase-by-phase prompts, MCP setup, plugins, watch-outs: read `CLAUDE_ENGINEERING.md`.
