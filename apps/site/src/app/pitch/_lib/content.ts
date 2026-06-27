// All pitch page copy. Each constant carries a SCOPE.md citation in a comment
// so any claim is traceable. Do not add features that aren't in SCOPE.md.

export const heroCopy = {
  eyebrow: "Private preview · For design partners",
  // §7.1 north star
  headline: "The Monday morning workflow",
  headlineAccent: "for media agencies.",
  // §2.1 + §7.1
  subhead:
    "Confidence in thirty minutes. A defense-ready one-pager at the end. Evidence on every row, not a footnote. Built around the way your AMs actually work.",
  scrollCueLabel: "How the next 33 months unfold",
};

export const problemCopy = {
  // §2.1
  headline: "Sound familiar?",
  intro:
    "Every Monday morning at every paid media team in every agency, the same routine.",
  before: {
    label: "Today",
    duration: "≈ 4 hours",
    steps: [
      "Pull numbers from Meta Ads Manager",
      "Pull numbers from Google Ads",
      "Pull GA4 conversions",
      "Pull TikTok",
      "Reconcile the disagreements (skipped — pick a favorite)",
      "Build the pacing pivot in Google Sheets",
      "Re-do the math after the planner reshuffles",
      "Draft a summary, color the cells, attach to the email",
      "Send. Walk into the 11am call hoping no one drills in.",
    ],
  },
  after: {
    label: "With MixSight",
    duration: "≈ 30 minutes",
    steps: [
      "Open last week's snapshot",
      "Read the auto-drafted summary",
      "Skim three reallocation options with confidence intervals",
      "Edit the narrative paragraph for tone",
      "Click 'Generate defense kit'",
      "Send the branded PDF to the client",
      "Walk into the 11am call with the artifact in hand",
    ],
  },
};

// §2.4 differentiators — what MixSight owns.
export const differentiators = [
  {
    id: "evidence",
    // §2.4 + §7.9
    title: "Disagreement is the headline, not a footnote.",
    body: "Platform-native and cross-platform efficiency live side-by-side on every pacing row. A range bar shows agreement; click expands the methodology. AMs engage with disagreement instead of picking a favorite.",
    mockup: "DisagreementBar",
    cite: "§2.4 · §7.9",
  },
  {
    id: "defense-kit",
    // §2.4 + §7.13
    title: "A named, white-labeled artifact — not a report export.",
    body: "The defense kit is what the AM walks into the 11am client meeting holding. Agency logo. Agency colors. Custom domain. Editable narrative. Built so the client thinks it's bespoke software.",
    mockup: "DefenseKitMini",
    cite: "§2.4 · §7.13",
  },
  {
    id: "options",
    // §3 + §7.10
    title: "Options with evidence. Never 'we recommend.'",
    body: "Top three reallocation suggestions, ranked with confidence intervals. The AM has context the tool doesn't. We surface choices; the AM decides.",
    mockup: "OptionsNotRecommendations",
    cite: "§3 · §7.10",
  },
  {
    id: "multi-market",
    // §7.11 + §7.12
    title: "Multi-market is a first-class axis. Not a retrofit.",
    body: "Per-market timezones drive the daily pull. Per-market currencies. Per-market attribution settings. Taxonomy-respecting reallocation constraints. From V1, not bolted on later.",
    mockup: "MultiMarketMap",
    cite: "§7.11 · §7.12",
  },
  {
    id: "freshness",
    // §7.16
    title: "Platform-honest freshness UX.",
    body: "Weekly snapshot is the frozen Monday artifact. Current week view is directional, with the trailing 3 days visually muted as 'still settling.' AMs don't mistake intraday wobble for real drift.",
    mockup: "FreshnessUXSplit",
    cite: "§7.16",
  },
  {
    id: "audit",
    // §7.13 + §7.4
    title: "Plan changes are audited and surfaced to clients.",
    body: "Every revision logged. The defense kit shows what changed and when. Clients see strategy evolve, not just the latest snapshot. Trust compounds.",
    mockup: "PlanChangeTimeline",
    cite: "§7.4 · §7.13",
  },
  {
    id: "calibration",
    // §10 + §7.10 step 11
    title: "Track record from day one.",
    body: "Every reallocation suggestion logged at creation — predicted vs. observed. By Phase 4, the tool can show its own accuracy by channel, by customer, by vertical. Honest about its limits.",
    mockup: "CalibrationGrowingChart",
    cite: "§7.10 · §10.2",
  },
];

