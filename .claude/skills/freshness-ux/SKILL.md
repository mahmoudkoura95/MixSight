---
name: freshness-ux
description: Use this skill whenever building or modifying any surface that shows pacing, current week data, or daily-refreshed actuals in the MixSight project. Triggers include "current week," "weekly snapshot," "freshness," "still settling," "daily refresh," "trailing 3 days," "reconciliation," "intraday." Encodes the SCOPE.md §7.16 freshness UX: weekly snapshot is the source of truth; current week view is a directional supplement with explicit "still settling" treatment on the trailing 3 days. Visual treatment communicates the difference clearly so AMs don't mistake intraday wobble for real drift. Use this skill BEFORE building any view that surfaces current-week data.
---

# Freshness UX skill

Daily refresh (Phase 1c) means data updates every morning, not weekly. But platforms restate the last 1-3 days of data — attribution windows close late, conversions get retroactively counted. The visual treatment must communicate "directional, settling" so AMs don't mistake intraday wobble for real drift and pull triggers they shouldn't.

## The two views

Per §7.16:

| Surface | Source of truth? | LLM narrative? | Visual treatment |
|---|---|---|---|
| Weekly snapshot | **Yes** | Yes (drift explanations, defense kit narrative) | Full saturation |
| Current week view | Directional supplement | No (or off by default) | Trailing 3 days "still settling" |

The weekly snapshot is the Monday morning artifact. It's what the defense kit is built from. It's where drift detection and reallocation suggestions live. The current week view is for "is something on fire right now?" — explicitly framed as preliminary.

## Visual treatment for trailing 3 days

On the current week view, the **trailing 3 days** (today, yesterday, day-before-yesterday) get:

1. **Lighter saturation.** Bars/lines in muted tones — typically 50-60% opacity or a desaturated variant of the channel color.
2. **Dotted top edge** on bars / line points marked with a "settling" annotation glyph.
3. **Tooltip on hover.** "Data still settling. Platform reconciliations typically complete within 72 hours."
4. **No drift status badges.** Drift detection on partial-day data is noise. Status shows "—" rather than green/amber/red for these days.

The component to use:

```tsx
import { SettlingTreatment } from "@mixsight/shared/charts";

<BarChart>
  <Bar dataKey="spend" fill={channelColor}>
    {data.map((d, i) => (
      <Cell
        key={i}
        fill={channelColor}
        fillOpacity={isSettling(d.date) ? 0.6 : 1.0}
        stroke={isSettling(d.date) ? channelColor : undefined}
        strokeDasharray={isSettling(d.date) ? "3 3" : undefined}
      />
    ))}
  </Bar>
</BarChart>
```

`isSettling(date)` returns true if `today - date <= 3 days`.

## Per-org / per-client toggle

Per §7.16:
- Per-organization setting: current week view default-on. Settings → Data freshness.
- Per-client override: AMs working with skittish stakeholders can disable for specific clients. Stakeholder sees only weekly snapshot.

```python
async def is_current_week_view_enabled(client_id: UUID) -> bool:
    client = await load_client(client_id)
    if client.current_week_view_enabled is not None:
        return client.current_week_view_enabled  # per-client override
    return client.organization.current_week_view_default
```

When disabled at client level: the current week tab is hidden in the nav for that client. Weekly snapshot remains.

## Freshness stamp

Every pacing surface shows a freshness stamp at the top:

```
Data current as of 6:14 AM GMT, Monday 18 Mar. Daily refresh re-fetched last 7 days.
```

The format includes:
- Latest pull timestamp (`Actuals.pull_timestamp` max, formatted in market local timezone).
- Refresh window (`Client.daily_refresh_window_days`).
- "Daily refresh" indicator (vs. weekly).

## Reconciliation diff in audit log

When the daily pull revises a previously-stored value by more than the threshold (default 5%), the audit log captures the diff. Surfaced in:
- Connector health audit log per platform.
- Optional per-row callout if the revision is significant.

This isn't user-facing on the pacing screen by default (would create noise) — it's available in admin-facing health surface.

## LLM cost discipline (§7.16)

Daily refresh creates a temptation: regenerate drift explanations every day. **Don't.** LLM cost compounds and the daily wobble triggers false signal.

LLM narrative is cached at the weekly-snapshot level. Daily updates do not retrigger generation. The current week view shows visual data only, no LLM-generated explanations.

If we ever turn on per-day drift explanation (Phase 3+):
- Quota counted aggressively.
- Behind a paid feature flag (Pro tier and above).
- Default-off per workspace.
- Cached by `(snapshot_line_id, day_of_week)`.

## Pacing table for current week

Current week pacing table columns and behavior:

| Column | Behavior |
|---|---|
| Campaign | Same as weekly. |
| Channel / Market | Same. |
| Spend (week-to-date) | Aggregated from start-of-week through latest complete day. |
| Pace vs plan | Computed from week-to-date / expected-week-to-date. Settling treatment on the "expected" if today's projected value falls in the 3-day window. |
| Status | `—` for rows where insufficient settled data; otherwise computed. |
| Last updated | Per-row freshness stamp (most recent pull for that campaign). |

Sort and filter behavior identical to weekly snapshot.

## The "settling" rule formally

A data point is "settling" if:
- Its `date` is today, OR
- Its `date` is within 3 days prior to today.

Where "today" is in the **market's local timezone**, not the user's or server's.

```python
def is_settling(point_date: date, market_timezone: str) -> bool:
    market_today = datetime.now(ZoneInfo(market_timezone)).date()
    return (market_today - point_date).days <= 3 and (market_today - point_date).days >= 0
```

For multi-market rolled views, the conservative rule applies: settling if **any** of the involved markets considers it settling.

## What you cannot do

- **No conflating weekly snapshot data with current-week data in the same chart.** They're separate routes.
- **No drift detection on current-week trailing-3-day data.** Detection runs only on settled data.
- **No LLM-generated narrative on current week view by default.** Cost discipline.
- **No silent reconciliations.** Revisions >5% write to AuditLog with row-level visibility.
- **No removing the freshness stamp** "to clean up the design." It is part of the design.

## Workflow when adding a current-week surface

1. Read §7.16 in full.
2. Confirm the route is separate from weekly snapshot (different URL).
3. Use `<SettlingTreatment>` shared component for the trailing-3-day visual.
4. Use `<FreshnessStamp>` component at the top of the surface.
5. Verify settling-rule logic uses market local time.
6. Run drift detection only on settled data.
7. Test with a market in a far timezone (Tokyo) to verify the local-time logic.

## Cross-references

- Daily refresh job: §7.14
- Reconciliation factors: §7.4 `ReconciliationFactor` table
- LLM cost discipline: §7.17
- Current-week-view as cut-of-last-resort: §7.21 (if Phase 1c slips past week 6, current-week view is the documented cut)
