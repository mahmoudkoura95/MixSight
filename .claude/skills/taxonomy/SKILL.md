---
name: taxonomy
description: Use this skill whenever working with ClientTaxonomy, CampaignLabelRule, plan ingestion, drift formula branching, or reallocation pooling in the MixSight project. Triggers include "taxonomy," "objective_type," "product_line," "audience_segment," "label rule," "campaign matching," "pooling," "dimensions," "plan template adoption." Encodes the SCOPE.md §7.5 taxonomy system as a first-class Phase 1 capability: per-client dimensions, versioned (no retroactive re-labeling), drives_drift_formula on objective_type, drives_reallocation_pooling on declared dimensions. Use this skill BEFORE touching taxonomy-related code.
---

# Taxonomy skill

Real plans have multiple product lines, mixed objective types, and rollup needs. Per §3 (locked) and §7.5, plan taxonomy is **first-class in Phase 1**. It drives:
- Drift formula (`drives_drift_formula` on `objective_type`).
- Reallocation pooling (`drives_reallocation_pooling` on declared dimensions, typically `product_line`).
- Filter bar on the pacing UI.

## The data model

```
ClientTaxonomy
├── client_id (FK)
├── dimensions (JSONB)
├── seeded_from_template (FK, nullable)
├── version
└── timestamps

CampaignLabelRule
├── client_id (FK)
├── market_id (FK, nullable for global rules)
├── rule_type (regex | prefix_match | lookup_table | explicit_assignment)
├── rule_config (JSONB)
├── label_assignments (JSONB)
├── priority (int)
└── active
```

Both versioned. Changing taxonomy or label rules **does not retroactively re-label historical actuals.** It applies forward only.

## The seeded default

Every new `Client` gets seeded with the default taxonomy if no template is adopted:

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

Per-dimension flags:
- `values`: list of valid values; empty `[]` means "open set, AM defines"
- `default`: fallback value
- `drives_drift_formula`: whether the drift formula branches on this dimension
- `drives_reallocation_pooling`: whether different values of this dimension cannot be paired in reallocation
- `required_per_plan_line`: whether every PlanLine must have this set

## Objective_type is special

It's the only dimension that drives the drift formula (§7.8):

| objective_type | KPI drift formula |
|---|---|
| conversions | CPA or ROAS |
| traffic | CPC or CTR |
| reach | CPM or unique reach |
| engagement | CPE |
| video_views | CPV |
| app_installs | CPI |
| leads | CPL |

Default value `conversions` if not specified. Parser is instructed to extract it when present.

## Label rules

Four rule types, evaluated in priority order. First match wins. Conflicts logged for AM review.

### regex
```json
{
  "rule_type": "regex",
  "rule_config": {"pattern": "^BRX_(MENS|WOMENS|KIDS)_PROSP_META.*$"},
  "label_assignments": {
    "product_line": "$1",
    "audience_segment": "prospecting"
  },
  "priority": 100
}
```

Capture groups can be referenced in `label_assignments` via `$1`, `$2`, etc.

### prefix_match
```json
{
  "rule_type": "prefix_match",
  "rule_config": {"prefix": "RT_"},
  "label_assignments": {"audience_segment": "remarketing"},
  "priority": 200
}
```

Simpler syntax for the same.

### lookup_table
AM uploads or maintains a CSV of `campaign_external_id → labels`. Stored in `rule_config` as a JSONB map.

### explicit_assignment
AM clicks a campaign in the pacing table and sets labels directly. `rule_config` carries the campaign external ID; `label_assignments` carries the chosen labels.

## Rule evaluation

```python
async def apply_label_rules(campaign: Campaign, client_id: UUID, db: AsyncSession) -> dict:
    rules = await db.scalars(
        select(CampaignLabelRule)
        .where(CampaignLabelRule.client_id == client_id)
        .where(CampaignLabelRule.active == True)
        .order_by(CampaignLabelRule.priority)
    )
    labels: dict[str, str] = {}
    for rule in rules:
        match = try_apply(rule, campaign)
        if match:
            for dim, value in match.items():
                if dim not in labels:  # First match wins per dimension
                    labels[dim] = value
    return labels
```

## Reallocation pooling implications (§7.10 step 7)

When a dimension has `drives_reallocation_pooling: true`:
- Suggestions don't pair donor and receiver across different values of that dimension.
- Exception: cross-pooling explicitly authorized in `/settings/reallocation-policy`.
- Different `objective_type` pairs are **always suppressed** (no cross-pooling override for objective_type).

```python
def respects_pooling(donor: PlanLine, receiver: PlanLine, taxonomy: ClientTaxonomy) -> bool:
    if donor.objective_type != receiver.objective_type:
        return False  # Hard rule, no override
    for dim, config in taxonomy.dimensions.items():
        if not config.get("drives_reallocation_pooling"):
            continue
        if dim == "objective_type":
            continue  # Already handled
        donor_val = donor.labels.get(dim)
        receiver_val = receiver.labels.get(dim)
        if donor_val != receiver_val and not cross_pooling_authorized(taxonomy, dim):
            return False
    return True
```

## Versioning

Per §7.5, taxonomy is versioned. Changing dimensions creates a new version. Historical actuals keep their previous labels. The pacing UI surfaces labels from the version active **at the time of the actual's date**.

When a template is adopted, `seeded_from_template` is set and the version starts at 1.

## AM-facing surfaces

Per §7.5:
- `/settings/taxonomy` — per-client taxonomy editor. Versioned with audit log.
- `/settings/labeling-rules` — per-client rule editor. Live preview against current actuals.
- Inline label chips on every pacing row, hoverable for label provenance.
- Filter bar above pacing table, current week view, forecast view.
- Unlabeled actuals panel — campaigns running that don't match any rule.

## Template adoption

Adopting a template seeds:
1. `ClientTaxonomy.dimensions` from `taxonomy.json`.
2. `CampaignLabelRule` rows from `label_rules.json`.

Both are subsequently editable per-client without affecting the template.

## What you cannot do

- **No hardcoded taxonomy dimensions.** Read from `ClientTaxonomy` always.
- **No retroactive re-labeling on taxonomy change.** Apply forward only.
- **No skip of pooling constraints in reallocation generation.** §7.10 step 7 is non-negotiable.
- **No filter bar with fixed dimensions.** Drive it from `ClientTaxonomy`.
- **No objective_type as a string literal anywhere outside the taxonomy schema and the drift formula.** Reference it from the schema.

## Workflow when adding taxonomy-related code

1. Identify the dimension(s) involved.
2. Read the `ClientTaxonomy.dimensions` JSONB structure. Don't assume a dimension exists — check.
3. For drift: read `objective_type` and branch the formula. For pooling: check `drives_reallocation_pooling` on each dimension.
4. For UI: render the filter bar from the dimensions list. Use the dimension's `values` for dropdown options if present, or pull distinct labeled values from actuals if open-set.
5. For label rules: evaluate in priority order, first match wins per dimension.
6. Test against multiple taxonomies — single-objective, multi-product-line, custom-dimension. Use fixtures in `tests/fixtures/taxonomies/`.

## Common mistakes

1. Assuming `product_line` always exists. It doesn't — open-set dimensions need to handle absence.
2. Mutating taxonomy as if it weren't versioned. Always create a new version.
3. Letting drift detection run on `insufficient_data` rows. Skip per §7.8 + §7.18.
4. Treating cross-pooling as a per-suggestion override. It's a per-dimension authorization.
5. Implementing labeling rules outside the rule engine. Always go through `apply_label_rules`.
