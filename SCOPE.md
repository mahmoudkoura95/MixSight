# MixSight — Project Scope v3.4 (Engineering Readiness)

**Domain:** mixsight.ai
**Document version:** 3.4 — v3.3 with two omitted entities formalized (MacroSignal, AuditLog), migration default conventions, and tenancy test harness specified
**Last updated:** May 2026
**Status:** Approved for engineering
**Audience:** Builder, Claude Code, future hires
**Supersedes:** v1.0, v2.1, v3.0, v3.1, v3.2, v3.3

This document is the single source of truth for engineering. v3.4 closes three gaps surfaced during Day 0 engineering setup: `MacroSignal` and `AuditLog` entities formally specified in §7.4 (previously referenced but never defined), database migration default conventions added to §6.2, and tenancy test harness specified in §7.19. Phase scope and timeline unchanged.

---

## 1. Vision

MixSight is a Monday-morning workflow tool for media agency account managers running paid media across multiple platforms and multiple markets. It turns "how did last week's spend track against plan, and what should we do about it?" from four hours of spreadsheet work into a thirty-minute review with a defense-ready one-pager at the end.

The wedge is pacing and reallocation. The depth is the multi-source disagreement (platform attribution, analytics-reported, modeled contribution, experimental incrementality) made visible inline rather than abstracted into a separate view. The closer is the defense kit — the branded artifact the AM walks into the 11am client meeting holding.

The product's primary commitment is workflow first, modeling second. Phase 1 makes the existing AM workflow faster, sharper, and more defensible. Later phases earn the right to charge more by adding modeled contribution, forecasting, and confidence calibration over time.

**Primary V1 use case:** a multi-market client with active media across Meta, Google, GA4, and TikTok, spanning multiple geographies and currencies, with multiple product lines and mixed objective types within their plan. Multi-market is a Phase 1 design constraint at the data-model level — but a single-market client must be onboardable in fifteen minutes.

---

## 2. Positioning & competitive context

### 2.1 What MixSight is

The pacing and measurement workspace for performance marketing agencies, built around the reality that platform numbers, analytics numbers, and modeled contribution will tell different stories — and the AM has to make a decision before the client call.

### 2.2 What MixSight is not

Not "the first triangulation platform." Lifesight, Measured, and Objective Platform have marketed triangulation as their core approach for at least eighteen months. We win on agency-native workflow depth.

Not an MMM tool. PyMC-Marketing and Google Meridian have commoditized the modeling layer. The model is not the moat.

Not real-time, but not stale either. Daily next-day data refresh with weekly workflow surface — see §7.16. "Real-time" implies streaming and autonomous bidding; that's a different product.

Not a category-definer in v1 marketing. Categories get defined by winning customers and being copied. Lead with the wedge; earn the category language.

### 2.3 Competitive landscape, for orientation

| Segment | Examples | Position vs us |
|---|---|---|
| Enterprise MMM SaaS | Recast, Sellforte, Liftlab, Keen, Mutinex, Paramark | Adjacent. Higher ACV, longer implementation. |
| Triangulation enterprise | Lifesight, Measured, Objective Platform | Direct philosophical neighbor for upper-tier agency engagements. |
| Agency self-service MMM | Cassandra, Arima | Head-to-head for the wedge. |
| DTC tactical attribution | Triple Whale, Northbeam, Fospha, Prescient, WorkMagic | Not direct, but their UX expectations bleed into our buyers. |
| Pacing dashboards (no measurement) | AgencyAnalytics, Marin, TapClicks | Solve part of Phase 1. |
| Ad-data pipelines | Improvado, Supermetrics, Funnel | Solve the data ingestion layer well. |
| Open-source MMM | Meridian (Google), Robyn (Meta), PyMC-Marketing | Commoditize the model. |

### 2.4 What we own that nobody else is shipping

Disagreement-as-evidence-column inline on every pacing row. Defense kit as a named, branded, white-labeled artifact. AI plan parser plus structured plan taxonomy with objective-type-aware drift detection and reallocation pooling. Multi-market as a first-class axis. Plan-change audit trail surfaced to clients in the defense kit. Confidence calibration over time, built on logged recommendations from day one. Platform-honest freshness UX — last 3 days visually distinguished as "still settling," with reconciliation diffs surfaced rather than hidden.

### 2.5 ICP refinement by phase

The phases are customer cohorts, not arbitrary timelines. Feature requests are evaluated against ICP fit for the relevant phase. A request from outside the active ICP is not "wrong" but doesn't shape that phase's roadmap.

**Phase 1 ICP.** 5-25 person performance or DTC agencies. Multi-market or aspirational multi-market roster. 3-8 active client engagements. Currently using Google Sheets plus a basic dashboard tool (AgencyAnalytics, Looker Studio, Supermetrics). $200K-$2M agency revenue. Founder or head-of-paid is the buyer and primary user. Geography: US, UK, EU. The value proposition: weekly pacing time saved, defensible Monday outputs, cleaner client communication.

**Phase 2 ICP.** Phase 1 cohort, plus agencies running across 4+ platforms with measurement-savvy senior staff, plus one or two slightly larger agencies (25-50 people) who want enterprise-flavored measurement without enterprise pricing. Plus expansion within the Phase 1 base — customers adopting MMM and modeling depth.

**Phase 3 ICP.** Agencies running incrementality testing (a more sophisticated practice). Phase 2 customers expanding workspace counts. Some agency holding companies considering MixSight as standard tooling across portfolios. Plus small-to-mid agencies who use forecasting in client pitches.

**Phase 4 ICP.** Vertical concentrations (DTC fashion, B2B SaaS, finance) where benchmarking becomes valuable. First B2B-focused agencies. Possibly first international expansion if customer demand pulls. The calibration UI value-prop becomes legible: "tool that has data on its own track record."

**The discipline this enforces.** Feature requests evaluated against the active phase's ICP. A request from a Fortune-500 in-house team in Phase 1 doesn't shape the Phase 2 roadmap. A request from a 200-person ad agency for enterprise-style features goes to Phase 3+ consideration, not Phase 1c. Every roadmap conflict is resolved by asking "is this from a Phase X ICP customer?"

---

## 3. Decisions locked

| Decision | Choice | Reason |
|---|---|---|
| Connector strategy | Full API connectors: Meta, Google, GA4, TikTok in Phase 1 | TikTok replaces DV360/TTD because mid-tier agencies run TikTok. |
| Connector credential model | Organization-level OAuth with per-(client, market) ad account mapping | Agency authenticates Meta Business Manager / Google MCC once; specific ad accounts mapped per client. Matches how agencies actually work. See §7.14. |
| Data freshness | Daily 7-day rolling refresh, weekly 90-day deep, monthly 13-month deep | "Yesterday only" misses platform restatements. Trailing windows + upsert is industry standard. |
| Real-time framing | Out of scope; framed as "next-day data" not "live" | Don't pick a fight with autonomous-MMM tools we're not trying to be. |
| UI stack | Next.js (App Router) + FastAPI | Streamlit cannot gracefully handle the surfaces this product needs. |
| Tenancy | Multi-client + multi-tenant from V1 | Retrofitting later costs more. |
| Hosting | Local for V1, deploy to Fly.io or Railway when first paying agency signs | Don't pay for infra without revenue. |
| Database | PostgreSQL from V1 | Multi-client + multi-market + multi-currency rules out SQLite. |
| Plan ingestion | AI agent parser with human-in-the-loop confirm + alternative templates | Both ship in Phase 1b. |
| Plan taxonomy | First-class entity in Phase 1 with objective_type, product line, audience segment, and agency-extensible dimensions | Real plans have multiple product lines, mixed objective types, and rollup needs. |
| LLM provisioning | MixSight-provided default; BYOK Claude available in Phase 1c with credit against plan price | Customers who care about cost or data residency can bring their own key. |
| LLM degraded operation | All LLM-dependent surfaces have explicit fallbacks; defense kit never blocks on narrative generation | Anthropic outages happen on Mondays; product cannot block on them. See §7.17. |
| Allocation modes | Dual-mode evidence column (platform-native + cross-platform) shown inline | Single-mode produces confidently wrong cross-channel suggestions. |
| Reallocation framing | "Options with evidence and confidence," ranked, not "we recommend" | Manages trust during the period when the algorithm is provably imperfect. |
| Reallocation pooling | Respects taxonomy constraints | Real budgets are politically separate even when mathematically poolable. |
| Modeling timing | MMM ships in Phase 2, not Phase 1 | Engineering scope creep, not data scarcity. Backfill from Phase 1a means data is ready. |
| Modeling engine | PyMC-Marketing in Phase 2a; Meridian as default by Phase 2b/2c if its API is stable | Architect modeling layer as a swappable engine from day one. |
| Lift test design | Phase 3, not Phase 2 | Designing a geo holdout is real statistics work. |
| Reforecasting | On-demand from Phase 3c, with versioned ForecastRun and forecast-vs-forecast diff view | A forecast is a tool to react to, not a quarterly artifact. |
| White-label | Phase 1c, not Phase 2 | The pricing-power lever for agency-targeted SaaS. |
| CSV ingestion | Shallow (actuals) in Phase 1c; deep (offline conversions, CRM) in Phase 2 | Both must be handled, but at different depths. |
| Recommendation tracking | Logged from day one of Phase 1; calibration UI ships Phase 4 | Track record needs time. Logging is cheap. |
| Public accuracy reporting | Internal and per-customer only — not external marketing | Public reporting weaponizes against you. |
| Open-protocol publication | Cut from roadmap | Move companies make after they've won. |
| Data deletion policy | 30-day grace, then hard delete; aggregates retained only if differentially private | Required for SOC 2 and GDPR. See §6.6. |
| Design-partner program | One committed partner by Phase 1a week 3 | Design-partner relationship is the gating risk for Phase 1, not engineering velocity. See §5.7. |

---

## 4. Pricing

Pricing structure is hybrid: base plans include seats and active client workspaces, with per-seat and per-workspace overage above plan limits. White-label and BYOK are tier features.

| Tier | Monthly | Includes | Overage | White-label |
|---|---|---|---|---|
| Starter | $599 | 2 seats, 3 workspaces, single-market only, 4 connectors, templates only (no AI parser) | $50/seat, $99/workspace | None |
| Growth | $1,499 | 5 seats, 10 workspaces, multi-market, all connectors, AI parser, BYOK option | $40/seat, $79/workspace | Logo + colors + PDF branding (no custom domain) |
| Agency | $3,999 | 15 seats, 30 workspaces, multi-market, all connectors, priority support, AI parser, BYOK option | $30/seat, $59/workspace | Full: custom domain, branded portal, white-labeled email-from |
| Enterprise | Custom | Custom seat/workspace caps, SLA, SSO, audit log export | Custom | Full + custom legal/data residency |

**Annual prepay:** 15% discount on all tiers paid annually.

**LLM generation quota:** every plan includes a per-workspace monthly quota for AI-generated content. Quotas: Starter 200/workspace/month, Growth 500/workspace/month, Agency 1500/workspace/month. Overage at $0.40 per generation.

### 4.1 BYOK LLM economics

Growth, Agency, and Enterprise tiers can configure a per-workspace Anthropic API key. When BYOK is active:

- All generation calls use the customer's key. MixSight passes through; we never see token volume.
- Customer's plan price is credited $200 per BYOK-active workspace per month, applied automatically on next invoice.
- Per-workspace LLM quotas no longer apply; customer is paying their own Anthropic bill capped by their own spend limits.
- Workspace LLM cost dashboard still shows generation counts to the customer for visibility.

**Why credit, not discount.** A tier discount creates tier-jumping problems. A per-workspace credit is clean: itemized on invoice, math survives mixed-BYOK rosters.

**Why $200/workspace/month.** Estimated average LLM cost per active workspace at our quota levels in 2026 prices is $120-280. $200 is the midpoint. Reviewable annually with actuals.

**Multi-model BYOK is not in v1.** Phase 2 or 3 if customer pull warrants.

