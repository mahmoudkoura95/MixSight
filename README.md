# MixSight

Monday-morning pacing and measurement workspace for performance marketing agencies. Domain: mixsight.ai.

Engineering scaffolding for build with Claude Code. The full project scope (canonical) is `SCOPE.md`.

## What's in this repo

- `SCOPE.md` — the project specification (v3.4 Engineering Readiness). Source of truth.
- `CLAUDE.md` — root operating manual for working with Claude Code in this repo.
- `CURRENT_PHASE.md` — live phase marker; update at every sub-phase boundary.
- `CLAUDE_ENGINEERING.md` — phase-by-phase prompts, MCPs, plugins, watch-outs.
- `DECISIONS.md` — ADR ledger.
- `SHIPPED.md` — actuals-vs-spec running ledger.
- `.claude/` — skills, slash commands, hooks.
- `apps/`, `packages/`, `modeling/`, `templates/`, `infra/`, `scripts/` — the monorepo layout per §6.1. Empty for now; populated through the build.

## How to start

1. Read `CLAUDE.md` (top to bottom — it's short).
2. Read `CURRENT_PHASE.md` to see what's active.
3. Read the relevant `SCOPE.md` section for the active phase.
4. Read `CLAUDE_ENGINEERING.md` for the recommended prompts and tooling for that phase.
5. Use `/phase-start <phase>` to formally kick off.

## Key commands

- `/phase-start <phase>` — kick off a phase or sub-phase.
- `/scope-check` — audit current diff against scope.
- `/out-of-scope-gate` — run before merging a large branch.
- `/tenancy-audit` — run before every commit touching API.
- `/llm-degraded-audit` — run after any change touching LLM calls.
- `/migration-new <description>` — scaffold a §6.2-compliant Alembic migration.
- `/connector-new <platform>` — scaffold a §7.14 Protocol connector.
- `/empty-state-coverage <surface>` — walk the §7.18 empty-state catalog.
- `/defense-kit-render <fixture>` — render the §7.13 defense kit locally.
- `/adr <decision>` — append an ADR.

## Stack

Per §6.1 / §6.2:

- **Frontend:** Next.js 14+ App Router, TypeScript strict, Tailwind, shadcn/ui.
- **Backend:** FastAPI, Python 3.11+, sqlmodel, Pydantic v2, async.
- **DB:** PostgreSQL 15+, Alembic.
- **Auth:** Clerk + JWT validation.
- **LLM:** Anthropic SDK. Sonnet default; Opus parser fallback. BYOK passthrough.
- **Modeling (Phase 2):** Pluggable engines. PyMC-Marketing → Meridian evaluation.
- **PDF:** Playwright headless Chromium.
- **Billing:** Stripe + Stripe Tax.

## Phase 1 success criteria (§7.22)

- 3 paying agencies, $1,500-3,500/mo each.
- ≥1 white-label deployment in production.
- ≥1 BYOK customer active.
- $90-130K ARR from Phase 1 customers.
- Defense kit usable through ≥3 Anthropic outages (the §7.17 fallback proven in practice).

See `SCOPE.md` for full detail.
