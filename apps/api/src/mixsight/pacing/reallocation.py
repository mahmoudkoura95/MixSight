"""§7.10 within-market within-channel reallocation algorithm.

Phase 1a Week 3 implementation: single channel (Meta), single market.
Steps from §7.10 map as follows:

  1. Realized efficiency per line — rolling spend / rolling KPI over the
     snapshot week. Lines with `status='insufficient_data'` are skipped.
  2. Donors = overpacing AND underperforming (spend_drift positive +
     kpi_drift negative, both past the §7.10 / drift band).
  3. Receivers = underpacing AND overperforming (spend_drift negative +
     kpi_drift positive).
  4. proposed_amount = min(donor_overpace_in_money, receiver_headroom × 1.3).
  5. Project delta in the receiver's objective units, using receiver's
     realized efficiency.
  6. scope = "within_market_within_channel" — locked for Phase 1a.
  7. Taxonomy pooling: objective_type compat only this week. Different
     objective_type pairs ARE allowed today because spend in money is the
     transferable unit, but cross-objective deltas can't be projected on
     a single shared scale — skip them so the ranking has comparable
     numbers. Cross-product-line + the `drives_reallocation_pooling`
     check land Phase 1b with the real ClientTaxonomy.
  8. Apply scope filter — N/A in Phase 1a single-channel scope.
  9. Confidence score 0.0–1.0 (Decimal(8,4) per §6.2).
 10. Rank top 3 by absolute projected_delta.
 11. Persist ReallocationSuggestion + RecommendationLog at every creation
     per the locked decision + recommendation-log skill (calibration
     substrate from day one of Phase 1a).

Framing is "options with evidence and confidence" — never "we recommend."
Locked decision per CLAUDE.md.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.logging import get_logger
from mixsight.models import (
    Market,
    PacingSnapshot,
    PacingSnapshotLine,
    PlanLine,
    ReallocationSuggestion,
    RecommendationLog,
)

log = get_logger("mixsight.reallocation")

_OVERPACE_THRESHOLD = Decimal("5")  # % above plan
_UNDERPACE_THRESHOLD = Decimal("-5")  # % below plan
_OVERPERFORM_THRESHOLD = Decimal("5")  # KPI % above plan
_UNDERPERFORM_THRESHOLD = Decimal("-5")  # KPI % below plan
_RECEIVER_HEADROOM_FACTOR = Decimal("1.3")  # per §7.10 step 4
_SCOPE_WITHIN_MARKET = "within_market_within_channel"
_TOP_N = 3
_RECOMMENDATION_SOURCE = "heuristic_v1"


@dataclass(frozen=True)
class _LineWithPlan:
    snapshot_line: PacingSnapshotLine
    plan_line: PlanLine

    @property
    def realized_efficiency(self) -> Decimal | None:
        """KPI per money. Higher = better. None when KPI or spend are zero."""
        kpi = self.snapshot_line.actual_kpi_to_date
        spend = self.snapshot_line.actual_spend_to_date
        if not kpi or not spend or spend == 0:
            return None
        return (kpi / spend).quantize(Decimal("0.000001"))


async def _fetch_lines_with_plan(db: AsyncSession, snapshot_id: UUID) -> Sequence[_LineWithPlan]:
    """Pull `(PacingSnapshotLine, PlanLine)` pairs for the snapshot in a
    single query so each candidate-pair check below is in-memory."""
    stmt = (
        select(PacingSnapshotLine, PlanLine)
        .join(PlanLine, col(PlanLine.id) == col(PacingSnapshotLine.plan_line_id))
        .where(col(PacingSnapshotLine.snapshot_id) == snapshot_id)
    )
    rows = (await db.execute(stmt)).all()
    return [_LineWithPlan(snapshot_line=sl, plan_line=pl) for sl, pl in rows]


def _is_donor(line: _LineWithPlan) -> bool:
    sl = line.snapshot_line
    if sl.status == "insufficient_data":
        return False
    return (
        sl.spend_drift_pct is not None
        and sl.kpi_drift_pct is not None
        and sl.spend_drift_pct > _OVERPACE_THRESHOLD
        and sl.kpi_drift_pct < _UNDERPERFORM_THRESHOLD
    )


def _is_receiver(line: _LineWithPlan) -> bool:
    sl = line.snapshot_line
    if sl.status == "insufficient_data":
        return False
    return (
        sl.spend_drift_pct is not None
        and sl.kpi_drift_pct is not None
        and sl.spend_drift_pct < _UNDERPACE_THRESHOLD
        and sl.kpi_drift_pct > _OVERPERFORM_THRESHOLD
    )


def _proposed_amount(donor: _LineWithPlan, receiver: _LineWithPlan) -> Decimal:
    """proposed_amount = min(donor_overpace_money, receiver_headroom_money × 1.3).

    `donor_overpace_money` = how much the donor is over its planned-to-date
    spend. `receiver_headroom_money` = how much the receiver is *under*
    its planned-to-date spend, with the §7.10 step-4 ×1.3 stretch factor.
    """
    donor_overpace = (donor.snapshot_line.actual_spend_to_date or Decimal(0)) - (
        donor.snapshot_line.planned_spend_to_date or Decimal(0)
    )
    receiver_planned = receiver.snapshot_line.planned_spend_to_date or Decimal(0)
    receiver_actual = receiver.snapshot_line.actual_spend_to_date or Decimal(0)
    receiver_headroom = (receiver_planned - receiver_actual) * _RECEIVER_HEADROOM_FACTOR
    return max(Decimal(0), min(donor_overpace, receiver_headroom)).quantize(Decimal("0.0001"))


def _project_delta(
    amount: Decimal, donor: _LineWithPlan, receiver: _LineWithPlan
) -> Decimal | None:
    """Projected KPI change in receiver's objective units when `amount`
    moves donor→receiver. Δ = amount × (receiver_eff − donor_eff)."""
    donor_eff = donor.realized_efficiency
    receiver_eff = receiver.realized_efficiency
    if donor_eff is None or receiver_eff is None:
        return None
    return (amount * (receiver_eff - donor_eff)).quantize(Decimal("0.0001"))


def _score_confidence(donor: _LineWithPlan, receiver: _LineWithPlan) -> Decimal:
    """Phase 1a confidence heuristic, returned in 0.0–1.0.

    A flat base of 0.5, plus a bonus that grows with the combined drift
    magnitude on both lines (a clearer signal earns more confidence), capped
    so a single suggestion can't exceed 0.9. §7.10 step 9 also lists data
    volume and week-over-week stability as inputs; those need multi-week
    history we don't have yet, and the MMM-derived confidence ships Phase 2.
    """
    base = Decimal("0.50")
    if (
        donor.snapshot_line.spend_drift_pct is None
        or receiver.snapshot_line.spend_drift_pct is None
    ):
        return base
    drift_magnitude = (
        abs(donor.snapshot_line.spend_drift_pct) + abs(receiver.snapshot_line.spend_drift_pct)
    ) / Decimal(100)
    bonus = min(Decimal("0.40"), drift_magnitude / Decimal(2))
    return (base + bonus).quantize(Decimal("0.0001"))


def _rationale(
    amount: Decimal,
    donor: _LineWithPlan,
    receiver: _LineWithPlan,
    delta: Decimal | None,
    currency: str,
) -> str:
    """Plain-English summary surfaced in the UI — "options with evidence"
    framing locked in CLAUDE.md (never "we recommend"). `amount` is in the
    market's local currency, so the rationale prefixes it with that ISO code
    rather than a hardcoded symbol."""
    donor_label = donor.plan_line.campaign_label or "donor"
    receiver_label = receiver.plan_line.campaign_label or "receiver"
    delta_str = f"≈ +{delta}" if delta is not None else "uncertain Δ"
    return (
        f"Option: move {currency} {amount} from {donor_label} "
        f"(overpacing + underperforming) to {receiver_label} "
        f"(underpacing + overperforming). Projected impact: "
        f"{delta_str} {receiver.plan_line.objective_type}."
    )


async def compute_suggestions_for_snapshot(
    db: AsyncSession, snapshot: PacingSnapshot
) -> list[ReallocationSuggestion]:
    """End-to-end §7.10 algorithm. Caller commits the session."""
    market = await db.get(Market, snapshot.market_id)
    currency = market.local_currency if market and market.local_currency else "GBP"

    lines = await _fetch_lines_with_plan(db, snapshot.id)
    donors = [line for line in lines if _is_donor(line)]
    receivers = [line for line in lines if _is_receiver(line)]

    candidates: list[tuple[_LineWithPlan, _LineWithPlan, Decimal, Decimal | None, Decimal]] = []
    for donor in donors:
        for receiver in receivers:
            # Step 7 simplified: same objective_type only — projected_delta
            # has no shared scale across different objectives in Phase 1a.
            if donor.plan_line.objective_type != receiver.plan_line.objective_type:
                continue
            amount = _proposed_amount(donor, receiver)
            if amount <= 0:
                continue
            delta = _project_delta(amount, donor, receiver)
            # Skip moves projected to leave the KPI flat or worse: the donor's
            # realized efficiency is >= the receiver's, so shifting budget
            # wouldn't help. A None delta (efficiency uncomputable) is kept —
            # it's directionally valid and ranks last.
            if delta is not None and delta <= 0:
                continue
            confidence = _score_confidence(donor, receiver)
            candidates.append((donor, receiver, amount, delta, confidence))

    candidates.sort(key=lambda c: -(abs(c[3]) if c[3] is not None else Decimal(0)))
    top = candidates[:_TOP_N]

    persisted: list[ReallocationSuggestion] = []
    for donor, receiver, amount, delta, confidence in top:
        suggestion = ReallocationSuggestion(
            organization_id=snapshot.organization_id,
            snapshot_id=snapshot.id,
            donor_line_id=donor.plan_line.id,
            receiver_line_id=receiver.plan_line.id,
            proposed_amount_local=amount,
            proposed_amount_reporting=amount,
            projected_delta=delta,
            projected_delta_units=receiver.plan_line.objective_type,
            confidence=confidence,
            scope=_SCOPE_WITHIN_MARKET,
            rationale_text=_rationale(amount, donor, receiver, delta, currency),
        )
        db.add(suggestion)
        await db.flush()

        # §7.10 step 11 + locked decision + recommendation-log skill:
        # every suggestion writes a RecommendationLog row at creation.
        # Phase 4 calibration UI reads this from day-one Phase 1a history.
        db.add(
            RecommendationLog(
                organization_id=snapshot.organization_id,
                client_id=snapshot.client_id,
                suggestion_id=suggestion.id,
                predicted_delta=delta,
                predicted_confidence=confidence,
                recommendation_source=_RECOMMENDATION_SOURCE,
            )
        )
        persisted.append(suggestion)

    log.info(
        "reallocation.suggestions.persisted",
        snapshot_id=str(snapshot.id),
        donors=len(donors),
        receivers=len(receivers),
        candidates=len(candidates),
        persisted=len(persisted),
    )
    return persisted


async def latest_suggestions_for_snapshot(
    db: AsyncSession, snapshot_id: UUID
) -> list[ReallocationSuggestion]:
    stmt = (
        select(ReallocationSuggestion)
        .where(col(ReallocationSuggestion.snapshot_id) == snapshot_id)
        .order_by(col(ReallocationSuggestion.created_at).desc())
    )
    return list((await db.execute(stmt)).scalars().all())