### 4.2 What we don't do

No usage-based pricing tied to ad spend. No free tier (30-day pilot instead). No per-API-call pricing on connectors.

### 4.3 Pricing validation through Phase 1

Pricing in the table is a starting point, not a commitment. Three tests run during Phase 1c through Phase 2a, each with a defined trigger for re-evaluation.

**Test 1: Tier mix.** Hypothesis: a healthy mix lands roughly 30% Starter / 50% Growth / 20% Agency among new customers. Watch: are the first 5-10 customers all going Starter? If yes, Growth's value isn't legible. **Trigger to revisit:** <30% of new customers at Growth or above by Phase 1c week 4. **Possible responses:** lower Growth price, raise Starter price, move features between tiers, restructure entirely.

**Test 2: BYOK adoption rate.** Hypothesis: BYOK adoption among Growth+ workspaces lands at 20-40%. Watch: <20% means BYOK isn't a value driver and the credit could be reduced or repositioned; >50% means the credit is generous and might be operationally unsustainable. **Trigger to revisit:** 90 days of BYOK data in Phase 2. **Possible responses:** adjust the credit amount, reposition BYOK as data-residency rather than cost feature, or maintain.

**Test 3: White-label tier jump (Growth → Agency, +$2,500/mo).** Hypothesis: agencies who care about white-label will pay the jump. Watch: by month 4 of Phase 1c, are any Growth customers upgrading to Agency? Zero upgrades suggests the tier jump is too steep, the Agency value-prop is unclear, or the customer base is too small to have Agency-fit profiles. **Trigger to revisit:** 4 months without a Growth-to-Agency upgrade. **Possible responses:** introduce an interim tier, restructure the white-label gating, lower the Agency price.

**The framing this enforces.** Pricing review at end of Phase 1c is a real meeting on the calendar, not "we'll see how it goes." Each test has a documented hypothesis and a documented response space; the goal is to make pricing changes data-driven rather than reactive.

### 4.4 Support model

Honest about what support means by tier and by phase.

**Phase 1 reality.** Founder is the support team. Email plus a per-customer Slack channel for Growth+ tiers. SLAs: 48-hour response for Starter (business hours), same-day for Growth, 4-hour for Agency, 1-hour for Enterprise. "Priority support" for Agency tier is a dedicated Slack channel with faster response, not a separate team. This is communicated honestly in the docs and on the website — early customers know they're getting founder-direct support, not pretending there's a department behind a queue.

**Phase 3 onward.** Hire first dedicated support person. Update SLAs as scale allows.

**Phase 4.** Small support team. Documented escalation paths. Self-service knowledge base. Status page. The trappings.

The Phase 1 model is a feature, not a limitation — agency owners value direct founder access during build-out periods. It's also the right cost structure for the revenue Phase 1 supports.

---

## 5. Pre-build dependencies

These have lead times that block Phase 1c if not started on day 1.

### 5.1 Platform API approvals

**Meta Marketing API.** Meta Business Verification + Advanced Access for production conversion data. Approval window: 1-3 weeks.

**Google Ads API.** Developer token. Test access immediate; Basic Access requires application approval, 1-2 weeks.

**GA4 Data API.** OAuth client setup fast; quota planning is the real work. Standard property quota is 10K tokens/day. Multi-client × multi-market × daily pulls × backfill must be quota-budgeted from start.

**TikTok Marketing API.** OAuth + business app review. 1-2 weeks.

### 5.2 Auth provider account

Set up Clerk. V1 recommendation.

### 5.3 Domain + DNS

Register and configure mixsight.ai.

### 5.4 Anthropic API key

For default-provisioned LLM features. Keep usage observable from day 1.

### 5.5 Stripe account

Verification + payout setup 1-2 weeks. Tax handling via Stripe Tax. Need to support per-workspace credit line items for BYOK.

### 5.6 SOC 2 prep (Phase 2 trigger)

Engage Vanta or Drata at start of Phase 2.

### 5.7 Design-partner program

The single biggest non-technical gating risk for Phase 1. Without a real design partner giving feedback on real plans by week 4, Phase 1b ships features against assumptions instead of evidence.

**Target profile.** 5-25 person performance or DTC agency. Multi-market roster, or single-market with multi-market aspirations. 3-8 active client engagements. Currently pacing in Google Sheets or AgencyAnalytics, with documented frustration about it. At least one client running across Meta + Google + GA4 + (TikTok or programmatic). Founder or head-of-paid willing to give 30 minutes per week of feedback. Geography: US, UK, or EU primarily — timezone overlap with the founder matters for weekly sessions.

**Why this profile.** Big enough to feel real workflow pain and have variety. Small enough to make decisions fast and adopt new tools without procurement. Multi-market makes the multi-market data model real. Performance/DTC makes measurement triangulation acutely felt. Founder-led means the buyer and the user are the same person.

**Acquisition approach.** Founder's personal network first (LinkedIn, prior agency relationships). Niche communities second (Slack groups for agency owners, Twitter/LinkedIn discussions about pacing pain). Direct outreach third. Target 10-15 conversations to land 1 committed partner.

**The deal.**
- Free Phase 1 access, equivalent to Agency-tier feature set ($3,999/mo retail value), including white-label setup with custom domain.
- Locked-in $999/month rate on a 12-month commitment when paid pricing kicks in at Phase 1 completion. This is a design-partner-only rate, not a published tier.
- Custom feature priority and direct Slack access to the founder.
- White-label configuration assistance free of charge (custom domain DNS, SES verification, branding).

**In exchange.**
- Weekly 30-minute feedback session through Phase 1.
- Screenshot and quote rights for case study and marketing.
- Willingness to be public reference at Phase 1 completion.
- Two peer introductions to other agency owners.

**Timeline.**
- Phase 1a week 1: outreach starts.
- Phase 1a week 3: 1 partner committed, signed informal MOU.
- Phase 1a week 4: partner has access to skeleton, providing first feedback.
- Phase 1b week 1: partner using product on a real client.
- Phase 1c week 4: partner deployed white-label in production, ready to be reference.

**What success looks like.**
- Partner gives feedback unprompted by Phase 1b week 3.
- At least 3 product decisions in Phase 1b shifted by their feedback.
- At least 2 quotable testimonials produced.
- 2+ peer introductions made.
- Converts to paying customer at Phase 1 completion.
- Becomes reference customer #1 who closes paying customer #2.

**Risk to watch.** Design partner becomes a feature-requester whose specific edge cases distort Phase 1 scope. Mitigation: explicit framing in the MOU that feedback informs but doesn't dictate; some requests will be deferred to Phase 2+ or declined. The relationship is collaborative, not contractual — we're not building bespoke software for them.

**Failure mode.** No partner committed by Phase 1a week 4. **Response:** broaden the target profile (consider 25-50 person agencies, or B2B agencies), or extend Phase 1a by 2 weeks to continue outreach. Do not start Phase 1b without a committed partner — building without external feedback is the highest-cost mistake in early-stage product work.

---

## 6. Architecture overview

### 6.1 Repository structure

Single monorepo, pnpm workspaces:

```
mixsight/
├── apps/
│   ├── web/          # Next.js 14+ App Router, TypeScript, Tailwind, shadcn/ui
│   └── api/          # FastAPI, Python 3.11+, sqlmodel
├── packages/
│   ├── types/        # Generated TypeScript client from OpenAPI spec
│   └── shared/       # Shared constants, enums, validation logic
├── infra/
│   └── docker/       # Postgres + Redis Compose for local dev
├── modeling/
│   └── engines/      # Pluggable MMM engines (Phase 2)
├── templates/
│   └── plans/        # Starter plan templates (Phase 1b)
├── scripts/
│   └── codegen.sh    # Regenerate types from OpenAPI on every backend change
└── SCOPE.md          # This document
```

### 6.2 Stack details

**Frontend.** Next.js 14+ (App Router), TypeScript strict mode, Tailwind, shadcn/ui, Recharts or Tremor, TanStack Query.

**Backend.** FastAPI, Python 3.11+, sqlmodel (SQLAlchemy 2.0), Pydantic v2. Async throughout.

**Database.** PostgreSQL 15+. Alembic migrations.

**Migration default conventions** (apply unless explicitly justified otherwise; document deviations with a comment in the migration file):
- UUIDs via Postgres `gen_random_uuid()` (v4). UUIDv7 ecosystem support in SQLAlchemy 2.0 is still uneven; revisit Phase 4.
- Monetary values: `numeric(18, 4)` stored in local currency. Never `float` for money.
- Percentages and ratios: `numeric(8, 4)` (allows up to 9999.9999%, sufficient).
- FX rates: `numeric(20, 10)` (some currency pairs need many decimal places).
- Timestamps: `timestamp with time zone` always. Stored UTC, converted at the edges. Never `timestamp without time zone`.
- JSONB columns: always `jsonb`, never `json`. Indexes on JSONB use GIN.
- Soft delete: `deleted_at timestamptz` nullable. Partial indexes on `WHERE deleted_at IS NULL` for hot query paths.
- Indexes: every FK gets an index. Every `(client_id, ...)` query pattern gets a composite index.
- Constraint names: `{table}_{column}_{type}` convention (e.g., `actuals_unique_pull`, `plan_lines_plan_id_fk`). Predictable matters more than concise.

These defaults exist because they're each load-bearing for at least one downstream phase: monetary precision affects Phase 2 modeling inputs, JSONB GIN indexes affect taxonomy filter performance in Phase 1c, soft delete partial indexes affect every query in the steady state, and predictable constraint names make migration debugging fast.

**Background jobs.** APScheduler embedded in FastAPI for V1 local. Migrate to Celery + Redis when deploying. Three cron schedules driven by per-market timezone.

**Auth.** Clerk on Next.js side, JWT validation middleware on FastAPI side.

**LLM calls.** Anthropic Python SDK. Sonnet (latest) default; Opus only for low-confidence extraction fallback. Per-workspace quota enforcement at application layer. BYOK passthrough using customer-provided key from encrypted workspace settings.

**Modeling engine (Phase 2).** Pluggable interface in `modeling/engines/`. Phase 2a ships PyMC-Marketing; Phase 2b/2c evaluates Meridian.

**PDF rendering.** Playwright (headless Chromium).

**External data.** `pytrends` (Phase 2), `holidays`, `exchangerate.host`.

**Type sharing.** OpenAPI → TypeScript via `openapi-typescript`. Regenerate on every backend schema change.

**Billing.** Stripe + Stripe Tax. Subscriptions with metered overage. Per-workspace BYOK credit as recurring line item.

### 6.3 Tenancy model

`Organization` (top level, the agency) → `Client` (the brand, one billable workspace) → `Market` (geographic market within the client). `User` belongs to organization with role `admin` or `account_manager`. `UserClientAccess` grants. AMs see only assigned clients; admins see all clients in their org.

**Role specifics.**
- `admin` — full access to organization settings, billing, all clients, connector management, taxonomy, team management. Can authenticate connectors and reauth them. Can add/remove users. Can configure white-label and BYOK.
- `account_manager` — access to assigned clients only. Can edit plans and taxonomy for their assigned clients. Can generate defense kits. Can flag connector reauth needed (visible in connector health surface) but cannot perform reauth themselves. Cannot access organization-level settings.

Tenancy enforcement at the application layer (FastAPI dependency injection), not Postgres RLS. Every endpoint that takes a `client_id` validates `(user, client)` access in middleware before any query runs.

### 6.4 White-label model

Three layers, gated by tier:

**Layer 1 (Growth tier and above).** Per-organization branding: logo, primary color, accent color, applied to in-app chrome and PDF/HTML defense-kit exports. "Powered by MixSight" footer toggle in Agency tier and above.

**Layer 2 (Agency tier).** Custom domain (`insights.{agency}.com` via CNAME). Custom email-from for scheduled reports (`reports@{agency}.com` via SES verified domain). Branded client-portal route.

