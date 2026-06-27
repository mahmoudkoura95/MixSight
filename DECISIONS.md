# MixSight Decision Records (ADRs)

Architecture decisions made during build. Use `/adr` to append a new entry.

The decisions in SCOPE.md §3 ("Locked decisions") are pre-decided and do not need ADRs — they're project-level constitution. ADRs are for decisions that come up during build that weren't explicitly pre-decided.

---

## Format

Each ADR follows:

```
## ADR-NNN: <headline-in-snake-case>

**Date:** [YYYY-MM-DD]
**Phase:** [active phase from CURRENT_PHASE.md]
**Status:** Accepted | Superseded by ADR-XXX | Rejected
**Scope reference:** [SCOPE.md section if applicable, or "extension"]

### Context
[What forced this decision. What's the problem we're solving?]

### Decision
[The choice made. State it definitively.]

### Alternatives considered
- Alternative A: [why not]
- Alternative B: [why not]

### Consequences
- Positive: [what we get]
- Negative: [what we lose or risk]
- Reversibility: [easy / moderate / hard]

### Related
- Related ADRs: [#]
- Related SCOPE.md sections: [§]
```

---

## Phase 1a

## ADR-001: marketing_site_outside_pnpm_workspace

**Date:** 2026-05-13
**Phase:** Pre-Phase-1a (Week 0)
**Status:** Accepted
**Scope reference:** Extension — supports §5 pre-build dependencies (Meta/Google/TikTok API approvals require a live privacy policy URL; §5.7 design partner outreach needs credible public surface). Not a §7.3 Phase 1a deliverable.

### Context

We need a public marketing site at mixsight.ai (separate from the app at app.mixsight.ai) live before filing platform API approval applications and before design partner outreach. The site needs a privacy policy, terms of service, pricing page, and landing page.

Two integration paths were considered for the new `apps/site/` package:

1. Part of the pnpm workspace (consistent with `apps/web` and `apps/api`).
2. Standalone, managed by npm, excluded from the workspace.

pnpm 11 (current version) blocks build scripts for new transitive dependencies by default (`ERR_PNPM_IGNORED_BUILDS`). The `unrs-resolver` transitive dep of `eslint-config-next` triggers this. Resolution requires either interactive `pnpm approve-builds` (not scriptable) or `pnpm.onlyBuiltDependencies` config plus lockfile regeneration — workable but a recurring friction point whenever someone fresh-clones the repo.

### Decision

The marketing site is scaffolded via `npx create-next-app@latest apps/site --use-npm ...` and managed by npm inside its own directory. `pnpm-workspace.yaml` excludes it via `!apps/site`. The site has its own `package.json`, `package-lock.json`, and `node_modules` and is operated independently of the pnpm workspace.

### Alternatives considered

- **Include in pnpm workspace with `onlyBuiltDependencies`:** Workable but introduces a fragile first-time-install ceremony. Future contributors who clone the repo and run `pnpm install` will hit the build-approval error and need debugging help. Not worth it for a package that shares zero code with the rest of the monorepo.
- **Use yarn or bun for the whole monorepo:** Out of scope. The rest of the project (Phase 1a `apps/web` and `apps/api`) targets pnpm per SCOPE.md §6.1.

### Consequences

- **Positive:** Site can be cloned, installed, and run with two commands (`cd apps/site && npm install`). Zero workspace-coupling failures. The pnpm workspace is left clean for the actual app work in Weeks 1–4.
- **Negative:** Two package managers in one repo. If we later want to share components between `apps/site` and `apps/web` (unlikely — marketing site vs. authenticated app have very different requirements), we'd need to migrate the site into the workspace. Low-probability future cost.
- **Reversibility:** Easy. Delete `apps/site/package-lock.json` and `apps/site/node_modules`, remove the `!apps/site` exclusion in `pnpm-workspace.yaml`, run `pnpm install`. Maybe 10 minutes of work if pnpm 11 build-approval issues get resolved upstream.

### Related

- Related ADRs: (none yet)
- Related SCOPE.md sections: §5 (pre-build dependencies), §5.7 (design partner program), §6.1 (repo structure)

## ADR-002: client_side_gate_for_private_pitch_page

**Date:** 2026-05-15
**Phase:** Pre-Phase-1a (Week 0)
**Status:** Accepted
**Scope reference:** Extension — supports §5.7 design partner outreach. Not a §7.3 Phase 1a engineering deliverable.

