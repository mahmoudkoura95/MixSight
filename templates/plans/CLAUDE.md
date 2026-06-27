# Plan template conventions

Templates are the Phase 1b fallback for the AI plan parser and the Starter-tier offering (Starter has templates only, no parser).

## The triple

Every template is **three files** in a directory:

```
templates/plans/<template-name>/
├── plan.xlsx          # The structural template AMs fill in
├── taxonomy.json      # The ClientTaxonomy seeded when this template is adopted
└── label_rules.json   # The CampaignLabelRule starter set
```

Adopting a template adopts all three. Forkable per-organization.

## Template set (Phase 1b)

1. **`single-market-single-channel/`** — Google Ads only, monthly budgets, conversions objective. Simplest case.
2. **`multi-channel-single-market/`** — Meta + Google + TikTok, single market, mixed objectives.
3. **`multi-market-multi-channel-product-lines/`** — the canonical fashion/DTC client. Multiple markets, multiple product lines.
4. **`retail-promo-heavy/`** — explicit promotional event columns. For clients running heavy seasonal calendars.
5. **`b2b-shaped/`** — Phase 4 readiness; ships now to avoid retrofit. Pipeline-stage attribution columns, longer windows.

## `plan.xlsx` structure

Columns required across all templates:
- `market_code` (matches `Market.code`)
- `channel` (meta / google_ads / ga4 / tiktok / other)
- `campaign_label` (human-readable name, used as fallback when no CampaignLabelRule matches)
- `period_start`, `period_end`
- `planned_spend_local`
- `objective_type` (conversions / traffic / reach / engagement / video_views / app_installs / leads)
- `kpi_target` (numeric, units depend on objective_type)
- `kpi_target_efficiency` (CPA / CPC / CPM / etc., depends on objective_type)

Plus dimension columns matching the template's taxonomy (e.g., `product_line`, `audience_segment`).

## `taxonomy.json` structure

Matches the seeded `ClientTaxonomy.dimensions` schema. See SCOPE.md §7.5 for the default. Each template includes the dimensions it expects, with sensible defaults.

Example fragment for the canonical DTC template:

```json
{
  "objective_type": {
    "values": ["conversions", "traffic", "reach"],
    "default": "conversions",
    "drives_drift_formula": true,
    "drives_reallocation_pooling": true,
    "required_per_plan_line": true
  },
  "product_line": {
    "values": ["mens", "womens", "kids", "accessories"],
    "drives_reallocation_pooling": true,
    "required_per_plan_line": true
  },
  "audience_segment": {
    "values": ["prospecting", "remarketing", "lookalike", "branded"],
    "drives_reallocation_pooling": false,
    "required_per_plan_line": false
  }
}
```

## `label_rules.json` structure

Starter set of `CampaignLabelRule` rows. Documented naming convention the template assumes. Example fragment:

```json
[
  {
    "rule_type": "regex",
    "priority": 100,
    "rule_config": {"pattern": "^BRX_(MENS|WOMENS|KIDS|ACCS)_(PROSP|RTG|LAL|BRAND)_(META|GOOGLE|TIKTOK).*$"},
    "label_assignments": {
      "product_line": "$1",
      "audience_segment": "$2",
      "channel": "$3"
    }
  },
  {
    "rule_type": "prefix_match",
    "priority": 200,
    "rule_config": {"prefix": "RT_"},
    "label_assignments": {"audience_segment": "remarketing"}
  }
]
```

## What templates do NOT do

- **No model assumptions.** Templates are about plan structure, not modeling parameters.
- **No connector configuration.** Connectors are organization-level (§7.14); templates don't touch them.
- **No retroactive re-labeling.** Adopting a template applies forward. Historical actuals keep their existing labels.
- **No promotional event seeding.** Templates may declare expected promotional events as guidance text, but the events themselves are entered per-client via the promotional calendar.

## Versioning

Templates are versioned (`templates/plans/<name>/v1/`, `v2/`...). Forking creates a new directory under the organization's scope; the original is unaffected. Adopting a versioned template records `Plan.template_id` and `Plan.template_version`.

## Phase 1b deliverable

3-5 templates shipped, all of them documented in `templates/plans/README.md`, all of them onboardable end-to-end in a test workspace.

Forkable per-organization (Phase 1c+ feature; in Phase 1b, templates are global).