**Layer 3 (Enterprise).** Custom legal entity for billing, data residency options (US/EU), custom SAML SSO. Phase 4 implementation; Enterprise deals during Phase 1-3 are scoped as paid custom work, not self-serve.

### 6.5 Background processing

Three cron schedules drive most work:

- **Daily 6 AM (per-market local time):** trailing 7-day rolling re-fetch from each platform per market, upsert on unique key. See §7.14, §7.16.
- **Weekly Sunday night:** trailing 90-day deep re-fetch.
- **Monthly first-of-month:** trailing 13-month deep re-fetch.
- **On demand:** plan upload, defense kit edit, manual reforecast (Phase 3).

### 6.6 Data lifecycle and deletion

Required for SOC 2 (Phase 2) and GDPR. Specifying now so the data model and infrastructure don't need retrofit.

**Cancellation grace period.** 30 days from cancellation. Data preserved during grace; reactivation possible with one click. Billing paused, not stopped. Notification at day 25: "Final notice — data deleted in 5 days unless reactivated."

**Hard deletion at day 30+.** All customer-specific data hard-deleted: Plans, PlanLines, Actuals, PacingSnapshots, ReconciliationFactors, ReallocationSuggestions, DefenseKits, RecommendationLog, ContributionFits, ForecastRuns, IncrementalityResults, PromotionalEvents, ConnectorPulls, ConnectorAuthEvents, CampaignLabelRules, ClientTaxonomies, all credentials. Soft-deleted entities flushed.

**Aggregated retention for benchmarking.** Phase 4 cross-customer benchmarking depends on aggregate data. Aggregates retained only when differentially-private — individual customer contribution cannot be reconstructed from aggregates. When a customer deletes, their contribution to aggregates is removed; aggregates recomputed without their data on next refresh cycle. This is documented in the Privacy Notice as the basis for retention.

