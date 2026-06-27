// Realistic fake data for pitch mockups. Generic-but-credible multi-market DTC
// (SCOPE.md §2.5 default ICP). All numbers are illustrative.

export const agency = {
  name: "Lumen Studios",
  description: "5-person performance / DTC agency",
  location: "London + New York",
};

export type PacingRow = {
  client: string;
  market: "US" | "UK";
  channel: string;
  productLine: "Core" | "Premium" | "Seasonal";
  objectiveType: "conversions" | "traffic" | "reach";
  plannedSpend: number;
  actualSpend: number;
  spendDrift: number; // signed pct, e.g., 0.058 = +5.8%
  kpiUnit: "CPA" | "ROAS" | "CPC" | "CPM";
  planned: number;
  actual: number;
  kpiDrift: number;
  status: "green" | "amber" | "red" | "critical" | "insufficient_data";
  // Mode A: platform-native efficiency; Mode B: GA4 / cross-platform truth.
  modeA: number;
  modeB: number;
  modeDelta: number;
};

// Halcyon Apparel (DTC apparel, US + UK), Stratton Botanicals (DTC skincare, US).
export const pacingRows: PacingRow[] = [
  {
    client: "Halcyon Apparel",
    market: "US",
    channel: "Meta — Prospecting",
    productLine: "Core",
    objectiveType: "conversions",
    plannedSpend: 84500,
    actualSpend: 89300,
    spendDrift: 0.057,
    kpiUnit: "CPA",
    planned: 38,
    actual: 41,
    kpiDrift: 0.079,
    status: "green",
    modeA: 41,
    modeB: 44,
    modeDelta: 0.073,
  },
  {
    client: "Halcyon Apparel",
    market: "US",
    channel: "Google — Search",
    productLine: "Core",
    objectiveType: "conversions",
    plannedSpend: 52000,
    actualSpend: 40400,
    spendDrift: -0.223,
    kpiUnit: "ROAS",
    planned: 4.2,
    actual: 3.1,
    kpiDrift: -0.262,
    status: "critical",
    modeA: 3.1,
    modeB: 2.7,
    modeDelta: -0.129,
  },
  {
    client: "Halcyon Apparel",
    market: "UK",
    channel: "Meta — Prospecting",
    productLine: "Premium",
    objectiveType: "conversions",
    plannedSpend: 31000,
    actualSpend: 32100,
    spendDrift: 0.035,
    kpiUnit: "CPA",
    planned: 52,
    actual: 49,
    kpiDrift: -0.058,
    status: "green",
    modeA: 49,
    modeB: 53,
    modeDelta: 0.082,
  },
  {
    client: "Halcyon Apparel",
    market: "UK",
    channel: "TikTok — Video",
    productLine: "Seasonal",
    objectiveType: "reach",
    plannedSpend: 18000,
    actualSpend: 22800,
    spendDrift: 0.267,
    kpiUnit: "CPM",
    planned: 6.8,
    actual: 9.4,
    kpiDrift: 0.382,
    status: "red",
    modeA: 9.4,
    modeB: 9.4,
    modeDelta: 0,
  },
  {
    client: "Stratton Botanicals",
    market: "US",
    channel: "Meta — Remarketing",
    productLine: "Core",
    objectiveType: "conversions",
    plannedSpend: 26500,
    actualSpend: 26200,
    spendDrift: -0.011,
    kpiUnit: "ROAS",
    planned: 5.4,
    actual: 5.6,
    kpiDrift: 0.037,
    status: "green",
    modeA: 5.6,
    modeB: 4.9,
    modeDelta: -0.125,
  },
  {
    client: "Stratton Botanicals",
    market: "US",
    channel: "Google — PMax",
    productLine: "Premium",
    objectiveType: "conversions",
    plannedSpend: 38000,
    actualSpend: 30100,
    spendDrift: -0.208,
    kpiUnit: "ROAS",
    planned: 3.6,
    actual: 4.4,
    kpiDrift: 0.222,
    status: "amber",
    modeA: 4.4,
    modeB: 4.1,
    modeDelta: -0.068,
  },
];

export type ReallocationSuggestion = {
  rank: 1 | 2 | 3;
  donor: { client: string; market: "US" | "UK"; channel: string };
  receiver: { client: string; market: "US" | "UK"; channel: string };
  amount: number;
  scope: "within-market · same-product-line" | "cross-market · same-product-line" | "within-market · cross-product-line";
  projectedImpact: string;
  projectedRange: string;
  confidence: "high" | "medium" | "low";
  rationale: string;
};