// §7.1–§7.22 Phase 1 — The Wedge
export const phaseOne = {
  number: 1,
  label: "Phase 1",
  months: "Months 1–7",
  // §7.1 north star
  northStar:
    "By end of Phase 1, an AM walks into a Monday client meeting with a defense-kit one-pager — branded, defensible, edited, sent — within thirty minutes.",
  subhead:
    "The wedge. The first thing a design partner uses on a real client. Three surfaces (weekly snapshot, current week view, defense kit). Four connectors (Meta, Google Ads, GA4, TikTok). Multi-market, taxonomy-aware, evidence-first.",
  mockupSections: [
    {
      mockup: "PacingTableMock",
      title: "Pacing table with evidence column",
      cite: "§7.2.2 · §7.9",
      callouts: [
        "Grouped by market and product line. Filtered by taxonomy.",
        "Spend drift + KPI drift, status computed against time-elapsed-in-flight.",
        "Evidence column shows both platform-native and cross-platform truth — paired indicators, range bar for agreement.",
        "Status: green, amber, red, critical, or insufficient_data — never wrongly red.",
      ],
    },
    {
      mockup: "EvidenceColumnExpanded",
      title: "Click a row → evidence drilldown",
      cite: "§7.9",
      callouts: [
        "Mode A: Platform-native efficiency (Meta's view of itself).",
        "Mode B: Cross-platform source-of-truth (GA4 attribution).",
        "Reconciliation factor with sample size and weekly history.",
        "Methodology footnote — defensible in front of any client.",
      ],
    },
    {
      mockup: "DefenseKitAssembly",
      title: "The Monday morning artifact",
      cite: "§7.13 · §7.17",
      callouts: [
        "Header (agency logo, week-ending date, client name)",
        "Editable narrative paragraph — falls back to template if LLM is unavailable.",
        "Pacing table excerpt, top 3 reallocation options, plan-change audit trail.",
        "Methodology footnote + next-week outlook. PDF via Playwright. Never blocks on LLM.",
      ],
    },
    {
      mockup: "ReallocationCards",
      title: "Three ranked reallocation options",
      cite: "§7.10",
      callouts: [
        "Donor (overpacing + underperforming) → Receiver (underpacing + overperforming)",
        "Scope tag: within-market / cross-market · same-product-line / cross-product-line",
        "Projected impact in objective-appropriate units (CPA, ROAS, CPC, CPM)",
        "Confidence band — Phase 2 replaces the heuristic with MMM-derived intervals.",
      ],
    },
    {
      mockup: "ConnectorHealthGrid",
      title: "Connector health per (client, market)",
      cite: "§7.14 · §7.15",
      callouts: [
        "Organization-level OAuth + per-(client, market) ad account mapping.",
        "Daily 6 AM (per-market local) · trailing 7-day rolling re-fetch.",
        "Weekly Sunday night · trailing 90-day deep re-fetch.",
        "Monthly first-of-month · trailing 13-month deep re-fetch.",
        "Backfill on first auth: 24–36 months historical in background. AM never waits.",
      ],
    },
    {
      mockup: "EmptyStateGallery",
      title: "First-experience empty states",
      cite: "§7.18",
      callouts: [
        "Backfill in progress, partial-week onboarding, plan not yet started, plan period ended, insufficient_data.",
        "Never 'come back next Monday.' Every state explains itself and shows what is available.",
        "First-experience is the most important experience. Empty states are not edge cases.",
      ],
    },
    {
      mockup: "FreshnessUXSplit",
      title: "Weekly snapshot vs. current week",
      cite: "§7.16",
      callouts: [
        "Weekly snapshot: frozen Monday artifact. Dated. Definitive.",
        "Current week: directional, intra-week. No reallocation suggestions (Wednesday data is too noisy).",
        "Trailing 3 days: 'still settling' visual treatment (muted color, dotted edge).",
        "'Data current as of 06:14 AM local' freshness stamp.",
      ],
    },
  ],
  wowMoments: [
    "“That's our evidence column?” — first time an AM sees Meta and GA4 diverge by 40% on a row that would have otherwise been called green.",
    "“We can white-label this?” — defense kit with agency logo, agency colors, custom domain. Clients think it's bespoke.",
    "“Thirty-minute Monday.” — done before the second coffee.",
    "“Monday morning even if the API goes down.” — defense kit generates without LLM. Templated narrative is the fallback.",
  ],
};