### Context

We need a private, password-gated pitch URL at `mixsight.ai/pitch` for design partner recruitment. The page covers Phase 1 through Phase 4 with animated mockups and is shared out-of-band with one agency at a time. Requirements: (1) not crawled by Google, (2) password protected, (3) deliverable on the existing `apps/site` deployment.

`apps/site/next.config.ts` has `output: "export"` (ADR-001 / static export to mixsight.ai). Static export excludes middleware, API routes, and any server-side auth. The CLAUDE.md for `apps/site` explicitly scopes out auth flows.

### Decision

Use a **client-side password gate** at `/pitch`:
- On submit, hash `username:password` with SHA-256 (Web Crypto).
- Compare against `NEXT_PUBLIC_PITCH_PASSWORD_HASH` (build-time inlined).
- On match: set `sessionStorage.pitch.authed.v1 = "1"` and render content.

Pair the gate with four independent layers of crawl prevention:
1. `public/robots.txt` with `Disallow: /pitch/`.
2. Route-level `metadata.robots = { index: false, follow: false }`.
3. Sitemap omission (no `/pitch/` entry).
4. No internal links from any other site route — URL shared via email/DM only.

### Alternatives considered

- **Cloudflare Access / Vercel Password Protection:** True HTTP-level auth, but couples the pitch URL to deployment-platform features that may not be configured yet. Reversible to this later if needed.
- **Drop `output: "export"` from `apps/site`:** Enables middleware-based HTTP Basic Auth, but contradicts ADR-001's static-export model and adds Node hosting requirements for what should be a one-page addition.
- **Separate sub-app for `/pitch`:** A tiny Next.js app deployed at a different path with its own runtime. Adds infrastructure for a single-purpose page.
- **No auth at all, rely on obscure URL:** Doesn't satisfy the "password protected" requirement and gives no plausible deniability if the URL leaks.

### Consequences

- **Positive:** Self-contained code change. Works with the existing static export. The password hash never reveals the password (SHA-256 with username salt makes brute-force non-trivial on a chosen password). Defense in depth against crawl indexing.
- **Negative:** Not cryptographic security. The hash sits in the JS bundle; a determined attacker who has the URL could attempt offline brute force. Acceptable because (a) the pitch content is the same material we'd share with the agency in any deck, (b) the URL is not publicly discoverable, and (c) we control rotation by updating the env var and redeploying.
- **Reversibility:** Easy. Replace the gate with platform-level auth at any time by removing the `PasswordGate` wrapper and configuring Cloudflare Access (or equivalent) in front of `/pitch/`.

### Related