export const reallocationSuggestions: ReallocationSuggestion[] = [
  {
    rank: 1,
    donor: { client: "Halcyon Apparel", market: "UK", channel: "TikTok — Video" },
    receiver: { client: "Halcyon Apparel", market: "UK", channel: "Meta — Prospecting" },
    amount: 4500,
    scope: "within-market · same-product-line",
    projectedImpact: "+92 conversions",
    projectedRange: "[+68 to +118] conversions",
    confidence: "high",
    rationale:
      "TikTok CPM +38% over 14d at flat reach growth. Meta CPA −6% with headroom on the prospecting audience.",
  },
  {
    rank: 2,
    donor: { client: "Stratton Botanicals", market: "US", channel: "Google — PMax" },
    receiver: { client: "Stratton Botanicals", market: "US", channel: "Meta — Remarketing" },
    amount: 6000,
    scope: "within-market · cross-product-line",
    projectedImpact: "+$28,400 revenue",
    projectedRange: "[+$19K to +$38K] revenue",
    confidence: "medium",
    rationale:
      "PMax ROAS overshooting plan with declining volume. Remarketing ROAS 5.6x stable; audience caps not yet hit.",
  },
  {
    rank: 3,
    donor: { client: "Halcyon Apparel", market: "US", channel: "Google — Search" },
    receiver: { client: "Halcyon Apparel", market: "UK", channel: "Meta — Prospecting" },
    amount: 8000,
    scope: "cross-market · same-product-line",
    projectedImpact: "+178 conversions",
    projectedRange: "[+110 to +250] conversions",
    confidence: "low",
    rationale:
      "Cross-market shift. Requires context check before defense kit inclusion — currency and audience overlap caveats.",
  },
];

export type EmptyState = {
  id: string;
  title: string;
  body: string;
  cite: string;
};

export const emptyStates: EmptyState[] = [
  {
    id: "backfill",
    title: "Historical data loading",
    body: "Full pacing view available in 6–12 hours. Going-forward pulls are already active.",
    cite: "§7.18 · §7.14",
  },
  {
    id: "partial-week",
    title: "First snapshot — partial week",
    body: "Based on 3 days of data. Full Monday experience available May 25, 2026.",
    cite: "§7.18",
  },
  {
    id: "pre-flight",
    title: "Plan hasn't started yet",
    body: "Plan period begins June 1. Pacing rows show planned values; actuals will populate as spend lands.",
    cite: "§7.18",
  },
  {
    id: "post-flight",
    title: "Plan period ended",
    body: "Snapshot frozen as of May 11, 2026. Defense kit available for the closing client review.",
    cite: "§7.18",
  },
  {
    id: "insufficient-data",
    title: "Insufficient data — not yet amber or red",
    body: "Campaign launched 3 days ago. Excluded from drift evaluation and reallocation until ≥7 days OR ≥30 conversions.",
    cite: "§7.18 · §7.8",
  },
];

// §8.2 Phase 2 modeling: marginal ROAS curve sample points (synthetic).
export const marginalROASCurve = {
  channel: "Meta — Prospecting (Halcyon US)",
  // (spend $K, ROAS) — diminishing returns past current spend.
  points: [
    { spend: 0, roas: 0 },
    { spend: 20, roas: 5.4 },
    { spend: 40, roas: 4.8 },
    { spend: 60, roas: 4.2 },
    { spend: 80, roas: 3.7 },
    { spend: 90, roas: 3.5 }, // current
    { spend: 100, roas: 3.3 },
    { spend: 120, roas: 2.9 },
    { spend: 150, roas: 2.5 },
  ],
  current: 90,
  unit: "ROAS",
};