// §8.1–§8.6 Phase 2 — Modeling Layer
export const phaseTwo = {
  number: 2,
  label: "Phase 2",
  months: "Months 8–15",
  // §8.1
  northStar:
    "Add modeled contribution as the third indicator in the evidence column. Hierarchical Bayesian MMM in production. Incrementality as the fourth indicator.",
  subhead:
    "The depth layer. Phase 1 measures last week. Phase 2 explains it. Bayesian MMM with adstock, saturation, hierarchical pooling — pluggable engine, PyMC-Marketing first.",
  mockupSections: [
    {
      mockup: "EvidenceColumnFour",
      title: "Four indicators in the evidence column",
      cite: "§8.2 · §8.6",
      callouts: [
        "Platform-native (Phase 1)",
        "Cross-platform truth (Phase 1)",
        "Modeled contribution with credible interval (Phase 2)",
        "Incrementality result (geo holdout, platform-native lift) (Phase 2)",
        "Tight cluster = high confidence. Wide spread = real disagreement — actionable.",
      ],
    },
    {
      mockup: "MarginalROASCurve",
      title: "Marginal ROAS at current spend",
      cite: "§8.2",
      callouts: [
        "Phase 1 reallocation used point estimates. Phase 2 uses the marginal ROAS curve from the MMM posterior.",
        "Diminishing returns visible. 'Moving another $50K returns 3.8x, not 4x.'",
        "Projected impact reported as a credible interval, not a point estimate.",
      ],
    },
    {
      mockup: "MMMDiagnosticsPanel",
      title: "Modeling diagnostics — model honesty",
      cite: "§8.3",
      callouts: [
        "Trace plots, posterior predictive checks, residuals by week.",
        "Confidence flags: credible interval width, sample-size thresholds, model stability over time.",
        "Refit weekly in background. 30–90 minutes async. AM never waits.",
      ],
    },
    {
      mockup: "PromotionalCalendar",
      title: "Promotional calendar — known events as model inputs",
      cite: "§8.2",
      callouts: [
        "AM enters: 'Black Friday Nov 23-27, expected 2x lift.'",
        "Macro controls: Google Trends, holidays, optional weather/CPI.",
        "Per-market promotional flags. Per-channel adstock + Hill saturation. Fourier seasonality.",
      ],
    },
  ],
  wowMoments: [
    "“Our seasonality is baked out?” — August always down 30% from summer holidays, controlled for in reallocation.",
    "“Marginal ROAS at our current spend?” — answers a different question than average ROAS.",
    "“Confidence intervals on reallocation.” — decision-making with ranges, not points.",
  ],
};

// §9.1–§9.5 Phase 3 — Forecasting & Lift Test Design
export const phaseThree = {
  number: 3,
  label: "Phase 3",
  months: "Months 15–23",
  // §9.1
  northStar:
    "Pre-flight forecast (plan justification). In-flight forecast (trajectory monitoring). On-demand reforecast (react to material change). Geo holdout test design.",
  subhead:
    "From explaining last week to projecting next quarter. Versioned ForecastRun. Visual diffs between forecasts. Geo holdouts designed from the planning tool.",
  mockupSections: [
    {
      mockup: "ForecastChart",
      title: "Per-channel forecast trajectory",
      cite: "§9.1",
      callouts: [
        "Posterior predictive sampling — credible interval ribbons, not point estimates.",
        "External signal forecasting (future Google Trends) at short horizons.",
        "Backtest framework on historical holdout windows.",
      ],
    },
    {
      mockup: "ReforecastDiff",
      title: "Reforecast on news",
      cite: "§9.2 · §9.3",
      callouts: [
        "Manual trigger: 'Reforecast given current actuals.'",
        "Auto-triggers: plan version change, reallocation execution, MMM refit.",
        "Side-by-side diff: contribution shift annotated to its cause (competitor announcement, Trends shift).",
      ],
    },
    {
      mockup: "GeoHoldoutDesigner",
      title: "Geo holdout designed inside the planning tool",
      cite: "§9.2",
      callouts: [
        "Specify channel, candidate market pairs, hypothesized effect size, target power.",
        "Tool returns recommended market matching, required duration, detectable lift range.",
        "Once test runs, results calibrate the MMM on the next refit.",
      ],
    },
  ],
  wowMoments: [
    "“Reforecasting on news.” — Tuesday morning competitor announcement, click reforecast, see the new trajectory.",
    "“Forecasts with uncertainty.” — credible intervals are how real decisions get made.",
    "“Geo holdout from inside the tool.” — usually a separate project, now an in-product flow.",
  ],
};

