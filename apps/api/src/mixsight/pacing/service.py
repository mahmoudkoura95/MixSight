"""PacingSnapshot generation per §7.4 + §7.16.

For a (client_id, market_id, week_ending) tuple, joins the active Plan's
PlanLines against the rolled-up Actuals for the week and emits one
PacingSnapshotLine per PlanLine — capturing spend + KPI drift percentages
and a status badge (green / amber / red / critical / insufficient_data).

Phase 1a Week 3 simplifications:
  - Snapshot is always generated on demand; the weekly scheduled job lands
    in Phase 1c (see §7.16, the "cut-of-last-resort" current-week view).
  - Drift thresholds are hard-coded sensible defaults; §7.21-flagged
    per-client per-objective_type configuration is Phase 1c.
  - `is_partial_week` flips true if `week_ending > today` OR the plan's
    period_start lies inside the snapshot week (mid-week launch).
  - `drift_explanation_text` stays null this week; LLM-generated
    explanations land Week 4 (§7.17 fallback discipline).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.logging import get_logger
from mixsight.models import Actuals, PacingSnapshot, PacingSnapshotLine, Plan, PlanLine

log = get_logger("mixsight.pacing")

# Minimum days of actuals before a campaign's drift status is computed.
# Below this, status = "insufficient_data" and drift columns stay null.
# Matches the §7.18 empty-state contract for new campaigns + the §7.10
# step 1 "skip lines with insufficient data" requirement.
_INSUFFICIENT_DATA_DAY_THRESHOLD = 14

# Drift status bands (absolute percentage). Defaults; §7.21 per-client
# configuration is Phase 1c.
_GREEN_THRESHOLD = Decimal("5")
_AMBER_THRESHOLD = Decimal("10")
_RED_THRESHOLD = Decimal("20")


@dataclass(frozen=True)
class _CampaignActuals:
    spend_local: Decimal
    conversions: Decimal | None
    distinct_days_in_week: int


@dataclass(frozen=True)
class _CampaignHistory:
    """14-day lookback distinct-day count per campaign for the §7.10 step 1
    sufficiency check. Decoupled from in-week rollup because the snapshot
    week is at most 7 days — using in-week distinct days for the
    insufficient_data threshold would gate every line forever."""

    distinct_days_lookback: int


def _week_window(week_ending: date) -> tuple[date, date]:
    """Return the (Monday, Sunday) tuple where Sunday == `week_ending`."""
    week_start = week_ending - timedelta(days=6)
    return week_start, week_ending


def _classify(drift_pct: Decimal | None) -> str:
    """Map a drift percentage to a status badge.

    None → insufficient_data (caller handles before passing None — defensive
    fall-through). Negative or positive both classified by magnitude.
    """
    if drift_pct is None:
        return "insufficient_data"
    abs_drift = abs(drift_pct)
    if abs_drift < _GREEN_THRESHOLD:
        return "green"
    if abs_drift < _AMBER_THRESHOLD:
        return "amber"
    if abs_drift < _RED_THRESHOLD:
        return "red"
    return "critical"


def _compute_drift_pct(actual: Decimal, planned: Decimal) -> Decimal | None:
    """(actual - planned) / planned * 100. None when planned is zero so
    callers can fall through to `no_conversion_baseline` / similar empty
    states from §7.18."""
    if planned == 0:
        return None
    return ((actual - planned) / planned * Decimal(100)).quantize(Decimal("0.0001"))


def _planned_to_date(weekly_plan: Decimal, days_elapsed: int) -> Decimal:
    """Linear prorate; complete week = full planned. The §7.10 v1 algorithm
    explicitly uses linear pacing; non-linear curves land Phase 2 with the
    MMM substrate."""
    if days_elapsed <= 0:
        return Decimal(0)
    if days_elapsed >= 7:
        return weekly_plan
    return (weekly_plan * Decimal(days_elapsed) / Decimal(7)).quantize(Decimal("0.0001"))


async def _find_active_plan(db: AsyncSession, client_id: UUID, week_ending: date) -> Plan | None:
    """Most-recently-ingested active Plan covering the snapshot week. If
    the plan period only partially overlaps the snapshot week, still use
    it — the partial overlap surfaces as `is_partial_week=True` so the
    §7.18 banner can render."""
    week_start, _ = _week_window(week_ending)
    stmt = (
        select(Plan)
        .where(
            col(Plan.client_id) == client_id,
            col(Plan.status) == "active",
            col(Plan.deleted_at).is_(None),
            col(Plan.period_start) <= week_ending,
            col(Plan.period_end) >= week_start,
        )
        .order_by(col(Plan.ingested_at).desc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _fetch_plan_lines(db: AsyncSession, plan_id: UUID, market_id: UUID) -> Sequence[PlanLine]:
    stmt = select(PlanLine).where(
        col(PlanLine.plan_id) == plan_id,
        col(PlanLine.market_id) == market_id,
        col(PlanLine.deleted_at).is_(None),
    )
    return list((await db.execute(stmt)).scalars().all())


async def _rollup_actuals(
    db: AsyncSession, client_id: UUID, market_id: UUID, week_ending: date
) -> dict[str, _CampaignActuals]:
    """Return `{campaign_label: in-week rolled-up actuals}` for drift calc.

    Grouped by `campaign_label` because PlanLines key on label, not on
    `campaign_external_id` (those come from connector pulls and may not
    match what the AM entered into the plan template). Phase 1b's
    CampaignLabelRule wires the two together — for Week 3 the seed +
    parser-derived labels match exactly so this group-by works.
    """
    week_start, _ = _week_window(week_ending)
    stmt = (
        select(
            col(Actuals.campaign_label),
            func.sum(col(Actuals.spend_local)).label("spend"),
            func.sum(col(Actuals.conversions)).label("conversions"),
            func.count(func.distinct(col(Actuals.date))).label("days"),
        )
        .where(
            col(Actuals.client_id) == client_id,
            col(Actuals.market_id) == market_id,
            col(Actuals.date) >= week_start,
            col(Actuals.date) <= week_ending,
        )
        .group_by(col(Actuals.campaign_label))
    )
    rows = (await db.execute(stmt)).all()
    return {
        row.campaign_label: _CampaignActuals(
            spend_local=row.spend or Decimal(0),
            conversions=row.conversions,
            distinct_days_in_week=row.days or 0,
        )
        for row in rows
    }


async def _history_days(
    db: AsyncSession, client_id: UUID, market_id: UUID, week_ending: date
) -> dict[str, _CampaignHistory]:
    """Distinct-day count over the §7.10 step 1 14-day lookback ending at
    `week_ending`. Used solely for the insufficient_data threshold —
    separate from the in-week rollup so the snapshot week's natural
    7-day ceiling doesn't permanently gate every campaign."""
    lookback_start = week_ending - timedelta(days=_INSUFFICIENT_DATA_DAY_THRESHOLD - 1)
    stmt = (
        select(
            col(Actuals.campaign_label),
            func.count(func.distinct(col(Actuals.date))).label("days"),
        )
        .where(
            col(Actuals.client_id) == client_id,
            col(Actuals.market_id) == market_id,
            col(Actuals.date) >= lookback_start,
            col(Actuals.date) <= week_ending,
        )
        .group_by(col(Actuals.campaign_label))
    )
    rows = (await db.execute(stmt)).all()
    return {
        row.campaign_label: _CampaignHistory(distinct_days_lookback=row.days or 0) for row in rows
    }


