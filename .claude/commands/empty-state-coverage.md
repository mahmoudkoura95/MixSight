---
description: Walk the §7.18 empty-state checklist against a surface. Use whenever a new pacing view, chart, or list is added. Empty states are first-experience, not edge cases.
argument-hint: <surface-name> (e.g., "pacing-table", "reallocation-suggestions", "current-week-view")
---

Walk the empty-state coverage checklist for surface: `$ARGUMENTS`.

Read SCOPE.md §7.18 in full. The framing matters: empty states are the **first** experience an AM has after onboarding. A product that says "come back next Monday" loses the user in 30 seconds.

Check this surface against every state below. For each, document what the surface renders.

## First-week empty states

1. **Backfill in progress** (Day 0 to ~Day 1)
   - Banner: "Historical data loading — full pacing view available in approximately 6-12 hours. Going-forward data updating every morning."
   - Pacing table populated with whatever exists (trailing 7-day daily pull window typically complete).
   - Status indicators muted.
   - Backfill progress visible in connector health surface.

2. **Backfill complete, partial week of going-forward data** (~Day 1 through end of first calendar week)
   - Pacing table populated.
   - Reallocation suggestions: available algorithmically once 14+ days of historical or backfilled data exists per campaign (backfill counts).
   - Reconciliation factors: "Preliminary — sample size limited" annotation until 4+ weeks of variance accumulated.

3. **First Monday snapshot for new client**
   - `PacingSnapshot.is_partial_week = true` if onboarded after Tuesday in the snapshot week.
   - Banner: "First snapshot — based on partial week and historical backfill. Full Monday-morning experience available [date]."
   - Reallocation suggestions visible if data sufficient; muted if not with explainer.
   - Drift explanations: not generated for `insufficient_data` rows. Empty state is "no significant drift detected — building baseline," not blank.
   - Defense kit: generatable with header, pacing table, methodology footnote, templated narrative. No drift callouts, no reallocation block.

## Permanent partial-data states

4. **Campaign launched mid-week with <7 days of data**
   - Pacing row visible.
   - Status badge `insufficient_data`.
   - Excluded from reallocation candidates.
   - No drift explanation.
   - Tooltip: "Building baseline — 7+ days needed for drift detection."

5. **Channel with zero historical conversions**
   - Drift formula handles divide-by-zero.
   - Status defaults to amber with reason `no_conversion_baseline`.
   - Drift explanation skipped.

6. **Market with ad accounts authed but zero spend**
   - Market visible in selector.
   - Pacing table empty for that market.
   - Explainer: "No spend yet in [market]. Pacing view available once first spend recorded."

7. **Plan period not yet started**
   - Pacing table shows planned values; actuals empty.
   - Status `pre_flight`.
   - Drift detection skipped.
   - AM can still review plan and configure taxonomy.

8. **Plan period ended**
   - Snapshot frozen at last-week-of-flight values.
   - Banner: "Plan period ended [date]. Final pacing recorded."
   - Subsequent weeks show "no active plan" until new plan ingested.

9. **Empty taxonomy filter result**
   - "No campaigns match the current filter."
   - Link to clear filter.
   - Link to extend taxonomy.

## Production

For each state, identify in the surface:
- The visual treatment (component, copy, affordances).
- The data condition that triggers it.
- The component that renders it (use `<EmptyState variant="...">` from `packages/shared/` — don't reinvent).

## Output

| State | Trigger condition | Treatment | Tested? |
|---|---|---|---|

For any row not covered, build it before merging. The §7.18 list is exhaustive for Phase 1 surfaces; new states in later phases get appended.

Reminder: empty states are not edge cases. They are the first experience.