// §10.1–§10.4 Phase 4 — Calibration & Network Effects
export const phaseFour = {
  number: 4,
  label: "Phase 4",
  months: "Months 23–33",
  // §10.1
  northStar:
    "Surface the track record. Add cross-customer benchmarks. Open B2B. 'The tool that knows its own limits' becomes the differentiator.",
  subhead:
    "Network effects. The reallocation log has been writing since Phase 1a day one — Phase 4 is when it pays off. Vertical-level benchmarks. Enterprise white-label. B2B-shaped data support.",
  mockupSections: [
    {
      mockup: "CalibrationDashboard",
      title: "The tool's own track record",
      cite: "§10.2",
      callouts: [
        "Per-channel, per-customer accuracy of past recommendations.",
        "'Meta reallocation suggestions over 3 months: predicted 8% improvement, actual 6.2%. Confidence downweighted by 8% next run.'",
        "Recommendation-source attribution: which came from heuristic_v1, model_v2.",
      ],
    },
    {
      mockup: "BenchmarkCards",
      title: "Vertical benchmarks — privacy-preserving",
      cite: "§10.2",
      callouts: [
        "Differential privacy / federated aggregation.",
        "'Your Meta ROAS: 42nd percentile among DTC fashion agencies.'",
        "Warm-start priors for new customers in a vertical.",
      ],
    },
    {
      mockup: "EnterpriseWhiteLabel",
      title: "Layer 3 white-label — enterprise",
      cite: "§10.2",
      callouts: [
        "Custom legal entity, data residency (US / EU), SAML SSO.",
        "Self-serve Enterprise tier opens.",
        "B2B-shaped data: pipeline-stage attribution, CRM integrations (Salesforce, HubSpot).",
      ],
    },
  ],
  wowMoments: [
    "“Tool that knows its own limits.” — calibration UI shows accuracy by channel, by customer. Clients trust tools that admit uncertainty.",
    "“Benchmarking against your cohort.” — competitive pressure inside the product. Improvement targets.",
    "“We go full enterprise here.” — SAML, custom domain, data residency. B2B agencies, regulated verticals.",
  ],
};

// §11 Beyond
export const beyondCopy = {
  label: "Beyond Phase 4",
  months: "Year 3 onward",
  northStar: "Category leader for performance marketing agencies.",
  items: [
    {
      title: "Auto-execution with guardrails",
      body: "Weekly reallocations execute on AM approval. The tool moves from advisory to operational — but only when the calibration record earns it.",
    },
    {
      title: "International expansion",
      body: "UK first, then EU, then APAC. Per-region data residency and SSO posture by default.",
    },
    {
      title: "Embeddable API",
      body: "Agencies embed pacing snapshots inside their own client portals. MixSight as the measurement substrate.",
    },
    {
      title: "Advanced incrementality designs",
      body: "Synthetic control, matched-market, switchback. Lift-test infrastructure that mid-tier agencies have never had access to.",
    },
    {
      title: "Plan generation from brief",
      body: "Brief + past performance → recommended spend allocation. The planning input itself becomes a MixSight surface.",
    },
    {
      title: "Public methodology",
      body: "The way we model, attribute, reconcile — published. Trust as a competitive moat.",
    },
  ],
};

// §4 Pricing
export const pricingCopy = {
  headline: "Pricing — transparent from day one",
  intro:
    "Per-seat + per-workspace subscriptions. LLM quota included with BYOK option. White-label as a tier jump, not a hidden surcharge.",
  tiers: [
    {
      name: "Starter",
      price: "$599",
      cadence: "/month",
      seats: "2 seats",
      workspaces: "3 workspaces",
      llm: "200 generations / workspace / month",
      whitelabel: false,
      blurb: "Solo operators and tiny teams trialing MixSight on one or two clients.",
    },
    {
      name: "Growth",
      price: "$1,499",
      cadence: "/month",
      seats: "5 seats",
      workspaces: "10 workspaces",
      llm: "500 generations / workspace / month",
      whitelabel: "Layer 1 (logo + colors)",
      blurb: "Working agencies with 5+ active clients. BYOK unlocks here.",
    },
    {
      name: "Agency",
      price: "$3,999",
      cadence: "/month",
      seats: "15 seats",
      workspaces: "30 workspaces",
      llm: "1,500 generations / workspace / month",
      whitelabel: "Layer 2 (custom domain + branded email)",
      blurb: "Established agencies running diversified rosters. Full white-label.",
      highlight: true,
    },
    {
      name: "Enterprise",
      price: "Custom",
      cadence: "",
      seats: "Custom seats",
      workspaces: "Custom workspaces",
      llm: "Negotiated",
      whitelabel: "Layer 3 (legal entity + data residency + SAML)",
      blurb: "B2B-shaped data, regulated verticals, dedicated infrastructure.",
    },
  ],
  byokNote:
    "BYOK option (Growth+): bring your own Anthropic API key. MixSight credits $200/workspace/month against your bill. Cost-sensitive customers get pricing power.",
};