**Audit log retention.** 7 years for compliance. After customer deletion, identifiers in audit log anonymized (replaced with deterministic hashes that don't tie back to identifiable customers).

**Self-serve data export.** During the 30-day grace period, customers can download a full data export (CSV bundle of all their data, all entities, from `/settings/export`). Reduces friction in cancellation conversations and is the right thing to do.

**GDPR right-to-be-forgotten.** Explicit request via support; completes within 30 days. Same deletion mechanics as cancellation. Acknowledgment email within 48 hours of request.

**API credentials.** Always deleted at the moment of cancellation, separate from the 30-day data grace period. Credential deletion does not have a grace period — they're nuked immediately to prevent any further pulls.

**Implementation timing.** Data export and deletion endpoints implemented in Phase 2a alongside SOC 2 prep. Until then, deletion is manual on request — small enough customer base that this is operationally feasible. The data model in Phase 1 must already support deletion (no orphan references, no cascading constraint failures), even if the user-facing flow is implemented later.

---

## 7. Phase 1 — The wedge (Months 1-7)

**Target duration:** 14-17 weeks of focused work for 1a-1c.

### 7.1 Goal

By end of Phase 1, the AM should be able to:

- Walk into a Monday client meeting with a defense-kit one-pager — branded, defensible, edited, sent — within thirty minutes of opening the tool.
- Check mid-week whether anything is going sideways before it shows up in next Monday's snapshot.
- Filter pacing by product line, objective type, audience segment, or any other taxonomy dimension the agency has configured.
- Onboard a new single-market client in 12-15 minutes; a new multi-market client in under an hour.

### 7.2 User flows

#### 7.2.1 Onboarding flows

Two distinct onboarding scenarios, with realistic time estimates that honestly reflect what the AM does.

**First-time agency setup (Day 1, the agency's first MixSight workspace).** Realistic time: 30-45 minutes.

| Step | Time | Notes |
|---|---|---|
| Account creation, email verification | 3 min | Clerk handles. |
| Stripe payment setup | 3 min | Tier selection, card entry. |
| Organization branding (logo, colors) | 5 min | White-label Layer 1. |
| First client created | 1 min | Name, reporting currency. |
| First market(s) defined | 1-3 min | 1-3 markets typical. |
| Connect Meta (organization-level OAuth) | 5 min | Meta Business Manager OAuth, scope all ad accounts. |
| Connect Google Ads (organization-level OAuth) | 5 min | Customer ID / MCC auth. |
| Connect GA4 (organization-level OAuth) | 3 min | Property selection. |
| Connect TikTok if applicable | 3 min | OAuth + business app review pre-completed. |
| Map ad accounts to (client, market) | 2-3 min | Per-platform UI lists accessible accounts; AM ticks the relevant ones for this client × market. |
| Pick template OR upload first plan | 5-10 min | Template path: 5 min. Parser path: 8-10 min including preview review. |
| Confirm taxonomy seeded from template, or accept defaults | 2 min | Auto-seeded; AM reviews and confirms. |
| View first pacing snapshot (partial — see §7.18) | 1 min | Empty-state messaging. |
| Generate first defense kit (templated narrative) | 2 min | Empty-state defense kit. |

**Total: 39-49 minutes.**

**Adding a new client to existing agency (Day N).** This is the more common case once the agency is on MixSight. Most connectors are already authed at organization level. Realistic time: **12-15 minutes** — this is the "single-market client onboardable in fifteen minutes" claim made elsewhere in the doc.

| Step | Time | Notes |
|---|---|---|
| Create new client | 1 min | Name, reporting currency, default allocation mode. |
| Define markets | 1-2 min | 1-3 markets typical. |
| Auto-detect ad accounts from already-authed connectors | 1 min | UI lists accessible Meta business manager accounts, Google MCC, GA4 properties; AM ticks the ones for this client × market. |
| Configure per-market attribution if non-default | 0-2 min | Often skipped; defaults usually fit. |
| Pick template or upload plan | 3-5 min | Template path is faster. |
| Confirm taxonomy | 1 min | |
| View first snapshot | 1 min | |
| Generate first defense kit | 1 min | |

**Total: 9-13 minutes for single-market; 12-18 minutes for multi-market.**

**Background work happening during onboarding.** Historical backfill (24-36 months of data per platform per market) starts the moment connectors authenticate, runs for 6-12 hours. The AM does not wait for it. The first usable view is built from going-forward data and the trailing 7-day daily refresh window. Backfill progress visible in the connector health surface (§7.15) throughout.

**Unhappy paths to specify:**

- **Meta business verification rejected.** Documented escalation path: contact Meta business support with use case description; offer test-account workaround for early demos.
- **Google Ads developer token in pending review.** Documented workaround: use test access for early demos; production access flips on when token approved.
- **GA4 property without conversions configured.** Detected during connector setup; AM walked through GA4 admin steps to configure conversion events. Link to relevant Google docs.
- **Plan upload fails the parser.** Clear path to template upload as fallback. Parser failure logged for our investigation. AM not blocked.
- **Single-market client whose plan is in a currency that doesn't match any defined market.** Detected at parser/template confirmation step; AM either adds the missing market or corrects the plan.

#### 7.2.2 Steady-state usage

The AM opens the app on Monday at 9 AM. Default view: most recent week's pacing snapshot for the client they last worked on.

**Two distinct views per client, surfaced via tab:**

**Weekly snapshot view (Monday-focused, the canonical surface).** Frozen artifact, dated, stable, with status indicators, reallocation suggestions, and defense-kit generation.

1. **Snapshot banner.** "Week ending May 4, 2026 — Brand X — 4 markets, 12 channels, 3 product lines. Net pacing: +6.3% vs plan. 2 channels critical, 3 amber, 7 on-plan."
2. **Filter bar.** Multi-select filters for taxonomy dimensions: market, product_line, objective_type, audience_segment, agency-defined dimensions. Selection drives all sections beneath. "All" default per dimension.
3. **Connector health strip.** "All connectors healthy as of 06:14 GMT. Daily refresh covered last 7 days."
4. **Pacing table** grouped by selected primary dimension. Columns: Channel, Campaign, Labels (taxonomy chips), Planned Spend, Actual Spend, Spend Drift %, objective-aware KPI columns (CPA/ROAS for conversions; CPC/CTR for traffic; CPM/Reach for awareness), KPI Drift %, Evidence column, Status.
5. **Drift explanations.** For each amber/red row, LLM-generated paragraph. Pre-computed in Monday morning job. Cached.
6. **Reallocation suggestions.** Top 3 ranked by projected impact in reporting currency, respecting taxonomy pooling rules. Cross-taxonomy suggestions show context-check prompt.
7. **Generate defense kit** button.

**Current week view (mid-week, live numbers).**

1. **Header.** "Current week (May 5 — May 11) — Data current as of 06:14 AM local. Conversions in last 48h may still be settling."
2. **Spend so far this week** vs **week's planned target**, per channel per market. Progress bars.
3. **Conversions/clicks/whatever-the-objective so far** vs week's planned target. Same progress bar treatment.
4. **No green/amber/red status** — mid-week status is too noisy.
5. **No reallocation suggestions** — we don't recommend moving money on Wednesday based on partial-week data.
6. **No defense-kit generation** — defense kits are generated from the Monday snapshot only.
7. **The last 3 days** rendered with "still settling" visual treatment (lighter color, dotted top edge), tooltip explanation. Toggleable per organization in `/settings`. Default on.

Settings (clients, markets, attribution config, taxonomy, white-label, BYOK, connectors) live in `/settings`.

### 7.3 Sub-phase sequencing

#### Phase 1a — End-to-end skeleton (4 weeks)

**Scope:**
- Auth + tenancy (Clerk integrated, organization/client/user model in DB).
- One client, one market, one channel (Meta) end-to-end.
- Plan ingestion via CSV upload (template-based) — AI parser deferred to 1b.
- Meta API connector pulling actuals weekly (organization-level OAuth, single ad account mapped).
- Single mode (Platform-native only).
- Within-market within-channel reallocation only.
- Static (non-editable) defense kit.
- PostgreSQL schema for all entities listed in §7.4 including taxonomy, recommendation log, forecast run, connector auth event, etc. Empty tables provisioned now to avoid retrofit.
- Recommendation logging active from day one.
- Empty-state handling for new client (§7.18).

**Deliverable.** Account manager logs in, sees one Meta-on-one-market pacing view for Brand X, sees top 3 within-channel reallocation suggestions, generates a basic defense kit. Internally usable. Design partner has access for first feedback.

#### Phase 1b — Multi-market + dual mode + plan taxonomy + parser + templates (5-6 weeks)

**Scope:**
- All four reallocation scopes (within/cross × market/channel).
- Mode B (cross-platform allocation) computed alongside Mode A. Evidence column displays both as paired indicators.
- Currency handling: FX rates ingested daily, plans entered in local, cross-market efficiency in reporting.
- GA4 connector added (organization-level OAuth, properties mapped per market).
- Multi-market UI: market selector, grouped pacing table, per-market subtotals.
- ReconciliationFactor entity computed and surfaced as expanded evidence-column drill-down.
- Cross-market context-check prompt enforced before inclusion in defense kit.
- Defense kit has two render modes (per-market, rolled-up).
- Plan taxonomy as a first-class capability (§7.5). `ClientTaxonomy` and `CampaignLabelRule` entities live. Default taxonomy schema seeded per client. Taxonomy editor in `/settings`. Pacing UI filter bar driven by taxonomy.
- AI plan parser (§7.6) replacing CSV template upload. Parser extracts taxonomy dimensions per row.
- 3-5 starter plan templates (§7.7) shipped alongside parser.
- Objective-type-aware drift detection (§7.8).
- Reallocation respects taxonomy pooling constraints (§7.10).
- Single-market quick-onboard flow (§7.2.1).
- Empty-state handling extended for new markets, new product lines, mid-week-launched campaigns (§7.18).

**Deliverable.** Full multi-market client usable end-to-end. Single-market client onboardable in 12-15 minutes. Design partner running real client through the product.

#### Phase 1c — Connectors, daily refresh, polish, white-label, BYOK, billing (5-6 weeks)

**Scope:**
- Google Ads connector (organization-level OAuth via MCC).
- TikTok connector (organization-level OAuth).
- Daily refresh cron (§7.14, §7.16). Trailing 7-day rolling pull at 6 AM per-market local. Weekly Sunday-night deep pull. Monthly first-of-month deep pull.
- Current week view (§7.2.2) with settling visual treatment on last 3 days.
- Shallow CSV ingestion for actuals (predating API window). Tagged `Actuals.source = "csv_upload"`.
- Plan versioning with diff view; plan-change audit trail surfaced in defense kit.
- Editable defense-kit narrative.
- Multi-client admin (creating new clients, assigning AMs, configuring per-client defaults).
- Reconciliation factor explainer panel.
- Drift threshold configuration per client per objective_type.
- Basic PromotionalEvent entry UI.
- Connector health surface with backfill progress, freshness stamps, data substrate completeness panel (§7.15).
- **Connector credential lifecycle**: token expiry detection, proactive refresh, reauth flow, ConnectorAuthEvent logging (§7.14).
- **LLM degraded operation**: fallbacks for plan parser failure, drift explanation failure, defense kit narrative failure (§7.17).
- White-label — Layer 1 and Layer 2.
- BYOK LLM (§7.17). Settings UI to add/validate Anthropic API key per workspace.
- Stripe billing live.
- Self-serve data export endpoint (§6.6).
- General polish, error states, loading states.

**Deliverable.** Production-feeling tool. White-labeled deployment in production for design partner. First paying customer (or design partner conversion to paid).

### 7.4 Data model

All entities live under organization → client hierarchy. UUID primary keys. `created_at`, `updated_at`, `deleted_at` (soft delete) on all tables.

#### Core entities (Phase 1)

**Organization** — id, name, branding_config (JSONB), billing_customer_id (Stripe), plan_tier, deletion_status (active / grace_period / deleted), grace_period_ends_at, settling_visual_default (bool, default true), notification_preferences (JSONB), created_at.

**User** — id, organization_id, email, role (admin / account_manager), clerk_user_id.

**Client** — id, organization_id, name, reporting_currency (ISO 4217), default_allocation_mode, source_of_truth_config (JSONB), settling_visual_enabled (bool, default true), daily_refresh_window_days (int, default 7, valid range 3-14), llm_byok_key_ref (FK to encrypted secret, nullable), llm_byok_fallback_enabled (bool, default false), created_at.

**Market** — id, client_id, code, local_currency, reallocation_constraint, local_timezone (IANA, drives daily pull cron timing).

**MarketConfig** — id, market_id, attribution_settings (JSONB per channel), ga4_property_id.

**ConnectorAuth** — id, organization_id, platform (meta / google_ads / ga4 / tiktok), oauth_token_ref (FK to encrypted secret), refresh_token_ref (FK to encrypted secret), token_expires_at, accessible_accounts (JSONB — list of ad accounts/properties accessible to this auth), last_validated_at, status (active / reauth_needed / revoked).

**AdAccountMapping** — id, market_id, platform, connector_auth_id (FK to ConnectorAuth), external_account_id (the platform-side ad account ID), account_label (human-readable, fetched from platform), active.

**ConnectorAuthEvent** *(new in v3.3)* — id, organization_id, platform, connector_auth_id, event_type (initial_auth / refresh / reauth / revoked / validated), user_id (who triggered, nullable for system events), success (bool), error_code, error_message, occurred_at.

**ClientTaxonomy** — id, client_id, dimensions (JSONB — full taxonomy schema), seeded_from_template (nullable FK to template), version, created_at, updated_at.

**CampaignLabelRule** — id, client_id, market_id (nullable for global rules), rule_type (regex / prefix_match / lookup_table / explicit_assignment), rule_config (JSONB), label_assignments (JSONB), priority (int), active (bool).

**Plan** — id, client_id, version, source_artifact_uri, source_method (csv_upload / parser / template), template_id (nullable FK), status, period_start, period_end, currency_handling, ingested_at, ingested_by_user_id, change_summary (text).

**PlanLine** — id, plan_id, market_id, channel, campaign_label, period_start, period_end, planned_spend_local, planned_spend_reporting, objective_type (conversions / traffic / reach / engagement / video_views / app_installs / leads), kpi_target, kpi_target_efficiency, labels (JSONB), extraction_confidence (high/medium/low).

**Actuals** — id, client_id, market_id, channel, campaign_external_id, campaign_label, date, spend_local, spend_reporting, impressions, clicks, conversions, conversions_value, conversions_alt_attributions (JSONB), labels (JSONB), source (api_pull / csv_upload / csv_offline_conversions), pull_timestamp, pull_window_start, pull_window_end, fx_rate_used, archived_at_source (bool, default false).

UNIQUE constraint on `(client_id, market_id, channel, campaign_external_id, date, source)`. Every pull is upsert.

**PacingSnapshot** — id, client_id, market_id, week_ending, allocation_mode, fx_rate_used, generated_at, is_partial_week (bool — empty-state flag).

**PacingSnapshotLine** — id, snapshot_id, plan_line_id, actual_spend_to_date, planned_spend_to_date, spend_drift_pct, actual_kpi_to_date, planned_kpi_to_date, kpi_drift_pct, status (green/amber/red/critical/insufficient_data), drift_explanation_text, drift_explanation_status (generated / pending / failed), evidence_payload (JSONB), objective_type (denormalized), labels (denormalized).

**ReconciliationFactor** — id, client_id, market_id, channel, week_ending, ga4_to_platform_ratio, sample_size, confidence (preliminary / stable).

**ReallocationSuggestion** — id, snapshot_id, donor_line_id, receiver_line_id, proposed_amount_local, proposed_amount_reporting, projected_delta, projected_delta_units, confidence, scope, taxonomy_pooling_compliance (JSONB), rationale_text, included_in_defense_kit (bool), am_justification_text.

**RecommendationLog** — id, client_id, suggestion_id, recommended_at, predicted_delta, predicted_confidence, recommendation_source (heuristic_v1 / model_v2), implemented (bool), implemented_at, implemented_amount, observed_outcome, outcome_window_end, calibration_score.

**DefenseKit** — id, snapshot_id, render_mode, narrative_text, narrative_status (generated / templated_fallback / regenerated), included_suggestion_id, generated_pdf_uri, am_user_id, sent_at.

**PromotionalEvent** — id, client_id, market_id, name, event_type, start_date, end_date, expected_impact_notes.

**ConnectorPull** — id, client_id, market_id, platform, pull_window_start, pull_window_end, pull_type (daily / weekly / monthly / backfill / manual / catch_up), status (success/failed/partial), rows_fetched, rows_upserted, rows_revised, error_message, attempted_at, completed_at.

**EncryptedSecret** — id, ciphertext (bytea), key_version (int), purpose (oauth_access / oauth_refresh / llm_api_key — categorical, optional), created_at, accessed_at. Referenced by FK from `ConnectorAuth.oauth_token_ref`, `ConnectorAuth.refresh_token_ref`, `Client.llm_byok_key_ref`. Centralizes encrypted storage, supports key rotation via `key_version`, and makes "what's encrypted in this database" auditable. Master key sourced from environment via Fernet.

**MacroSignal** *(provisioned Phase 1, populated from Phase 2a)* — id, market_id, signal_type (google_trends_brand / google_trends_category / holiday / weather / cpi / custom), date, value (numeric), source (pytrends / holidays_lib / manual / external_api), captured_at. Phase 2 modeling consumes this. Provisioned in Phase 1a so the schema is set before Phase 2 starts populating.

**AuditLog** — id, organization_id, actor_user_id (nullable for system events), entity_type (string — table name), entity_id (UUID — reference to the affected entity), action (created / updated / deleted / restored), before (JSONB — entity state before mutation, nullable on create), after (JSONB — entity state after mutation, nullable on delete), occurred_at, request_id (string — for distributed tracing), metadata (JSONB — extensibility for action-specific context). Append-only; never updated, never deleted (except via the §6.6 anonymization at customer deletion). Wire mutation logging from Phase 1a so audit log export in Phase 1c+ has data to export. Surface a UI for export in Phase 1c (admin-only). 7-year retention with anonymization at customer deletion per §6.6.

**ContributionFit** *(Phase 2)* — id, client_id, model_version, engine, fit_date, training_window_start, training_window_end, parameters_uri, diagnostics (JSONB), status.

**IncrementalityResult** *(Phase 2 ingestion, Phase 3 design)* — id, client_id, market_id, channel, test_type, test_start, test_end, lift_estimate, lift_ci_low, lift_ci_high, source, notes.

**ForecastRun** *(Phase 3)* — id, client_id, run_at, run_type, input_plan_version, input_model_fit_id, input_external_signals_uri, output_trajectory (JSONB), output_summary (LLM-generated narrative).

### 7.5 Plan taxonomy and campaign matching

Per-client `ClientTaxonomy` declares what dimensions matter for that client and what values are valid. Default seeded schema:

```json
{
  "objective_type": {
    "values": ["conversions", "traffic", "reach", "engagement", "video_views", "app_installs", "leads"],
    "default": "conversions",
    "drives_drift_formula": true,
    "drives_reallocation_pooling": true,
    "required_per_plan_line": true
  },
  "product_line": {
    "values": [],
    "drives_reallocation_pooling": true,
    "required_per_plan_line": false
  },
  "audience_segment": {
    "values": ["prospecting", "remarketing", "lookalike", "branded"],
    "drives_reallocation_pooling": false,
    "required_per_plan_line": false
  },
  "funnel_stage": {
    "values": ["upper", "mid", "lower"],
    "drives_reallocation_pooling": false,
    "required_per_plan_line": false
  }
}
```

The agency can add dimensions, edit values, change pooling behavior, or remove dimensions. The taxonomy is versioned — changing it doesn't retroactively re-label historical data; it applies forward.

**Objective_type is special.** Drives the drift formula (§7.8) and required on every PlanLine. Default value `conversions` if not specified, but the parser is instructed to extract it when present.

**Campaign label rules** apply taxonomy labels to actuals:

- **Regex match on campaign name.** `BRX_MENS_PROSP_META.*` → `{product_line: "mens", audience_segment: "prospecting"}`.
- **Prefix match.** Simpler syntax for the same.
- **Lookup table.** AM uploads or maintains a CSV of `campaign_external_id → labels`.
- **Explicit assignment.** AM clicks a campaign in the pacing table and sets labels directly.

Rules evaluated in priority order. First match wins. Conflicts logged for AM review.

**Default seeded rules.** When a client is created from a template, the template seeds both `ClientTaxonomy` and a starter set of `CampaignLabelRule`s based on the template's documented naming convention.

**AM-facing UI:**
- `/settings/taxonomy` — per-client taxonomy editor. Versioned with audit log.
- `/settings/labeling-rules` — per-client rule editor. Live preview against current actuals.
- Inline label chips on every pacing row, hoverable for label provenance.
- Filter bar above pacing table, current week view, forecast view.
- Unlabeled actuals panel — campaigns running that don't match any rule.

**Reallocation pooling implications.** When a dimension has `drives_reallocation_pooling: true`, suggestions don't pair donor and receiver across different values of that dimension unless cross-pooling is explicitly authorized in `/settings/reallocation-policy`. See §7.10.

### 7.6 AI plan parser

**Pipeline:**

1. **Upload.** AM uploads .xlsx, .csv, or pastes a Google Sheets export URL. File stored at `source_artifact_uri`.
2. **Extraction.** Claude Sonnet (latest) called with structured-output schema matching `PlanLine` plus the client's `ClientTaxonomy` schema. Excel files: every sheet converted to CSV and passed together. Large files chunked by sheet if total tokens exceed budget.
3. **Confidence assessment.** Per-row `extraction_confidence`. Low-confidence rows re-run with Opus.
4. **Preview UI.** Editable table grouped by market. Low-confidence cells highlighted. Taxonomy chips visible per row. "What got dropped" panel for rejected lines.
5. **Confirm.** AM commits. Extraction confidence preserved per row in DB for audit.

**No auto-ingest path.**

**Versioning.** Revised plans show diff vs active version. Plan-change audit trail surfaced in defense kit.

**BYOK.** Parser calls use customer's API key when BYOK is active.

**Failure modes** — see §7.17.

### 7.7 Plan templates

3-5 starter templates, shipped in Phase 1b alongside the parser.

**Initial template set:**
- Single-market single-channel (Google Ads only, monthly budgets, conversions objective).
- Multi-channel single-market (Meta + Google + TikTok, single market, mixed objectives).
- Multi-market multi-channel with product lines (the canonical fashion / DTC client).
- Retail/promo-heavy (with explicit promotional event columns).
- B2B-shaped (Phase 4 readiness; ships now to avoid retrofit).

Templates stored in `templates/plans/` as Excel files plus accompanying `taxonomy.json` and `label_rules.json`. Adopting a template adopts its `ClientTaxonomy` and seeded `CampaignLabelRule`s. Forkable per-organization.

**Starter tier gating.** Starter offers templates only — AI parser is Growth and above. This gives Growth a clear functional reason to exist. Validated through pricing test 1 (§4.3).

### 7.8 Drift detection

**Objective-type-aware drift formulas.** Drift formula branches on `PlanLine.objective_type`:

| objective_type | Spend drift | KPI drift |
|---|---|---|
| conversions | `\|actual - planned\| / planned` on spend | Same formula on cost-per-conversion (CPA) or ROAS |
| traffic | Same | Same on cost-per-click (CPC) or CTR |
| reach | Same | Same on CPM or unique reach |
| engagement | Same | Same on cost-per-engagement (CPE) |
| video_views | Same | Same on cost-per-view (CPV) |
| app_installs | Same | Same on cost-per-install (CPI) |
| leads | Same | Same on cost-per-lead (CPL) |

Default thresholds (configurable per client per objective_type):
- **Spend drift:** Amber 10%, red 20%.
- **KPI drift:** Amber 15%, red 30%.

Pacing computed against time-elapsed in the flight, not calendar week. `status` is the worse of the two.

**Drift explanation text** generated by Claude per amber/red row in Monday job, objective-type-aware. Cached by snapshot line hash; regenerated only on data change.

**Insufficient-data status.** Pacing rows with <7 days of data or <30 conversions render with status `insufficient_data` rather than amber/red. See §7.18.

### 7.9 Evidence column

Both modes always run; evidence column displays them as paired indicators inline.

**Mode A — Platform-native.** `realized_efficiency` from platform's own measurement framework.

**Mode B — Cross-platform source-of-truth.** `realized_efficiency` from `Client.source_of_truth_config` (typically GA4).

**Visual.** Horizontal range bar with two indicators. Tight cluster (<15% delta default) renders quiet/green; wide spread renders red with delta visible. Click expands to full breakdown, attribution settings per source, reconciliation factor history, methodology footnote.

**No third "blended" mode.**

When top-3 reallocation suggestions diverge between modes, an inline note: "In cross-platform mode, recommendation #1 changes to..."

### 7.10 Reallocation logic (v1 algorithm)

For a given `PacingSnapshot` and allocation mode:

1. Compute realized efficiency per line (rolling 14-day cost-per-KPI on `objective_type` metric). Skip lines with insufficient data.
2. Identify donors (overpacing AND underperforming).
3. Identify receivers (underpacing AND overperforming).
4. Generate candidate pairs. `proposed_amount = min(donor_overpace, receiver_headroom × 1.3)`.
5. Project impact in objective-appropriate units.
6. Tag scope (within/cross × market/channel).
7. **Apply taxonomy pooling constraints.** Different `objective_type` pairs are suppressed entirely. Different values of any `drives_reallocation_pooling: true` dimension (typically product_line) are suppressed unless cross-pooling enabled in `/settings/reallocation-policy`.
8. Apply scope filter and reallocation_constraint.
9. Score confidence (data volume, weekly stability, cross-channel/cross-market caps, taxonomy-cross-dimension caps).
10. Rank top 3 by absolute `projected_delta`. Same-market, same-product-line surface first when impact comparable.
11. Persist as `ReallocationSuggestion`. Also write to `RecommendationLog`.

**Cross-market context-check.** Justification required for inclusion in defense kit.

**Cross-taxonomy context-check.** Justification required for cross-pooling-enabled cross-dimension suggestions.

### 7.11 Multi-market handling

Multi-market is a first-class axis. Cross-market views in reporting currency; in-market views in local with reporting toggle. Per-market attribution settings, reallocation constraints, local timezones. Pacing table grouped by market first.

### 7.12 Currency handling

Each market has `local_currency`; each client has `reporting_currency`. Plans in local; parser detects and confirms. Actuals stored in local; reporting-currency computed on read. FX rates daily from `exchangerate.host`. Projected deltas shown in both currencies.

### 7.13 Defense kit

Branded with agency identity (Growth tier and above). HTML server-rendered; PDF via Playwright.

**Two render modes:** per-market and rolled-up.

**Sections:** Header (agency logo), top-line summary (LLM-generated, editable; falls back to template if LLM fails — see §7.17), pacing table, top 3 drift callouts, selected reallocation, plan-change audit, methodology footnote, next-week outlook.

**Editing.** Narrative paragraph and outlook are rich-text editable. Pacing table and reallocation block are structural.

**Defense kit never blocks on LLM.** See §7.17.

### 7.14 Connector specification

Each connector is a Python module under `apps/api/connectors/<platform>/`. Common interface:

```python
class Connector(Protocol):
    async def authenticate(self, organization_id: UUID) -> ConnectorAuth: ...
    async def list_accessible_accounts(self, auth: ConnectorAuth) -> list[Account]: ...
    async def pull_actuals(
        self,
        auth: ConnectorAuth,
        ad_account_id: str,
        market_id: UUID,
        start_date: date,
        end_date: date,
        pull_type: PullType,
    ) -> list[ActualsRecord]: ...
    async def health_check(self, auth: ConnectorAuth) -> ConnectorHealth: ...
    async def refresh_token(self, auth: ConnectorAuth) -> ConnectorAuth: ...
```

#### Credential model (organization-level OAuth + per-(client, market) ad account mapping)

This is how agency tools actually work, and it differs from the per-(client, market, platform) credential model implied in v3.0-v3.2.

**Authentication is at the organization level.** An agency authenticates Meta Business Manager once via OAuth. The auth grants access to all ad accounts under that BM. Stored as one `ConnectorAuth` row per (organization, platform).

**Ad accounts are mapped per (client, market).** During client/market setup, the AM picks from the list of ad accounts accessible via the org-level auth. Stored as `AdAccountMapping` rows per (market, platform). One ad account can be mapped to multiple (client, market) tuples if needed (rare but allowed).

**The same model for Google Ads MCC, GA4 properties, TikTok Business Center.** Each platform has an organization-level identity that owns multiple sub-accounts; we authenticate the parent and map sub-accounts.

**Practical implication.** Onboarding time decreases substantially after the first client because connectors are already authed at the agency level. New client setup is just "create client, map ad accounts" — the OAuth dance happens once per agency per platform.

#### Pull schedules

Three scheduled pull types, plus on-demand and backfill:

**Daily — trailing 7-day rolling re-fetch.** Runs at 6 AM per-market local time. Re-fetches the trailing 7 days from each platform per market, upserts on unique key. Trailing window configurable per client (`Client.daily_refresh_window_days`, default 7, valid range 3-14).

**Weekly — trailing 90-day deep re-fetch.** Sunday night. Full attribution variants. Reconciliation factors recomputed. Canonical record for Monday's PacingSnapshot.

**Monthly — trailing 13-month deep re-fetch.** First of month. Catches the very long tail.

**Historical backfill on first authentication.** When an `AdAccountMapping` is first created, MixSight triggers a full historical pull targeting **maximum available, capped at 36 months by default, configurable per platform**. Background job; AM is told "backfill in progress, going-forward daily/weekly pulls active immediately."

Per-platform backfill caps (defaults):
- Meta: 36 months.
- Google Ads: 36 months (capped from 4+ year API max for cost control).
- GA4: since property creation, capped at 36 months.
- TikTok: 24 months.

Backfill is paced to respect platform rate limits and especially GA4 token quotas — historical pull won't exhaust the daily quota budget.

**Idempotency.** All pulls upsert on `(client_id, market_id, channel, campaign_external_id, date, source)`.

**Restatement tracking.** When a pull changes a previously-stored value by more than the configurable threshold (default 5%), recorded in `ConnectorPull.rows_revised` and surfaced in audit log.

**CSV ingestion (Phase 1c, shallow).** AM uploads CSV of actuals for periods predating API window or to fill API gaps. Stored with `Actuals.source = "csv_upload"`. Phase 2 extends to deep CSV for offline conversions, in-store sales, CRM data.

#### Per-platform notes

- **Meta:** Marketing API current version. Pull at campaign level. Attribution windows: pull all available, store in `conversions_alt_attributions` JSONB.
- **Google Ads:** GAQL query at campaign level. Attribution models: pull conversions under configured model, store all_conversions in `alt_attributions`.
- **GA4:** Data API. Pull `sessions`, `conversions`, `purchaseRevenue` per `sessionSource`/`sessionMedium`. Quota-budgeted.
- **TikTok:** Marketing API. Day-level campaign aggregates.

#### Connector hardening (Phase 1c)

- Idempotent upserts.
- Rate-limit aware with exponential backoff.
- Audit log per pull populates `ConnectorPull`.
- Credentials encrypted at rest using Fernet with key from environment.
- Campaign rename detection — surfaced in audit log when same `campaign_external_id` returns with different name.
- Campaign archiving — campaigns missing from a pull marked `archived_at_source = true`, historical preserved.

#### Credential lifecycle and reauth

Real things that will happen:

**Token expiry by platform.** Meta long-lived tokens expire (~60 days). Google Ads OAuth refresh tokens are stable but can be revoked by password change or admin action. GA4 OAuth similar. TikTok access tokens are short-lived (typically 24 hours for access tokens, longer for refresh).

**Proactive refresh.** Background job checks token expiry across all `ConnectorAuth` records every 6 hours. Tokens within 7 days of expiry get refreshed automatically using refresh tokens. Refresh failures (e.g., refresh token revoked) trigger reauth-needed state.

**Reauth-needed state.** Distinct from connector-failed (which is rate limit, transient error, platform outage). When reauth is needed:
- `ConnectorAuth.status` set to `reauth_needed`.
- All ad account pulls under that auth pause.
- Pacing data goes stale but is preserved.
- Connector health surface shows red banner: "Reauth needed — Meta. Last good data: Saturday May 4."
- Pacing screen shows the same banner inline.
- AMs can flag the issue but cannot perform reauth. Org admins receive notification (configurable: immediate / daily digest / weekly digest; default immediate for paid tiers, daily for Starter).

**Reauth flow.**
1. Org admin clicks "Reauth Meta" in `/settings/connectors` or in the connector health surface.
2. OAuth handshake with the platform.
3. On success: new auth tokens stored, status set to `active`, all paused pulls resume.
4. Catch-up backfill of missed days runs in background; visible in connector health.
5. Logged as `ConnectorAuthEvent` with `event_type = reauth`.

**Edge cases:**
- **Original AM who authed has left the agency.** Any user with `admin` role can reauth. No constraint on it being the original authenticator.
- **Multiple ad accounts under one connection with partial revocation.** Detected and surfaced per-ad-account in connector health.
- **Platform-level access entirely revoked (e.g., Meta business verification revoked).** Distinct error, surfaced as "platform-level access revoked" with link to platform help docs. Reauth alone won't fix this; the AM must address the platform-side issue first.

**Audit.** Every credential event logged in `ConnectorAuthEvent`: who triggered (or system), when, which platform, success/failure, error code. Available in agency admin's audit view in `/settings/audit-log`.

### 7.15 Connector health surface

A first-class status route, `/health`, accessible to all users in the org. Shows:

- Per (client, market, platform) tuple: last successful pull timestamp, expected next pull, current status (green/amber/red/reauth_needed), pull type breakdown (daily / weekly / monthly).
- Inline indicator on the main pacing screen and current week view: "Data current as of 06:14 AM local. Daily refresh covered last 7 days."
- Manual retry button per failed pull.
- Audit log of last 30 days of pulls per platform, including rows revised in restatements.
- **Historical backfill progress.** Per (client, market, platform): how much of the requested window has been ingested, ETA, gaps with platform-side reasons.
- **Data substrate completeness panel.** Per client: weeks of clean data per channel per market, promotional event coverage, FX rate completeness, channel taxonomy coverage. MMM eligibility indicator.
- **Reauth needed banner.** Prominent when any `ConnectorAuth.status = reauth_needed`. Click goes to reauth flow (admin-only).

### 7.16 Data freshness and accuracy UX

**Two views, clearly distinguished.**
- **Weekly snapshot view** (Monday surface): frozen, dated, with status, reallocations, defense kit. Data current as of last Sunday-night deep pull.
- **Current week view** (mid-week surface): live numbers from daily pulls, no status, no reallocations, no defense-kit generation.

**The "still settling" visual treatment.** On any chart in the current week view, the trailing 3 days render with:
- Lighter color saturation than older data.
- Dotted top edge on chart strokes.
- Hover tooltip: "Conversions in this window may still be reported as platforms finalize attribution. Stable values typically by Day N+3 to N+7."

**Per-organization toggle in `/settings`** (default on). Per-client override available; defaults inherit from org.

**Freshness stamp** on every data view: "Data current as of [timestamp] [timezone]. Daily refresh re-fetched last [N] days."

**Settling caveat configurable per client** for clients with shorter conversion lag.

**Reconciliation diff in audit log.** When deep weekly pull restates a prior day's number by more than threshold (default 5%), diff logged with old/new values.

**LLM cost stays bounded.** All LLM-generated content gated to weekly snapshot view. Mid-week current week view uses no LLM calls.

### 7.17 LLM cost guards, BYOK, and degraded operation

Per-workspace generation quota enforced at the application layer (§4 quotas).

**Three modes per workspace:**

- **Default — MixSight key, in quota.** Counted against monthly quota. Cached generations don't count.
- **Default — MixSight key, overage.** Continues at $0.40/generation. Per-org config can hard-stop instead.
- **BYOK — Customer key.** All calls use customer's key. No quota counting on our side. Per-workspace credit applied to billing.

**BYOK setup flow:**

1. Admin navigates to `/settings/llm`.
2. Pastes Anthropic API key. Encrypted at rest using Fernet.
3. MixSight sends a no-op test call (single-token completion) to validate.
4. On success: BYOK active. Per-workspace credit ($200) applied on next invoice.

**Per-feature cost dashboard** for workspace admins regardless of mode.

**Multi-model BYOK is not in v1.**

#### Failure modes and degraded operation

LLM-dependent surfaces have explicit fallbacks because Anthropic outages, rate limits, and BYOK key issues will happen. Monday morning is exactly when an outage hurts most.

**Plan parser failure.** Three retries with exponential backoff. After failure: UI shows "Parser temporarily unavailable — try again or upload using a template." Source artifact preserved; parsing can be retried from upload history. AM can immediately fall back to template path. No data loss.

**Drift explanation generation failure.** In the Monday-morning batch job: failed rows get "Explanation pending" placeholder rather than empty. Background retry every 30 minutes for 4 hours. After exhaustion, deferred until next batch run. On-demand regeneration: same retry policy with manual retry visible in the row. Cached explanations from prior weeks remain visible and clearly dated.

**Defense kit narrative failure — the critical path.** AM clicks "Generate defense kit." Narrative generation timeout: 60 seconds. If the LLM call fails or times out:

- Defense kit **still generates** with all structural elements (header, pacing table, reallocation block, plan-change audit, methodology footnote).
- Narrative replaced with templated fallback: "Top-line summary: [edit this paragraph with your client-facing narrative]."
- "Regenerate narrative" button visible in the editor to retry when service returns.
- `DefenseKit.narrative_status` set to `templated_fallback` for audit visibility.

The AM walks into the meeting with the structural defense kit. The LLM polish is an enhancement, not a dependency. This is non-negotiable: the product cannot block defense kit generation on LLM availability.

**BYOK-specific failure modes.**

- **401/403 (key invalid).** Treat as auth failure. Banner in workspace: "BYOK key invalid — update in /settings/llm." If `Client.llm_byok_fallback_enabled = true`, fall back to MixSight key with quota counting and overage billing. Default: false (strict BYOK).
- **429 (rate limited).** Respect retry-after header, wait, retry. Sustained 429s (>30 minutes): treat as outage with same fallback option.
- **402 (insufficient credit on customer's Anthropic account).** Notify org admin immediately. Treat as outage. Fall back if `llm_byok_fallback_enabled = true`.

**Workspace quota exhaustion.** At quota: continues with overage billing or hard-stop based on org-level config. Hard-stop never applies to defense kit narrative — defense kit is structural artifact, must always generate. If hard-stop enabled and quota exhausted, defense kit narrative falls back to templated.

### 7.18 Empty states and first-week experience

The product needs to feel useful from minute one of onboarding, not "come back next Monday."

**Backfill in progress (Day 0 to ~Day 1).** AM has just authenticated connectors; backfill running. UI banner: "Historical data loading — full pacing view available in approximately 6-12 hours. Going-forward data updating every morning." Pacing table populated with whatever data exists (typically the trailing 7-day daily pull window already complete). Status indicators muted.

**Backfill complete, partial week of going-forward data (~Day 1 through end of first calendar week).** Pacing table populated. Reallocation suggestions become available algorithmically once 14+ days of historical or backfilled data exists per campaign — backfill counts. Reconciliation factors warming up: "Preliminary — sample size limited" annotation until 4+ weeks of variance accumulated.

**First Monday snapshot for new client.** Snapshot generated even if onboarded mid-week.
- `PacingSnapshot.is_partial_week = true` if onboarded after Tuesday in the snapshot week.
- Banner across the top: "First snapshot — based on partial week and historical backfill. Full Monday-morning experience available [date of first complete Sunday-to-Sunday week]."
- Reallocation suggestions visible if data sufficient; muted if not, with explainer: "Reallocation suggestions require 14+ days of stable per-campaign efficiency data."
- Drift explanations: not generated for `insufficient_data` rows. The empty state is "no significant drift detected — building baseline" rather than blank.
- Defense kit: generatable with header, pacing table, methodology footnote, and a templated narrative ("Initial week of MixSight tracking; baseline established. Detailed insights available from Week 2."). No drift callouts, no reallocation block.

**Permanent partial-data states.** These persist indefinitely and need explicit handling:

- **Campaign launched mid-week with <7 days of data.** Pacing row visible. Status badge `insufficient_data`. Excluded from reallocation candidates. No drift explanation. Tooltip: "Building baseline — 7+ days needed for drift detection."
- **Channel with zero historical conversions.** Drift formula handles divide-by-zero. Status defaults to amber with reason `no_conversion_baseline`. Drift explanation skipped.
- **Market with ad accounts authed but zero spend.** Market visible in selector. Pacing table empty for that market with explainer: "No spend yet in [market]. Pacing view available once first spend recorded."
- **Plan period not yet started.** Pacing table shows planned values; actuals empty. Status `pre_flight`. Drift detection skipped. AM can still review plan and configure taxonomy.
- **Plan period ended.** Snapshot frozen at last-week-of-flight values. Banner: "Plan period ended [date]. Final pacing recorded." Subsequent weeks show "no active plan" until new plan ingested.
- **Empty taxonomy filter result.** AM filters to a dimension value with no matching rows. UI shows "No campaigns match the current filter" with link to clear filter or extend taxonomy.

**Why this section exists.** The first time an AM logs into MixSight is also the first time they're deciding whether to keep their team using it. A product that says "come back next Monday" loses the AM in 30 seconds. A product that says "here's what I can show you now, here's what's coming, here's what to do in the meantime" earns another visit. Empty states are not edge cases; they're the first experience.

### 7.19 Auth & tenancy specifics

- Sign-in via Clerk on web side.
- API receives Clerk session JWT, verifies via Clerk JWKS.
- Middleware extracts `clerk_user_id`, looks up `User`, attaches `current_user` to request scope.
- Every endpoint with `client_id` calls `enforce_client_access(current_user, client_id)`. 403 if no `UserClientAccess` and not org admin.
- Admins see all clients; AMs see only assigned clients.
- Connector authentication and reauth restricted to `admin` role.
- AMs can flag connector reauth-needed via the connector health surface; org admins receive notification.
- Audit log on every mutation, written to `AuditLog` (§7.4). Retention and anonymization per §6.6.

**Clerk role sync.** Clerk is the authentication source of truth; our DB is the authorization source of truth. Custom organization roles `admin` and `account_manager` configured in Clerk dashboard (overriding Clerk's default `org:admin` / `org:member`). Webhook subscriptions on `organizationMembership.created`, `.updated`, `.deleted` upsert to our `User` and `UserClientAccess` tables. JWT carries the role as a custom claim for fast checks; mutations and sensitive operations re-check the DB to handle the eventual-consistency window between Clerk update and webhook delivery. Webhook handler must use `event_id` and event timestamp to reject stale or out-of-order events for the same entity.

**Tenancy test harness.** Multi-tenancy enforced at the application layer means a single missed `enforce_client_access` call is a tenancy breach. Two pieces, both shipped in Phase 1a, both run in CI from week 1:

1. **App-startup decorator audit.** On FastAPI app startup, introspect every registered route. For routes that take a `client_id` parameter (path, query, or body), assert that `enforce_client_access` is in the dependency chain. Routes that fail the audit fail app startup. Same pattern applies to `organization_id` parameters with `enforce_organization_access`. Routes that don't take a tenant identifier but should (background-job-triggered routes with implicit tenancy from the user) are the harder class — those are caught by the integration test pattern below. The audit produces a clear failure message naming the offending route, so a missed access check is impossible to merge.

2. **Integration test pattern.** Every authenticated endpoint test has a "second user from different org cannot access this resource" case. Test fixture provides `user_a_in_org_1` and `user_b_in_org_2`; for any endpoint that returns or mutates resource owned by `user_a`, assert `user_b` gets 403 (or 404 if we want to avoid leaking existence). This is enforced by a custom pytest marker (`@pytest.mark.tenancy_isolated`) that fails the test suite if an authenticated endpoint test exists without the cross-tenant case.

The combination catches both the static and dynamic cases. Cheap to implement in 1a, expensive to retrofit later when there are hundreds of routes.

### 7.20 Phase 1 — explicit out of scope

- Real-time / sub-daily refresh (daily pull is the ceiling).
- Auto-execution of reallocations.
- Ad-set or creative-level performance analysis.
- MMM (Phase 2).
- Audience overlap / saturation analysis.
- MTA modeling.
- Server-side conversion tracking / CAPI configuration.
- A/B test or experiment management.
- Cross-client benchmarking.
- Plan generation from brief.
- DV360 / The Trade Desk connectors (Phase 4 if customer demand warrants).
- "Blended" third allocation mode.
- Public-facing accuracy reporting.
- Lift test design.
- Agentic auto-trading.
- Multi-model BYOK.
- Deep CSV ingestion (offline conversions, CRM) — Phase 2.
- Creative-level taxonomy.
- Custom SAML SSO and Layer 3 white-label (Enterprise; Phase 4).
- Self-serve Enterprise tier — Phase 1-3 Enterprise deals scoped as paid custom work.

### 7.21 Phase 1 — known risks and mitigations

- **Design partner not committed by Phase 1a week 4.** See §5.7 failure mode response.
- **Plan format wildness.** AI parser + templates + human confirm + rejected-rows panel + plan versioning.
- **Taxonomy schema drift.** Versioned `ClientTaxonomy`, audit log, no retroactive re-labeling.
- **Reallocation suggestions wrong in obvious ways early.** Three options, math always shown, taxonomy pooling respected, never "we recommend."
- **GA4 / platform conversion mismatches.** Evidence column, reconciliation factor inline.
- **Cross-market suggestion blindness.** Market constraints, context-check, justification required.
- **API connector flakiness.** Idempotent upserts, audit log, manual re-run, connector health surface, proactive token refresh, reauth flow with explicit notifications.
- **GA4 quota exhaustion.** Quota-budgeted scheduling, backfill paced over multiple days.
- **LLM-dependent surfaces failing on Monday morning.** Explicit degraded-mode designs (§7.17). Defense kit never blocks on LLM. Drift explanations have placeholders. Plan parser falls back to templates.
- **Postgres schema retrofitting.** All Phase 2/4 tables provisioned in Phase 1a.
- **Auth/authorization bugs.** Middleware enforcement, integration tests.
- **White-label complexity at Phase 1c.** Custom domain via Vercel API or Caddy; SES for email-from. Test end-to-end with design partner before opening tier publicly.
- **Daily pull settling visual misread by clients.** Org-level toggle, per-client override.
- **BYOK key validation false-positive.** Detect 401/403/402 from customer key, surface in workspace UI, fall back to MixSight key if `llm_byok_fallback_enabled`.
- **Empty-state coverage gaps.** Phase 1a includes empty-state tests for backfill-in-progress, partial-week, zero-spend, zero-conversion scenarios.

**The cut-of-last-resort.** If Phase 1c is slipping past week 6, the current-week view (§7.16) is the right thing to cut. The weekly snapshot covers the core Monday-morning use case; the mid-week check-in is a nice-to-have. Document this decision in advance so it doesn't have to be re-litigated under deadline pressure.

### 7.22 Phase 1 success criteria

- 3 paying agencies at $1,500-3,500/month each (one of which may be the converted design partner at $999).
- ≥1 agency with 3+ active workspaces.
- ≥1 white-labeled deployment in production with custom domain.
- ≥1 documented case where the evidence column changed an AM's recommendation.
- ≥1 documented case where the taxonomy filter / objective-type-aware drift surfaced an issue that channel-rollup would have hidden.
- ≥1 customer using BYOK actively.
- Historical backfill verified working: ≥3 clients with 12+ months of clean weekly data ingested per platform per market, surfaced in the data substrate completeness panel as MMM-eligible for Phase 2 launch.
- Daily refresh running stably for ≥30 days across all paying customers, with rare-or-no SLA breaches.
- ≥1 connector reauth event handled successfully in production (via the proactive refresh or admin-triggered flow).
- ≥1 LLM-degraded-mode incident handled gracefully (e.g., Anthropic transient outage) without blocking customer workflow.
- Single design-partner agency willing to be a public reference, with a quotable testimonial.
- Pricing tier mix observed and documented (per §4.3 Test 1).
- BYOK adoption rate observed (per §4.3 Test 2 — partial data, full data in Phase 2).
- Total ARR run-rate: $90K-$130K.

---

## 8. Phase 2 — The modeling layer (Months 8-15)

**Target duration:** 11-13 weeks of focused work.

### 8.1 Goal

Add modeled contribution as the third indicator in the evidence column, using a hierarchical Bayesian model. Incrementality results as fourth indicator. Deep CSV ingestion. SOC 2 Type I.

The multi-market angle is the unlock. Phase 1's backfill ensures most onboarded clients are MMM-eligible the moment Phase 2 ships.

### 8.2 Modeling approach

**Engine: pluggable.** Phase 2a ships PyMC-Marketing. Phase 2b/2c evaluates Meridian.

**Model components:**
- Geometric adstock (per-channel decay parameter).
- Hill function saturation (half-saturation point and shape per channel).
- Fourier seasonality.
- Per-market promotional event flags from `PromotionalEvent`.
- Macro controls: Google Trends, holidays, optional weather/CPI.
- Hierarchical structure: per-channel coefficients pool across markets; market intercepts independent. Where taxonomy provides additional structure (separate product lines), additional pooling layers added when data supports.

**Refit cadence:** weekly background job. 30-90 min. Asynchronous.

### 8.3 Sub-phase sequencing

#### Phase 2a — Plumbing + deep CSV + SOC 2 kickoff (3 weeks)

- SOC 2 Type I engagement with Vanta or Drata.
- Promotional calendar UI (replaces basic 1c entry form).
- Macro signal ingestion: Google Trends, holidays.
- `ContributionFit` table, job runner stub.
- Modeling-engine interface defined.
- Deep CSV ingestion for offline conversions, in-store sales, CRM data.
- **Self-serve data export and deletion endpoints implemented** (§6.6).

#### Phase 2b — Single-market model + Meridian spike (3 weeks)

- PyMC-Marketing integration. End-to-end fit on one market.
- Diagnostics UI: trace plots, posterior predictive checks, residuals.
- Confidence flagging: CI width, sample-size threshold.
- Meridian feasibility spike (2 days). If outputs in tolerance and API stable, plan switch.

#### Phase 2c — Hierarchical multi-market + engine decision (3 weeks)

- Pooling structure: channels pool across markets, market intercepts independent.
- Refit-time optimization: caching, partial re-fits, queue + dedicated worker.
- Multi-market diagnostics UI.
- Weekly auto-refit cron.
- Engine decision (Meridian or PyMC-Marketing default).

#### Phase 2d — Phase 1 integration + incrementality intake (2 weeks)

- Marginal ROAS curve extraction from posterior at each channel's current spend.
- Phase 1 reallocation engine v2: replaces step 5 (Project impact) with curve-based projection. CIs from posterior samples.
- Reallocation suggestions show projected impact as interval, not point.
- Evidence column gets third indicator (model contribution with credible interval).
- Incrementality intake UI. AM uploads geo holdout, platform-native lift, brand lift studies. Surfaced as fourth evidence-column indicator. Calibrates priors on next refit.

### 8.4 Data substrate built in Phase 1 for Phase 2 use

Phase 1's connector layer backfills aggressively (§7.14) and refreshes daily. By the time Phase 2 ships:

- Actuals at full granularity: 24-36 months of weekly data per channel per market on every onboarded client.
- Taxonomy labels applied to all actuals via `CampaignLabelRule`.
- PromotionalEvent: only Phase 1 capture not backfillable. Sparse coverage acceptable for first fit.
- MacroSignal: Google Trends backfilled at Phase 2 start.
- Plan history: all versions retained.
- RecommendationLog: every reallocation suggestion logged with prediction from Phase 1a.
- Offline conversions / CRM data (Phase 2 onboarding): deep CSV, mapped to taxonomy.

### 8.5 Phase 2 risks and out of scope

**Risks.** Identifiability, calibration without incrementality, refit performance, result instability, engine swap complexity, SOC 2 timeline slippage, taxonomy pooling layer increasing parameter count when data sparse.

**Out of scope.** Calibrated MMM beyond simple incrementality calibration (Phase 4+). Geo-level modeling within markets. Audience or creative-level decomposition. MTA fusion. Custom Bayesian model architecture. Lift test design.

### 8.6 Phase 2 success criteria

- 8+ paying agencies, 25+ active workspaces.
- ARR run-rate $300K-$450K.
- Modeling layer running in production for ≥3 clients.
- Incrementality results ingested for ≥2 clients.
- SOC 2 Type I report issued.
- ≥1 client where the model contribution indicator changed an AM's reallocation decision.
- ≥1 customer onboarded in Phase 2 reaching MMM-eligible status within 48 hours of platform authentication.
- ≥1 client using deep CSV ingestion in modeling.
- Pricing tests 1-3 fully evaluated; pricing structure either confirmed or restructured by end of Phase 2.

---

## 9. Phase 3 — Forecasting, reforecasting & lift test design (Months 15-23)

**Target duration:** 9 weeks (without optimization), 12 weeks (with optimization).

### 9.1 Goal

Three AM use cases:
- Pre-flight forecast (plan justification).
- In-flight forecast (trajectory monitoring).
- On-demand reforecast (reaction to material change).

Plus geo holdout test design.

### 9.2 Components

- **Forward-applied contribution model.** Posterior predictive sampling.
- **External signal forecasting.** Future Google Trends short-horizon (statsforecast).
- **Backtest framework.** Walk-forward backtest per model version.
- **Versioned forecasts.** Every run writes a new `ForecastRun` (immutable, append-only).
- **Forecast-vs-forecast diff view.** Visual diff (two trajectories with CI ribbons, per-channel contribution shift). LLM-generated causal narrative deferred to Phase 3e once backtest data validates attributions are stable. Phase 3c ships visual diff only.
- **Manual reforecast triggers.** UI button. Auto-triggered by plan version change, reallocation execution, MMM refit completion.
- **Scenario modeling UI.** "What if I shift $50K from US Meta to UK Google in weeks 5-8?"
- **Geo holdout test design.** AM specifies channel, candidate market pairs, hypothesized effect size, target power. MixSight returns recommended market matching with similarity score, required test duration, expected lift detectability range.

### 9.3 Sub-phase sequencing

- **Phase 3a — Forecast infrastructure (2 weeks).**
- **Phase 3b — Backtest framework (2 weeks).**
- **Phase 3c — Forecast UI + reforecasting + visual diff view (3 weeks).** Visual diff only; LLM narrative deferred.
- **Phase 3d — Scenario modeling + geo holdout design (2 weeks).**
- **Phase 3e — Budget optimization + LLM forecast diff narrative (3 weeks, optional).**

### 9.4 Phase 3 risks and out of scope

**Risks.** Forecast accuracy at long horizons; compound uncertainty; plan-as-input gaming; optimization-as-autopilot temptation; lift test design oversimplification; forecast version sprawl.

**Out of scope.** Real-time forecasting. Forecasting at creative or audience level. Forecast-driven autopilot bidding. Synthetic control or matched-market designs. Brand lift design (platform-native).

### 9.5 Phase 3 success criteria

- 15+ paying agencies, 40+ active workspaces.
- ARR run-rate $550K-$800K.
- Forecast in active use for ≥5 clients.
- ≥1 geo holdout designed in MixSight, run, and result calibrating MMM in same workspace.
- Optimization (if shipped) used in ≥2 client engagements.
- ≥3 clients using on-demand reforecasting in a typical quarter.

---

## 10. Phase 4 — Confidence calibration & network effects (Months 23-33)

### 10.1 Goal

Surface the calibration layer logging since Phase 1 day one. Add cross-customer benchmarks. Begin B2B-shaped data support.

### 10.2 Components

- **Calibration UI.** Per-channel, per-customer track record with recommendation-source attribution.
- **Calibration loop.** Future recommendations widen confidence ranges or downweight historically-wrong channels.
- **Per-customer accuracy export.**
- **Cross-customer benchmarking.** Privacy-preserving via differential privacy or federated aggregation.
- **Industry-vertical priors.** Pre-built per vertical, warm-starting new customers.
- **B2B-shaped data support.** Pipeline-stage attribution, longer windows, CRM integrations (Salesforce, HubSpot only).
- **Additional connectors.** LinkedIn Ads, Reddit, programmatic via DV360.
- **Layer 3 white-label.** Custom legal entity, data residency, custom SAML SSO. Self-serve Enterprise tier opens.

### 10.3 Phase 4 risks and constraints

- Calibration data volume — Phase 1's logging from day one means the clock starts at onboarding.
- Privacy-preserving aggregation correctness — engage privacy engineer for 4-6 weeks.
- Cross-customer benchmark cold-start — vertical-level benchmarks need ~10 customers per vertical.
- B2B integration scope creep — Salesforce + HubSpot only.

### 10.4 Phase 4 success criteria

- 25-30 paying customers, 70+ active workspaces.
- ARR run-rate $1.2M-$1.7M.
- Calibration UI in active use for ≥10 clients.
- Cross-customer benchmarks live in ≥2 verticals.
- ≥3 B2B customers demonstrating product fit.
- SOC 2 Type II issued.
- Self-serve Enterprise tier with first paying customer.

---

## 11. Phase 5+ — Future direction

- Auto-execution with strict guardrails.
- International expansion (UK first, then EU, then APAC).
- API access and embeddability.
- Advanced incrementality designs (synthetic control, matched-market, switchback).
- Multi-model BYOK.
- Public methodology documentation as customer-facing trust documentation.
- Plan generation from brief.
- Creative-level or audience-level analysis surfaces.

---

## 12. Honest timeline summary

| Phase | Duration | Notes |
|---|---|---|
| Phase 1a — End-to-end skeleton | 4 weeks | One client, one market, Meta only. Design partner committed by week 3. |
| Phase 1b — Multi-market + dual mode + taxonomy + parser + templates | 5-6 weeks | Multi-market end-to-end; single-market 12-15 min onboarding |
| Phase 1c — Connectors + daily refresh + reauth + LLM degraded ops + white-label + BYOK + billing | 5-6 weeks | First paying customer |
| **Phase 1 total** | **14-17 weeks (16-19 with buffer)** | First $90-130K ARR |
| Settling period | 4-8 weeks | Real weekly use; MMM-readiness verified; pricing tests evaluated |
| Phase 2a — Plumbing + deep CSV + SOC 2 kickoff + data export/deletion | 3 weeks | |
| Phase 2b — Single-market model + Meridian spike | 3 weeks | |
| Phase 2c — Hierarchical multi-market + engine decision | 3 weeks | |
| Phase 2d — Phase 1 integration + incrementality intake | 2 weeks | |
| **Phase 2 total** | **11 weeks** + SOC 2 in parallel | $300-450K ARR |
| Phase 3a — Forecast infrastructure | 2 weeks | |
| Phase 3b — Backtest framework | 2 weeks | |
| Phase 3c — Forecast UI + reforecasting + visual diff | 3 weeks | |
| Phase 3d — Scenario modeling + geo holdout design | 2 weeks | |
| Phase 3e — Budget optimization + LLM forecast narrative (optional) | 3 weeks | |
| **Phase 3 total** | **9 weeks (12 with optimization)** | $550-800K ARR |
| Phase 4 — Calibration + benchmarks + B2B + Layer 3 white-label | ~10 months | $1.2-1.7M ARR |

End-to-end through Phase 3 (no optimization): **~10 months of focused build**, plus settling time. Through Phase 4: **~33 months**. Phase 1 still feasible at side-project pace with discipline; Phase 2 onward realistically requires founder full-time and at least one engineering hire.

---

## 13. What we explicitly cut from prior versions

From v2.1:
- MMM in Phase 1 (engineering scope and positioning, not data scarcity).
- Triangulation View as a separate primary surface.
- "First triangulation system" framing.
- "Category-defining" language in external positioning.
- Public-facing accuracy reporting as a marketing feature.
- Open-protocol publication.
- Real-time / sub-daily refresh.
- Confidence calibration as a Phase 3 marketing message (Phase 4).
- DV360/TTD in Phase 1 connectors.
- Lift test design in Phase 2.
- The 32-month "becoming the standard" promise.

From v3.0:
- "New clients don't have 26+ weeks of data" reasoning (corrected v3.1).

From v3.1:
- "Yesterday only" daily pull framing (corrected v3.2 to trailing 7-day).
- Flat plan structure (taxonomy first-class in v3.2).
- Implicit assumption that AI parser is the only ingestion path (templates added v3.2).

From v3.2:
- Per-(client, market, platform) credential model implied in v3.2 §7.14 (corrected v3.3 to organization-level OAuth + per-(client, market) ad account mapping).
- Implicit assumption that LLM-dependent surfaces are reliable (v3.3 specifies degraded-mode for plan parser, drift explanations, defense kit narrative).
- Implicit "15-minute onboarding" claim without step-by-step flow (v3.3 specifies two onboarding flows with realistic time accounting).
- Implicit assumption that Phase 1 ICP is obvious (v3.3 specifies §2.5 with phase-by-phase ICP).
- Pricing presented as settled (v3.3 specifies §4.3 validation tests with triggers).
- Data deletion policy unspecified (v3.3 specifies §6.6).
- Empty states unspecified (v3.3 specifies §7.18).
- Connector reauth lifecycle unspecified (v3.3 specifies in §7.14).
- Support model unspecified (v3.3 specifies §4.4).
- Design-partner program unspecified beyond "we should have one" (v3.3 specifies §5.7).

---

## 14. Glossary

- **AM.** Account Manager. Primary user.
- **AuditLog.** Append-only log of every mutation: who did what to which entity when, with before/after state. 7-year retention with anonymization at customer deletion. Surfaced for export in Phase 1c+ to admin role.
- **EncryptedSecret.** Centralized table for encrypted credential storage (OAuth tokens, BYOK API keys). Supports key rotation via `key_version`. Referenced by FK from owning rows.
- **MacroSignal.** Per-market signal data (Google Trends, holidays, weather, CPI) consumed by Phase 2 modeling. Table provisioned Phase 1a, populated from Phase 2a.
- **DSP.** Demand-Side Platform (DV360, The Trade Desk). Out of Phase 1 scope.
- **Flight.** Period a campaign is scheduled to run.
- **Plan.** Agreed media spend allocation across channels and markets for a defined period.
- **Actuals.** What was actually spent and realized, pulled from each platform on three schedules.
- **Pacing.** Relationship between actual and planned spend at a given point in flight.
- **Drift.** Deviation between actual and planned. Formula branches on `objective_type`.
- **Reallocation suggestion.** Proposal to shift budget from donor to receiver, respecting taxonomy pooling.
- **Scope (of a reallocation).** Within/cross × market/channel.
- **Mode A / Platform-native.** Each channel evaluated using its own platform's reporting.
- **Mode B / Cross-platform.** All channels evaluated using a unified source of truth.
- **Evidence column.** The inline UI element on every pacing row showing platform vs cross-platform indicators (Phase 1) and modeled contribution + incrementality (Phases 2-3).
- **Reconciliation factor.** Per-channel-per-market historical ratio of GA4 conversions to platform-reported.
- **Adstock.** Carryover effect of media spend on KPI in subsequent weeks.
- **Saturation.** Diminishing returns of additional spend on the same channel.
- **Hierarchical model.** Bayesian model where parameters pool across groups.
- **Marginal ROAS.** Expected return on next dollar of spend.
- **Source of truth.** The configured conversion source treated as authoritative.
- **Defense kit.** The branded, white-labeled one-pager artifact.
- **Connector health surface.** First-class status route showing per-platform pull health.
- **Recommendation log.** Append-only log of every reallocation suggestion.
- **Calibration over time.** Phase 4 feature surfacing per-channel per-customer accuracy of MixSight's predictions.
- **Modeling engine.** Pluggable MMM implementation behind a stable contract.
- **White-label tier.** Layered branding model.
- **Plan taxonomy.** Per-client structured schema of dimensions.
- **ClientTaxonomy.** DB entity holding a client's taxonomy schema.
- **CampaignLabelRule.** Rule mapping campaign names/IDs to taxonomy labels.
- **Objective_type.** Special taxonomy dimension. Drives drift formula and reallocation pooling.
- **Plan template.** Excel + taxonomy + label rules combo. Adopting a template adopts its taxonomy.
- **Daily refresh.** Trailing 7-day rolling re-fetch at 6 AM per-market local time.
- **Weekly deep refresh.** Sunday-night trailing 90-day re-fetch.
- **Monthly deep refresh.** First-of-month trailing 13-month re-fetch.
- **"Still settling" treatment.** Visual styling on trailing 3 days. Default on, configurable.
- **Current week view.** Mid-week dashboard with live numbers, no status, no recommendations.
- **Weekly snapshot view.** Monday surface, frozen, with status, reallocations, defense kit.
- **BYOK.** Bring Your Own Key. Customer provides Anthropic API key. Per-workspace credit applied.
- **ForecastRun.** Append-only entity capturing every forecast execution.
- **Reforecast.** On-demand or event-triggered re-execution of forecast.
- **Restatement.** Platform-side revision of previously-reported numbers. Caught by trailing-window pulls.
- **ConnectorAuth.** Organization-level OAuth credential per (organization, platform).
- **AdAccountMapping.** Per (market, platform) mapping to a specific platform-side ad account, referencing a ConnectorAuth.
- **ConnectorAuthEvent.** Audit-log entity capturing every credential lifecycle event.
- **Reauth-needed state.** Distinct from connector-failed; means token expired/revoked, requires admin to re-OAuth.
- **Templated fallback narrative.** Default text used in defense kit when LLM narrative generation fails. Defense kit never blocks on LLM.
- **Insufficient data status.** Pacing row state when <7 days of data or <30 conversions. Excluded from drift detection and reallocation candidates.
- **Partial week snapshot.** First snapshot for a newly-onboarded client, generated even if onboarded mid-week. `is_partial_week = true`.
- **Design partner.** Phase 1 reference customer with privileged access, custom pricing, and direct founder relationship in exchange for feedback and reference rights.
- **ICP.** Ideal Customer Profile. Different per phase; documented in §2.5.

---

## 15. Document maintenance

This scope is the baseline for engineering. Material changes require explicit decision and re-publication.

**Changelog:**
- v3.4 (May 2026) — Engineering readiness. Three gaps closed during Day 0 setup: (1) `MacroSignal` entity formally specified in §7.4 (was referenced in §8.4 but never defined as a table); (2) `AuditLog` entity formally specified in §7.4 (was referenced in §7.19 but never defined); (3) database migration default conventions added to §6.2 (UUID generation, monetary precision, timestamp handling, JSONB usage, soft-delete patterns, index conventions, constraint naming) — these were implicit in v3.3, are now explicit defaults that don't need to be re-asked per migration. Also: tenancy test harness formally specified in §7.19 (app-startup decorator audit + integration test pattern with cross-tenant isolation marker, both shipped in Phase 1a, both run in CI from week 1). Also: `EncryptedSecret` entity added to §7.4 to make the FK pattern referenced throughout the connector and BYOK specs concrete. Also: Clerk role sync semantics formalized in §7.19 (Clerk = auth source of truth, DB = authz source of truth, JWT for fast path, DB re-check for sensitive operations, webhook out-of-order handling). Phase scope and timeline unchanged.
- v3.3 (May 2026) — Operational readiness. Eight specifications added or expanded: ICP refinement by phase, design-partner program, onboarding flows, empty states, connector lifecycle, LLM degraded operation, pricing validation, data lifecycle, support model. Connector credential model corrected from per-(client, market, platform) to organization-level OAuth + per-(client, market) ad account mapping.
- v3.2 (May 2026) — Six post-v3.1 additions: maximum-available historical backfill with quota-safe pacing plus CSV ingestion; plan taxonomy as first-class Phase 1 capability; BYOK Claude with credit economics; plan templates alongside parser; daily next-day data refresh with platform-honest freshness UX; on-demand reforecasting with versioned ForecastRun and forecast-vs-forecast diff view. Phase 1 timeline stretched to 14-17 weeks.
- v3.1 (May 2026) — Backfill correction. v3.0 reasoning that "new clients don't have 26+ weeks of data" was wrong: platform APIs support multi-year historical backfill. Connector spec added 24-month backfill on first authentication.
- v3.0 (May 2026) — Synthesis of v1.0 (pacing) and v2.1 (triangulation). MMM moved to Phase 2; triangulation reframed as inline evidence column; white-label moved to Phase 1c; TikTok replaces DV360/TTD in Phase 1; pricing tiers defined; SOC 2 Type I in Phase 2; recommendation logging from day one; calibration UI ships Phase 4.
- v2.1 — Triangulation conviction version. Superseded.
- v1.0 — Initial pacing scope. Superseded.
