---
name: empty-state
description: Use this skill whenever building a new pacing surface, chart, list view, or any UI component that may render with no or partial data in the MixSight project. Triggers include "new view," "new surface," "empty state," "no data," "first week," "backfill in progress," "insufficient data," "partial week," "pre-flight," "post-flight," "no spend," "zero conversions." Encodes the SCOPE.md §7.18 empty-state catalog. Empty states are NOT edge cases — they are the FIRST experience an AM has after onboarding. A product that says "come back next Monday" loses the user in 30 seconds. Use this skill BEFORE shipping any new surface.
---

# Empty state skill

The first time an AM logs into MixSight is also the first time they're deciding whether to keep their team using it. A product that says "come back next Monday" loses the AM in 30 seconds. A product that says "here's what I can show you now, here's what's coming, here's what to do in the meantime" earns another visit. Empty states are not edge cases; they are the first experience.

## The empty-state catalog

Every new surface walks this list. Each state has a specific treatment.

### First-week empty states

| State | When | Treatment |
|---|---|---|
| **Backfill in progress** | Day 0 to ~Day 1; connectors just authed | Banner: "Historical data loading — full pacing view available in ~6-12 hours. Going-forward data updating every morning." Pacing table populated with whatever exists from the trailing 7-day daily pull window. Status indicators muted. Backfill progress visible in connector health surface. |
| **Backfill complete, partial week** | ~Day 1 through end of first calendar week | Pacing table populated. Reallocation suggestions available algorithmically once 14+ days exist per campaign (backfill counts). Reconciliation factors annotated "Preliminary — sample size limited" until 4+ weeks of variance accumulated. |
| **First Monday snapshot for new client** | First weekly snapshot, `is_partial_week = true` if onboarded after Tuesday | Banner: "First snapshot — based on partial week and historical backfill. Full Monday-morning experience available [date of first complete Sunday-to-Sunday week]." Reallocation suggestions muted if data insufficient with explainer. Drift explanations: not generated for `insufficient_data` rows; "no significant drift detected — building baseline" rather than blank. Defense kit generatable with templated narrative ("Initial week of MixSight tracking; baseline established. Detailed insights available from Week 2.") No drift callouts, no reallocation block. |

### Permanent partial-data states

These persist indefinitely and need explicit handling:

| State | When | Treatment |
|---|---|---|
| **Campaign launched mid-week, <7 days data** | New campaign appears | Pacing row visible. Status badge `insufficient_data`. Excluded from reallocation candidates. No drift explanation. Tooltip: "Building baseline — 7+ days needed for drift detection." |
| **Channel with zero historical conversions** | Channel without conversion baseline | Drift formula handles divide-by-zero. Status defaults to amber, reason `no_conversion_baseline`. Drift explanation skipped. |
| **Market with ad accounts authed but zero spend** | Market exists but no spend yet | Market visible in selector. Pacing table empty for that market. Explainer: "No spend yet in [market]. Pacing view available once first spend recorded." |
| **Plan period not yet started** | Plan exists but flight start in future | Pacing table shows planned values; actuals empty. Status `pre_flight`. Drift detection skipped. AM can still review plan and configure taxonomy. |
| **Plan period ended** | Past flight end date | Snapshot frozen at last-week-of-flight values. Banner: "Plan period ended [date]. Final pacing recorded." Subsequent weeks show "no active plan" until new plan ingested. |
| **Empty taxonomy filter result** | User filters to a dimension value with no rows | "No campaigns match the current filter." Link to clear filter. Link to extend taxonomy. |

## The shared component

Use the `<EmptyState>` component from `packages/shared/`:

```tsx
<EmptyState
  variant="backfill_in_progress"
  context={{ etaHours: 8, lastPullAt: "06:14 GMT" }}
  primaryAction={{ label: "View connector health", href: "/health" }}
/>
```

Variants:
- `backfill_in_progress`
- `partial_week`
- `first_monday_partial`
- `insufficient_data`
- `no_conversion_baseline`
- `no_spend_in_market`
- `pre_flight`
- `post_flight`
- `no_filter_match`

Each variant is a single source of truth for copy, icon, color, primary action. Do not reinvent.

## The empty-state status badge

A pacing row's `status` field has these values:

| Status | Color | Drift formula? | Reallocation candidate? |
|---|---|---|---|
| `green` | green | yes | yes |
| `amber` | amber | yes | yes |
| `red` | red | yes | yes |
| `critical` | bright red | yes | yes |
| `insufficient_data` | gray | no | no |
| `pre_flight` | gray | no | no |
| `post_flight` | gray | no | no |
| `no_conversion_baseline` | amber | partial (spend only) | no |

## What "useful from minute one" means

The product needs to feel useful from minute one of onboarding, not "come back next Monday." Concretely, on Day 0 the AM should see:

1. **Their first pacing table** (sparse, but populated with what daily-pull window already covered).
2. **Connector health surface** showing what's loading.
3. **Taxonomy already seeded** from the template they picked.
4. **A defense kit** that's generatable with templated narrative.
5. **Setting surfaces** all functional — they can configure white-label, drift thresholds, attribution settings while data loads.

What they should NOT see:

- A blank pacing screen.
- A "no data" error.
- A "please come back later" wall.
- Disabled buttons with no explanation.

## Workflow when building a new surface

1. List every possible data state for this surface.
2. For each state, identify the matching entry in the catalog above. If none matches, propose a new entry — get it added to the catalog and to `<EmptyState>` variants before shipping.
3. Build the surface to render the appropriate `<EmptyState>` for each state.
4. Test each state with a fixture. Use `tests/empty_states/` patterns.
5. Visually review — does the empty state feel like a beginning, not a dead end?
6. Run `/empty-state-coverage <surface>` to walk the catalog systematically.

## Common mistakes

1. Rendering a blank component when data is empty. Always render the appropriate `<EmptyState>`.
2. Treating empty states as "edge cases" — they are the **first** experience.
3. Inventing new copy per surface — use the shared variants for consistency.
4. Forgetting to skip drift detection for `insufficient_data` rows — they'll generate noisy false amber/red.
5. Forgetting that backfill counts toward the "14+ days of data" threshold for reallocation suggestions.
6. Hiding the surface entirely if data is sparse. Show it with appropriate empty-state treatment so the AM knows what's coming.