- Related ADRs: ADR-001 (static export is what forces this gate model).
- Related SCOPE.md sections: §5.7 (design partner program — the page's purpose), §7.3 (this is adjacent to Phase 1a, not from a later phase).

## ADR-003: csv_first_ingestion_for_phase_1a

**Date:** 2026-06-21
**Phase:** Phase 1a (Week 0 → Week 1 kickoff)
**Status:** Accepted
**Scope reference:** Modifies §7.14 (Connector Protocol — first implementation is CSV, not OAuth API). Modifies §7.3 (Phase 1a connector deliverable replaced with CSV ingestion). Pairs with §5.1 (API approval lead times handled in parallel, not blocking).

### Context

Design partner **Brave Bison Agency** committed to Phase 1a with **New Balance EMEA** as the pilot client. Two facts about the partner state forced this decision:

1. Brave Bison is not ready to grant API access (Meta, Google Ads, GA4, TikTok) on the New Balance EMEA accounts in Phase 1a week 1 — internal security review and client coordination required first.
2. Platform API approval applications (§5.1) take 4–6 weeks to clear regardless.

Two options:

- **Wait for API access + approvals.** Pushes Phase 1a week 1 by 4–6 weeks. Partner momentum decays.
- **Ingest data via CSV uploads now; add API connectors as §7.14 Protocol implementations alongside CSV later.** Phase 1a starts immediately.

The pacing engine, drift formulas (§7.10), evidence column (§7.9), defense kit (§7.13), and reallocation logic (§7.10) are all source-agnostic — they operate on the normalized `actuals` table regardless of how rows got there. The Connector Protocol abstraction holds whether the implementation is an OAuth API client or a CSV parser.

### Decision

**Phase 1a ingestion is CSV-first. API connectors come in Phase 1b/1c.**

- **First implementation of §7.14 Connector Protocol: CSV parsers.** Native exports from Meta Ads Manager, Google Ads, and GA4 are the primary path. A normalized MixSight CSV template is the fallback for platforms without a native parser (TikTok in Phase 1a; future LinkedIn/Reddit).
- **Upload mechanism: web UI drag-drop, AM-triggered.** Monday-morning workflow per §7.16 — AM logs in, drags last week's CSVs into the pacing page upload zone, sees pacing populate. "Scheduled" means a Monday-morning reminder email; the trigger is human, the cadence is system-prompted.
- **§7.14 Protocol mapping for CSV:**
  - `authenticate` → schema validation (no OAuth)
  - `pull_actuals` → parse uploaded file, upsert into `actuals`
  - `health_check` → "last upload received N days ago"
  - `backfill` → accept date-range CSV, replay through the upsert path
  - `list_ad_accounts` → derive from distinct account_id column in the CSV
- **API connectors deferred to Phase 1b/1c.** Each platform becomes a second `Connector` implementation when (a) API approval lands and (b) Brave Bison grants Brave's-side access. Meta + Google + GA4 + TikTok API approval applications still filed in Phase 1a week 1 per §5.1 lead times — they bake while CSV ships.
- **Schema unchanged from §7.4.** `ConnectorAuth`, `AdAccountMapping`, `ConnectorAuthEvent` still provision in Phase 1a, sit empty for CSV-uploaded clients, populate when API connectors come online. No retrofit per locked decision: "All Phase 2/4 tables provisioned (empty) in Phase 1a."
- **`ConnectorAuthEvent` event types expand** to cover CSV ingestion: `csv_uploaded`, `csv_parse_failed`, `schema_mismatch`, `partial_ingestion`. Same audit story (§7.4), different event types.

### Alternatives considered

- **Wait for APIs:** Pushes Phase 1a week 1 by 4–6 weeks. Rejected — the wedge is the Monday morning workflow, not the ingestion mechanism.
- **CSV permanent (no API connectors ever):** Simpler now, more rework if APIs become a customer ask. Phase 4 calibration (§10.2) and cross-customer benchmarks would suffer if data hygiene drifts under manual upload. Rejected — APIs come later, but they come.
- **Normalized template only (no native parsers):** Lower parsing burden but higher AM friction (manual reformatting every Monday). Rejected — native parsers respect §7.16's "thirty-minute Monday" promise.
- **S3 / SFTP bucket polling:** More automation but requires Brave Bison to set up their dump pipeline. Adds infra and a moving part the AM can't see. Rejected for Phase 1a; reconsider in Phase 1c if the partner asks.

### Consequences

- **Positive:** Phase 1a week 1 starts immediately — no 4–6 week API approval blocker. CSV exports are universally available across Meta/Google/GA4 — Brave Bison already has them in their existing reporting workflow. The §7.14 Protocol abstraction holds, so API connectors plug in as additional implementations later without disturbing the pacing engine, evidence column, or defense kit.
- **Negative:** AM workload includes a manual weekly upload step that APIs would eliminate. Schema validation must be more defensive (a UI dropzone accepts anything). Mode B (cross-platform via GA4 — §7.9) becomes "Mode B *if* GA4 CSV uploaded" — explicit unavailability path needed in the §7.18 empty-state catalog. Two ingestion paths will coexist temporarily once APIs roll in — must keep the Protocol surface clean to avoid divergence.
- **Reversibility:** Moderate. The CSV-parser Connector implementation lives alongside API implementations; switching a (client, market) from CSV to API is a configuration change, not a migration. Backfilled CSV `actuals` rows remain valid history. The work to add API connectors in Phase 1b/1c is additive, not destructive.

### Related

- Related ADRs: ADR-001 (workspace structure), ADR-002 (pitch gate — the recruitment artifact that landed Brave Bison).
- Related SCOPE.md sections: §7.14 (Connector Protocol — first implementation is now CSV), §7.3 (Phase 1a deliverables — connector line modified), §5.1 (API approval lead times still apply, file in parallel), §7.16 (freshness UX — Monday upload reminder is the "scheduled" piece), §7.18 (empty-state catalog needs CSV-specific states: never-uploaded, partial-week-uploaded, parse-failed), §7.4 (`ConnectorAuthEvent` event-type expansion).

## ADR-004: phase_1a_week_1_stack_picks_and_partner_access_timing

**Date:** 2026-06-22
**Phase:** Phase 1a · Week 1 kickoff
**Status:** Accepted
**Scope reference:** Fills gaps left open by §6.2 (stack details). Modifies §7.3 (Phase 1a deliverable framing — partner access moves to Phase 1b Week 1).

### Context

SCOPE.md §6.2 names the languages, frameworks, and database but deliberately leaves several stack picks open. Four came up during Phase 1a Week 1 kickoff: (a) Python package manager for `apps/api`, (b) Clerk integration UX strategy, (c) deployed infra provider, (d) when Brave Bison gets first product access.

Per root CLAUDE.md: "Anything not listed [in the stack quick reference] is not pre-decided — pick when the first use forces the choice, document in DECISIONS.md if non-obvious, then stick with that choice across the codebase." Three of these are stack picks worth recording; the fourth deviates from §7.3's stated timing and needs the record.

### Decision

1. **Python package manager: `uv`.** Single binary, lockfile-first, fast installs. Drives `apps/api` and any future Python tooling. Lockfile committed; `pyproject.toml` is the source of truth.
2. **Clerk integration UX: Clerk Elements (custom components).** Build sign-in/sign-up screens as custom Next.js components using Clerk Elements primitives (not Clerk's hosted UI). Visual coherence with the existing `apps/site` marketing surface is worth the additional component work.
3. **Deployed infra provider: deferred to Phase 1c.** Week 1 sets up GitHub Actions for CI only (typecheck, lint, pytest with tenancy harness, Alembic round-trip). Phase 1a-b run on local dev. Phase 1c re-opens this decision when billing (§5.5) and custom-domain white-label (§6.4) force the choice.
4. **Brave Bison's first product access: Phase 1b Week 1, not Phase 1a Week 4.** §7.3 says "design partner has access for first feedback" at end of Phase 1a. We're holding that until Phase 1b Week 1 when real New Balance EMEA data is loaded, so first impression is on substance rather than skeleton. Weekly 30-min feedback calls per §5.7 continue throughout Phase 1a — via screen-share demos from local dev, not a deployed URL.

### Alternatives considered

- **Poetry / pip+pip-tools:** Poetry is mature but slower than uv; pip+pip-tools is most basic but higher friction. Rejected for speed and modern UX.
- **Clerk hosted UI:** Faster to ship but locks visual UX to Clerk templates. Rejected — Phase 1a polish for Brave Bison's first impression matters more than the few days saved.
- **Pick deployed infra now (Render / Fly / Railway / etc.):** Adds Week 1 setup overhead for a decision Phase 1c re-opens under more constraints (billing webhooks, custom domains, white-label, BYOK). Rejected — defer is cheaper.
- **Brave Bison access at Phase 1a Week 4 (the §7.3 framing):** Risks anchoring first impression to a skeleton over demo data. Rejected — substance-first.

### Consequences

- **Positive:** uv keeps Docker rebuilds fast. Clerk Elements gives polish parity with apps/site. Deferring infra collapses Week 1 setup. Holding the partner URL until Phase 1b sharpens first-impression signal.
- **Negative:** uv has a smaller community than Poetry; new contributors lap a slightly less familiar tool. Clerk Elements is more component code than hosted UI. Deferring infra means Phase 1c starts with a hosting decision still to make. Holding partner access means Phase 1a weekly feedback rides on screen-share, small operational overhead.
- **Reversibility:** All four easy. Tooling swaps are infrastructural, not data-shape changes. Partner access can move earlier on request.

### Related

- Related ADRs: ADR-001 (pnpm workspace — `apps/api` is a member), ADR-003 (CSV-first ingestion shapes the Phase 1a feature surface and supports the deferred-infra call), ADR-002 (the pitch artifact that landed Brave Bison).
- Related SCOPE.md sections: §6.2 (stack details — this ADR fills uv + Clerk UX gaps), §7.3 (Phase 1a deliverable timing — partner access deliberately shifted to Phase 1b Week 1), §7.19 (Clerk Elements still wires the Clerk JWT middleware unchanged), §5.5 (deployed infra — deferred to Phase 1c).

## Phase 1b

(future)

## Phase 1c

(future)

## Phase 2

(future)

## Phase 3

(future)

## Phase 4

(future)
