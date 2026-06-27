---
name: recommendation-log
description: Use this skill whenever creating, modifying, or analyzing a ReallocationSuggestion in the MixSight project. Triggers include "reallocation suggestion," "RecommendationLog," "calibration," "track record," "ranked suggestion," "donor-receiver." Encodes the SCOPE.md §7.10 step 11 rule: every ReallocationSuggestion writes a RecommendationLog row at creation, regardless of phase. The calibration UI that ships in Phase 4 depends on this logging starting day one of Phase 1a. Phase 4 customers will see "tool that has data on its own track record" — but only if logging has been running since onboarding. Use this skill BEFORE any reallocation-related code.
---

# Recommendation log skill

Per §7.10 step 11 and §3 (locked decisions): every `ReallocationSuggestion` writes a `RecommendationLog` row at creation, **from day one of Phase 1a**. The Phase 4 calibration UI exists because this logging has been running since onboarding. Track record needs time. Logging is cheap. Don't skip it.

## The pattern

When a `ReallocationSuggestion` is created (during the Monday batch job or on-demand recalculation):

```python
from app.models import ReallocationSuggestion, RecommendationLog


async def persist_suggestion_with_log(
    suggestion: ReallocationSuggestion,
    db: AsyncSession,
) -> None:
    db.add(suggestion)
    await db.flush()  # Get suggestion.id

    log_entry = RecommendationLog(
        client_id=suggestion.client_id,
        suggestion_id=suggestion.id,
        recommended_at=suggestion.created_at,
        predicted_delta=suggestion.projected_delta,
        predicted_confidence=suggestion.confidence,
        recommendation_source="heuristic_v1",  # Phase 1; "model_v2" in Phase 2d+
        implemented=False,
        implemented_at=None,
        implemented_amount=None,
        observed_outcome=None,
        outcome_window_end=None,
        calibration_score=None,
    )
    db.add(log_entry)
    await db.commit()
```

`recommendation_source` is the algorithm version:
- `heuristic_v1` — Phase 1 algorithm (§7.10 steps 1-11).
- `model_v2` — Phase 2d+ algorithm with curve-based projection from modeling engine.
- `forecast_v3` — Phase 3 (if reallocation gets forecast input).

## What gets logged at creation

Per §7.4 RecommendationLog fields:

| Field | Source | When set |
|---|---|---|
| `client_id` | suggestion.client_id | At creation |
| `suggestion_id` | suggestion.id | At creation |
| `recommended_at` | now() | At creation |
| `predicted_delta` | suggestion.projected_delta | At creation |
| `predicted_confidence` | suggestion.confidence | At creation |
| `recommendation_source` | algorithm version | At creation |
| `implemented` | false | Updated later if AM implements |
| `implemented_at` | null | Updated on implementation |
| `implemented_amount` | null | Updated on implementation |
| `observed_outcome` | null | Computed in batch from actuals |
| `outcome_window_end` | null | Set when observation window closes |
| `calibration_score` | null | Computed in batch from prediction vs outcome |

## Implementation tracking

When an AM marks a suggestion as implemented (via `am_justification_text` + included in defense kit), update the log:

```python
async def mark_implemented(suggestion_id: UUID, actual_amount: Decimal, db):
    log_entry = await db.scalar(
        select(RecommendationLog).where(RecommendationLog.suggestion_id == suggestion_id)
    )
    log_entry.implemented = True
    log_entry.implemented_at = datetime.now(timezone.utc)
    log_entry.implemented_amount = actual_amount
    await db.commit()
```

## Outcome observation

In a batch job, after the observation window closes (typically 2-4 weeks post-implementation):

```python
async def observe_outcomes_batch():
    open_logs = await db.scalars(
        select(RecommendationLog)
        .where(RecommendationLog.implemented == True)
        .where(RecommendationLog.outcome_window_end <= now())
        .where(RecommendationLog.observed_outcome.is_(None))
    )
    for log in open_logs:
        outcome = await compute_outcome_from_actuals(log)
        log.observed_outcome = outcome
        log.calibration_score = score(log.predicted_delta, outcome)
    await db.commit()
```

The `calibration_score` is a normalized measure of prediction accuracy. Phase 4 surfaces it per channel per customer.

## Phase 4 calibration UI

Per §10.2:
- Per-channel, per-customer track record with recommendation-source attribution.
- Calibration loop: future recommendations widen confidence ranges or downweight historically-wrong channels.
- Per-customer accuracy export.

None of this works without 2+ years of recommendation logs. **Log from day one or Phase 4 is dead on arrival.**

## What you cannot do

- **No `ReallocationSuggestion` creation path that skips `RecommendationLog`.** Every path goes through `persist_suggestion_with_log` or equivalent.
- **No deletion or update of `RecommendationLog` rows.** It's append-only (except for the implementation/outcome columns which transition from NULL to set once).
- **No retroactive backfilling.** If you discover a code path was skipping the log, the lost history is lost. Don't try to reconstruct from `ReallocationSuggestion` rows — calibration math depends on knowing the prediction at the time it was made, not what it would look like if computed now.
- **No `RecommendationLog` outside the application layer.** Migrations don't touch its rows; only the application creates them.

## Workflow when adding a reallocation path

1. Read §7.10 in full. Make sure the algorithm respects taxonomy pooling constraints (step 7).
2. Use `persist_suggestion_with_log` for any new path that creates suggestions.
3. Tag with the correct `recommendation_source`.
4. Test that the log row is written, even when no AM is involved (batch job creates suggestions; log gets written).
5. If introducing a new algorithm version, document in `DECISIONS.md`. New `recommendation_source` values get an ADR.

## Cross-references

- `RecommendationLog` table definition: §7.4
- Reallocation algorithm: §7.10
- Calibration UI: §10.2
- The "logging from day one" lock: §3 (Recommendation tracking decision)
- Phase 4 success criterion: §10.4 (calibration UI in active use for ≥10 clients)
