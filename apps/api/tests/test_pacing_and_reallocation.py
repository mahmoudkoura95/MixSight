"""Integration tests for §7.10 + §7.16 pacing + reallocation services.

Three contracts under test:

1. **PacingSnapshot generation correctness.** Drift formula, status banding,
   insufficient_data threshold (14 days).
2. **§7.10 step 11 RecommendationLog write.** Every ReallocationSuggestion
   created must produce a RecommendationLog row, source `heuristic_v1`,
   tenant-scoped. The recommendation-log skill names this the load-bearing
   day-one Phase 1a contract that Phase 4 calibration depends on.
3. **Empty-state handling.** No active plan → `None` snapshot (caller
   surfaces §7.18 `no_active_plan`); insufficient_data per row when <14d
   of actuals.

Endpoint + tenancy isolation is in `test_pacing_endpoint.py`.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.models import (
    Actuals,
    Client,
    Market,
    Organization,
    PacingSnapshotLine,
    Plan,
    PlanLine,
    RecommendationLog,
)
from mixsight.pacing.reallocation import compute_suggestions_for_snapshot
from mixsight.pacing.service import default_week_ending, generate_snapshot


async def _build_scenario(
    db: AsyncSession,
    *,
    suffix: str,
    week_ending: date,
    line_overrides: list[tuple[str, str, Decimal, Decimal, float, float]] | None = None,
    actuals_days: int = 14,
) -> tuple[Organization, Client, Market, Plan]:
    """Build NB-EMEA-shaped scenario. line_overrides shape:
    [(campaign_label, objective_type, weekly_plan_spend, weekly_plan_kpi,
      actuals_spend_modifier, actuals_kpi_modifier)]"""
    org = Organization(name=f"Org {suffix}", clerk_organization_id=f"clerk_org_{suffix}")
    db.add(org)
    await db.commit()
    await db.refresh(org)
    client = Client(organization_id=org.id, name=f"Client {suffix}", reporting_currency="GBP")
    db.add(client)
    await db.commit()
    await db.refresh(client)
    market = Market(
        organization_id=org.id,
        client_id=client.id,
        code="UK",
        local_currency="GBP",
    )
    db.add(market)
    await db.commit()
    await db.refresh(market)

    period_start = week_ending - timedelta(days=6)
    plan = Plan(
        organization_id=org.id,
        client_id=client.id,
        version=1,
        source_method="template",
        status="active",
        period_start=period_start,
        period_end=week_ending,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    overrides = line_overrides or [
        # donor: overpaces (+25%), underperforms (-30%)
        ("Brand Search", "conversions", Decimal("1400.00"), Decimal("280"), 1.25, 0.70),
        # receiver: underpaces (-35%), overperforms (+45%)
        ("Prospecting", "conversions", Decimal("2100.00"), Decimal("180"), 0.65, 1.45),
        # on-pace control
        ("Retargeting", "conversions", Decimal("980.00"), Decimal("220"), 1.02, 0.98),
    ]
    pull_window_start = period_start - timedelta(days=7)
    pull_window_end = week_ending
    for label, objective_type, weekly_spend, weekly_kpi, sm, km in overrides:
        plan_line = PlanLine(
            organization_id=org.id,
            plan_id=plan.id,
            market_id=market.id,
            channel="meta",
            campaign_label=label,
            period_start=period_start,
            period_end=week_ending,
            planned_spend_local=weekly_spend,
            objective_type=objective_type,
            kpi_target=weekly_kpi,
        )
        db.add(plan_line)
        daily_spend = (weekly_spend * Decimal(str(sm))) / Decimal(7)
        daily_kpi = (weekly_kpi * Decimal(str(km))) / Decimal(7)
        for d_offset in range(actuals_days):
            d = pull_window_start + timedelta(days=d_offset)
            db.add(
                Actuals(
                    organization_id=org.id,
                    client_id=client.id,
                    market_id=market.id,
                    channel="meta",
                    campaign_external_id=f"camp_{label.lower().replace(' ', '_')}",
                    campaign_label=label,
                    date=d,
                    spend_local=daily_spend.quantize(Decimal("0.0001")),
                    spend_reporting=daily_spend.quantize(Decimal("0.0001")),
                    conversions=daily_kpi.quantize(Decimal("0.0001")),
                    source="csv_upload",
                    pull_timestamp=datetime.now(UTC),
                    pull_window_start=pull_window_start,
                    pull_window_end=pull_window_end,
                )
            )
    await db.commit()
    return org, client, market, plan


@pytest.mark.asyncio
async def test_snapshot_generates_lines_with_correct_drift_and_status(
    db_session: AsyncSession,
) -> None:
    week_ending = default_week_ending(date.today())
    org, client, market, _plan = await _build_scenario(
        db_session, suffix="snap1", week_ending=week_ending
    )

    snapshot = await generate_snapshot(
        db_session,
        organization_id=org.id,
        client_id=client.id,
        market_id=market.id,
        week_ending=week_ending,
    )
    await db_session.commit()
    assert snapshot is not None
    assert snapshot.allocation_mode == "mode_a"
    assert snapshot.organization_id == org.id

    lines = list(
        (
            await db_session.execute(
                select(PacingSnapshotLine).where(col(PacingSnapshotLine.snapshot_id) == snapshot.id)
            )
        )
        .scalars()
        .all()
    )
    assert len(lines) == 3
    by_status = {ln.status for ln in lines}
    # Donor's 25% overpace + 30% underperform → at least one critical row.
    # Receiver's 35% underpace + 45% overperform → at least one critical row.
    # On-pace control → green or amber depending on jitter.
    assert "critical" in by_status, by_status


@pytest.mark.asyncio
async def test_insufficient_data_when_under_14_days(db_session: AsyncSession) -> None:
    week_ending = default_week_ending(date.today())
    org, client, market, _plan = await _build_scenario(
        db_session, suffix="snap2", week_ending=week_ending, actuals_days=5
    )
    snapshot = await generate_snapshot(
        db_session,
        organization_id=org.id,
        client_id=client.id,
        market_id=market.id,
        week_ending=week_ending,
    )
    await db_session.commit()
    assert snapshot is not None
    lines = list(
        (
            await db_session.execute(
                select(PacingSnapshotLine).where(col(PacingSnapshotLine.snapshot_id) == snapshot.id)
            )
        )
        .scalars()
        .all()
    )
    assert all(ln.status == "insufficient_data" for ln in lines), [ln.status for ln in lines]
    assert all(ln.spend_drift_pct is None for ln in lines)


@pytest.mark.asyncio
async def test_no_active_plan_returns_none(db_session: AsyncSession) -> None:
    """§7.18 `no_active_plan` empty state — generator returns None when no
    Plan covers the snapshot week. Caller (route) renders the banner."""
    org = Organization(name="Empty org", clerk_organization_id="clerk_org_emptyplan")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    client = Client(organization_id=org.id, name="No Plan Client")
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    market = Market(organization_id=org.id, client_id=client.id, code="UK", local_currency="GBP")
    db_session.add(market)
    await db_session.commit()
    await db_session.refresh(market)

    snapshot = await generate_snapshot(
        db_session,
        organization_id=org.id,
        client_id=client.id,
        market_id=market.id,
        week_ending=default_week_ending(date.today()),
    )
    assert snapshot is None


@pytest.mark.asyncio
async def test_reallocation_writes_suggestion_and_recommendation_log(
    db_session: AsyncSession,
) -> None:
    """§7.10 step 11 contract: every ReallocationSuggestion creates a
    matching RecommendationLog row (source heuristic_v1, tenant-scoped)."""
    week_ending = default_week_ending(date.today())
    org, client, market, _plan = await _build_scenario(
        db_session, suffix="alloc1", week_ending=week_ending
    )
    snapshot = await generate_snapshot(
        db_session,
        organization_id=org.id,
        client_id=client.id,
        market_id=market.id,
        week_ending=week_ending,
    )
    await db_session.commit()
    assert snapshot is not None

    suggestions = await compute_suggestions_for_snapshot(db_session, snapshot)
    await db_session.commit()
    assert len(suggestions) >= 1, "donor+receiver pair should produce at least one suggestion"

    for s in suggestions:
        assert s.scope == "within_market_within_channel"
        assert s.organization_id == org.id
        assert s.proposed_amount_local > 0
        # §7.10 step 11 + recommendation-log skill: RecommendationLog row exists.
        log_row = (
            await db_session.execute(
                select(RecommendationLog).where(col(RecommendationLog.suggestion_id) == s.id)
            )
        ).scalar_one()
        assert log_row.recommendation_source == "heuristic_v1"
        assert log_row.client_id == client.id
        assert log_row.organization_id == org.id


@pytest.mark.asyncio
async def test_reallocation_compatible_objective_types_only(
    db_session: AsyncSession,
) -> None:
    """Step 7 simplified: cross-objective pairs are skipped because their
    deltas have no shared unit. video_views donor + conversions receiver
    should produce no suggestion even when both are well-shaped."""
    week_ending = default_week_ending(date.today())
    org, client, market, _plan = await _build_scenario(
        db_session,
        suffix="alloc2",
        week_ending=week_ending,
        line_overrides=[
            # donor: video_views, overpaces + underperforms
            ("Video Views", "video_views", Decimal("560.00"), Decimal("180000"), 1.25, 0.70),
            # receiver: conversions, underpaces + overperforms — INCOMPATIBLE
            ("Conversions", "conversions", Decimal("1750.00"), Decimal("310"), 0.65, 1.45),
        ],
    )
    snapshot = await generate_snapshot(
        db_session,
        organization_id=org.id,
        client_id=client.id,
        market_id=market.id,
        week_ending=week_ending,
    )
    await db_session.commit()
    assert snapshot is not None
    suggestions = await compute_suggestions_for_snapshot(db_session, snapshot)
    await db_session.commit()
    assert suggestions == [], "cross-objective pairs must not produce suggestions in Phase 1a"