async def generate_snapshot(
    db: AsyncSession,
    *,
    organization_id: UUID,
    client_id: UUID,
    market_id: UUID,
    week_ending: date,
    allocation_mode: str = "mode_a",
) -> PacingSnapshot | None:
    """Compute + persist a fresh PacingSnapshot for the given week.

    Returns None if no active Plan covers the week — caller is responsible
    for showing the §7.18 "no_active_plan" empty state. The caller commits
    the session; this function only stages writes.
    """
    plan = await _find_active_plan(db, client_id, week_ending)
    if plan is None:
        log.info("pacing.no_active_plan", client_id=str(client_id), week_ending=str(week_ending))
        return None

    week_start, _ = _week_window(week_ending)
    today = datetime.now(UTC).date()
    days_elapsed = min(7, max(0, (min(today, week_ending) - week_start).days + 1))
    is_partial_week = (
        week_ending > today  # snapshot was requested for an in-flight week
        or plan.period_start > week_start  # plan launched mid-week
    )

    plan_lines = await _fetch_plan_lines(db, plan.id, market_id)
    actuals_by_label = await _rollup_actuals(db, client_id, market_id, week_ending)
    history_by_label = await _history_days(db, client_id, market_id, week_ending)

    snapshot = PacingSnapshot(
        organization_id=organization_id,
        client_id=client_id,
        market_id=market_id,
        week_ending=week_ending,
        allocation_mode=allocation_mode,
        is_partial_week=is_partial_week,
    )
    db.add(snapshot)
    await db.flush()

    for plan_line in plan_lines:
        actuals = actuals_by_label.get(
            plan_line.campaign_label or "",
            _CampaignActuals(spend_local=Decimal(0), conversions=None, distinct_days_in_week=0),
        )
        history_days = history_by_label.get(
            plan_line.campaign_label or "", _CampaignHistory(distinct_days_lookback=0)
        ).distinct_days_lookback
        planned_spend_to_date = _planned_to_date(plan_line.planned_spend_local, days_elapsed)
        planned_kpi_to_date = (
            _planned_to_date(plan_line.kpi_target, days_elapsed) if plan_line.kpi_target else None
        )

        if history_days < _INSUFFICIENT_DATA_DAY_THRESHOLD:
            spend_drift_pct = None
            kpi_drift_pct = None
            status = "insufficient_data"
        else:
            spend_drift_pct = _compute_drift_pct(actuals.spend_local, planned_spend_to_date)
            kpi_drift_pct = (
                _compute_drift_pct(actuals.conversions or Decimal(0), planned_kpi_to_date)
                if planned_kpi_to_date is not None
                else None
            )
            # Status takes the worst of the two signals so an AM looking at
            # a green spend / red KPI row doesn't get a falsely-reassuring
            # green badge.
            spend_status = _classify(spend_drift_pct)
            kpi_status = _classify(kpi_drift_pct) if kpi_drift_pct is not None else "green"
            status = max(
                spend_status,
                kpi_status,
                key=lambda s: ("green", "amber", "red", "critical", "insufficient_data").index(s),
            )

        db.add(
            PacingSnapshotLine(
                organization_id=organization_id,
                snapshot_id=snapshot.id,
                plan_line_id=plan_line.id,
                actual_spend_to_date=actuals.spend_local,
                planned_spend_to_date=planned_spend_to_date,
                spend_drift_pct=spend_drift_pct,
                actual_kpi_to_date=actuals.conversions,
                planned_kpi_to_date=planned_kpi_to_date,
                kpi_drift_pct=kpi_drift_pct,
                status=status,
                objective_type=plan_line.objective_type,
                labels=plan_line.labels,
            )
        )

    return snapshot


async def latest_snapshot_for_week(
    db: AsyncSession, *, client_id: UUID, market_id: UUID, week_ending: date
) -> PacingSnapshot | None:
    """Most-recent snapshot for the (client, market, week) tuple, or None."""
    stmt = (
        select(PacingSnapshot)
        .where(
            col(PacingSnapshot.client_id) == client_id,
            col(PacingSnapshot.market_id) == market_id,
            col(PacingSnapshot.week_ending) == week_ending,
        )
        .order_by(col(PacingSnapshot.generated_at).desc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


def default_week_ending(today: date) -> date:
    """Last completed Sunday relative to `today`. If today IS Sunday, today."""
    # Python weekday: Mon=0 .. Sun=6
    days_since_sunday = (today.weekday() + 1) % 7
    return today - timedelta(days=days_since_sunday)