// §9.1 Phase 3 forecasting: 8-week trajectory with credible interval ribbons.
export const forecastChart = {
  channel: "Meta — Prospecting (Halcyon US)",
  weeks: 8,
  // Each entry: { week, baseline, lo, hi, reforecast?, reforecast_lo?, reforecast_hi? }
  trajectory: [
    { week: 1, baseline: 38, lo: 35, hi: 41, reforecast: 38, reforecast_lo: 35, reforecast_hi: 41 },
    { week: 2, baseline: 40, lo: 36, hi: 44, reforecast: 39, reforecast_lo: 35, reforecast_hi: 43 },
    { week: 3, baseline: 42, lo: 37, hi: 47, reforecast: 39, reforecast_lo: 34, reforecast_hi: 44 },
    { week: 4, baseline: 45, lo: 39, hi: 51, reforecast: 38, reforecast_lo: 32, reforecast_hi: 44 },
    { week: 5, baseline: 47, lo: 40, hi: 54, reforecast: 36, reforecast_lo: 30, reforecast_hi: 43 },
    { week: 6, baseline: 48, lo: 40, hi: 56, reforecast: 35, reforecast_lo: 28, reforecast_hi: 43 },
    { week: 7, baseline: 48, lo: 40, hi: 57, reforecast: 36, reforecast_lo: 29, reforecast_hi: 44 },
    { week: 8, baseline: 49, lo: 40, hi: 58, reforecast: 38, reforecast_lo: 31, reforecast_hi: 45 },
  ],
  unit: "Weekly conversions (K)",
};

// §10.2 Phase 4 calibration: track record per channel.
export const calibrationRows = [
  {
    channel: "Meta — Prospecting",
    suggestions: 24,
    predicted: "+7.8%",
    actual: "+6.2%",
    accuracy: 0.94,
    nextConfidence: "−8%",
  },
  {
    channel: "Google — Search",
    suggestions: 19,
    predicted: "+5.1%",
    actual: "+4.7%",
    accuracy: 0.92,
    nextConfidence: "−4%",
  },
  {
    channel: "TikTok — Video",
    suggestions: 8,
    predicted: "+12.4%",
    actual: "+3.8%",
    accuracy: 0.69,
    nextConfidence: "−24%",
  },
  {
    channel: "Meta — Remarketing",
    suggestions: 17,
    predicted: "+4.1%",
    actual: "+4.3%",
    accuracy: 0.98,
    nextConfidence: "+2%",
  },
];

export const benchmarkCards = [
  {
    metric: "Meta ROAS",
    yourValue: "3.9x",
    percentile: 42,
    cohort: "DTC fashion · 12 agencies",
    median: "4.2x",
    direction: "below",
  },
  {
    metric: "Google Search CPA",
    yourValue: "$38",
    percentile: 78,
    cohort: "DTC fashion · 12 agencies",
    median: "$46",
    direction: "above",
  },
  {
    metric: "TikTok CPM",
    yourValue: "$9.40",
    percentile: 28,
    cohort: "DTC fashion · 12 agencies",
    median: "$7.10",
    direction: "below",
  },
] as const;

export const connectorHealth = [
  {
    platform: "Meta",
    market: "US",
    lastPull: "Today 06:14",
    nextPull: "Tomorrow 06:00",
    status: "healthy",
    backfill: "24 / 24 months",
  },
  {
    platform: "Google Ads",
    market: "US",
    lastPull: "Today 06:14",
    nextPull: "Tomorrow 06:00",
    status: "healthy",
    backfill: "24 / 24 months",
  },
  {
    platform: "GA4",
    market: "US",
    lastPull: "Today 06:14",
    nextPull: "Tomorrow 06:00",
    status: "healthy",
    backfill: "26 / 26 months",
  },
  {
    platform: "TikTok",
    market: "US",
    lastPull: "Today 06:14",
    nextPull: "Tomorrow 06:00",
    status: "healthy",
    backfill: "18 / 24 months",
  },
  {
    platform: "Meta",
    market: "UK",
    lastPull: "Today 06:00",
    nextPull: "Tomorrow 06:00",
    status: "healthy",
    backfill: "22 / 24 months",
  },
  {
    platform: "Google Ads",
    market: "UK",
    lastPull: "Today 06:00",
    nextPull: "Tomorrow 06:00",
    status: "reauth_due",
    backfill: "24 / 24 months",
  },
];

export const planChanges = [
  { date: "Apr 03", change: "Initial plan v1 ingested", author: "Auto" },
  { date: "Apr 14", change: "US Halcyon Core: +$8K Meta, −$8K Google (client request)", author: "AM" },
  { date: "Apr 24", change: "UK Halcyon Premium: launched TikTok line ($15K)", author: "AM" },
  { date: "May 06", change: "US Stratton Premium: PMax cap reduced to $35K (efficiency goal)", author: "AM" },
];