// §5.7 Design partner program
export const designPartnerCopy = {
  eyebrow: "The ask",
  headline: "Be our founding design partner.",
  subhead:
    "One agency. Phase 1. We build alongside you, you tell us when we're wrong, and you become reference customer #1.",
  whatYouGet: [
    {
      title: "Agency-tier features — free through Phase 1",
      body: "$3,999/month retail value. Full feature set as it ships.",
    },
    {
      title: "$999/month locked rate after",
      body: "12-month commitment at Phase 1 completion. Design-partner-only pricing.",
    },
    {
      title: "White-label setup assistance",
      body: "Logo, colors, custom domain. We do the configuration with you.",
    },
    {
      title: "Direct founder access",
      body: "Slack, weekly call, custom feature priority for your workflow.",
    },
  ],
  whatWeAsk: [
    {
      title: "Weekly 30-min feedback through Phase 1",
      body: "Real-time signal. You tell us when we're wrong; we course-correct.",
    },
    {
      title: "Screenshot and quote rights",
      body: "For case study, sales material, marketing site. Final approval on every asset.",
    },
    {
      title: "Willingness to be public reference",
      body: "Phase 1 completion. Quotable testimonial.",
    },
    {
      title: "Two peer introductions",
      body: "Other agency owners. Warm intros only.",
    },
  ],
  timeline: [
    { week: "1a · Wk 3", label: "Commit · informal MOU signed" },
    { week: "1a · Wk 4", label: "Access · skeleton in your hands" },
    { week: "1b · Wk 1", label: "First real client loaded" },
    { week: "1c · Wk 4", label: "White-label live · reference-ready" },
  ],
  fitChecklist: [
    "5–25 person performance / DTC agency",
    "Multi-market roster (or aspirational)",
    "3–8 active client engagements",
    "Founder or head-of-paid is buyer + primary user",
    "Existing roster on Meta + Google + GA4 (TikTok a bonus)",
    "Timezone overlap with London",
  ],
};

export const founderCopy = {
  eyebrow: "Who's building this",
  headline: "Mahmoud Koura · founder · ex-agency operator",
  body: [
    "I've spent enough Monday mornings building pacing tables in Sheets that I'd like to stop. So would your team.",
    "MixSight is the tool I wish I'd had — built around the way AMs actually work, not the way dashboard tools wish they did. The roadmap is durable: Phase 1 wedge, Phase 2 modeling depth, Phase 3 forecasting, Phase 4 calibration. Every entity for Phase 2/4 is provisioned in Phase 1a — no retrofit later.",
    "If you're up for shaping the product, you'll get the founder's attention every week for the next seven months.",
  ],
  emailLabel: "Email me directly",
  email: "mahmoud@mixsight.ai",
  schedulerLabel: "Pick a time",
  // Replace this with the actual Cal.com / Calendly URL before sharing.
  schedulerUrl: "https://cal.com/mahmoudkoura/mixsight-design-partner",
};

export const footerCopy = {
  privacyStripe:
    "Private preview — shared in confidence with Brave Bison Agency. Not for redistribution.",
  lastUpdated: "June 2026",
  citation:
    "Every claim on this page is traceable to a section of SCOPE.md. The full specification is available on request.",
  citationLinks: [
    { label: "Phase 1 spec", section: "§7" },
    { label: "Phase 2 spec", section: "§8" },
    { label: "Phase 3 spec", section: "§9" },
    { label: "Phase 4 spec", section: "§10" },
    { label: "Pricing", section: "§4" },
    { label: "Design partner program", section: "§5.7" },
  ],
};

export const navSections = [
  { id: "top", label: "Top" },
  { id: "problem", label: "Problem" },
  { id: "different", label: "What's different" },
  { id: "phase-1", label: "Phase 1" },
  { id: "phase-2", label: "Phase 2" },
  { id: "phase-3", label: "Phase 3" },
  { id: "phase-4", label: "Phase 4" },
  { id: "beyond", label: "Beyond" },
  { id: "pricing", label: "Pricing" },
  { id: "partner", label: "The ask" },
  { id: "contact", label: "Contact" },
];
