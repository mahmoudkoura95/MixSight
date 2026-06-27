"""Endpoint test for GET /clients/{client_id}/markets/{market_id}/pacing
and /reallocation-suggestions, including the §7.19 cross-tenant case."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mixsight.models import Actuals, Client, Market, Plan, PlanLine, User
from mixsight.pacing.service import default_week_ending


async def _seed_for_user(db: AsyncSession, user: User) -> tuple[Client, Market]:
    """Build a single-campaign donor scenario under `user`'s org."""
    client = Client(organization_id=user.organization_id, name="Endpoint NB EMEA")
    db.add(client)
    await db.commit()
    await db.refresh(client)
    market = Market(
        organization_id=user.organization_id,
        client_id=client.id,
        code="UK",
        local_currency="GBP",
    )
    db.add(market)
    await db.commit()
    await db.refresh(market)

    # UTC to match the endpoint (which uses datetime.now(UTC).date()); local
    # date.today() can sit a day — and across the Sunday boundary, a whole
    # week — off the endpoint's week_ending.
    week_ending = default_week_ending(datetime.now(UTC).date())
    period_start = week_ending - timedelta(days=6)
    plan = Plan(
        organization_id=user.organization_id,
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

    # One donor + one receiver, same objective_type → at least one suggestion.
    for label, weekly_spend, weekly_kpi, sm, km in [
        ("Brand Search", Decimal("1400.00"), Decimal("280"), 1.25, 0.70),
        ("Prospecting", Decimal("2100.00"), Decimal("180"), 0.65, 1.45),
    ]:
        line = PlanLine(
            organization_id=user.organization_id,
            plan_id=plan.id,
            market_id=market.id,
            channel="meta",
            campaign_label=label,
            period_start=period_start,
            period_end=week_ending,
            planned_spend_local=weekly_spend,
            objective_type="conversions",
            kpi_target=weekly_kpi,
        )
        db.add(line)
        daily_spend = (weekly_spend * Decimal(str(sm))) / Decimal(7)
        daily_kpi = (weekly_kpi * Decimal(str(km))) / Decimal(7)
        pull_window_start = period_start - timedelta(days=7)
        for d_offset in range(14):
            d = pull_window_start + timedelta(days=d_offset)
            db.add(
                Actuals(
                    organization_id=user.organization_id,
                    client_id=client.id,
                    market_id=market.id,
                    channel="meta",
                    campaign_external_id=f"camp_{label.lower().replace(' ', '_')}",
                    campaign_label=label,
                    date=d,
                    spend_local=daily_spend.quantize(Decimal("0.0001")),
                    conversions=daily_kpi.quantize(Decimal("0.0001")),
                    source="csv_upload",
                    pull_timestamp=datetime.now(UTC),
                    pull_window_start=pull_window_start,
                    pull_window_end=week_ending,
                )
            )
    await db.commit()
    return client, market


@pytest.mark.asyncio
@pytest.mark.tenancy_isolated
async def test_pacing_and_reallocation_endpoints_with_cross_tenant_isolation(
    db_session: AsyncSession,
    user_a_in_org_1: User,
    user_b_in_org_2: User,
    authenticated_client_a: httpx.AsyncClient,
    authenticated_client_b: httpx.AsyncClient,
) -> None:
    client_a, market_a = await _seed_for_user(db_session, user_a_in_org_1)

    # 1. user_a hits pacing on their own client → 200 with snapshot + lines.
    resp = await authenticated_client_a.get(f"/clients/{client_a.id}/markets/{market_a.id}/pacing")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["snapshot"] is not None
    assert body["currency"] == "GBP"
    assert len(body["lines"]) == 2

    # 2. user_a hits reallocation suggestions → 200 with at least one option.
    resp = await authenticated_client_a.get(
        f"/clients/{client_a.id}/markets/{market_a.id}/reallocation-suggestions"
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["snapshot_id"] is not None
    assert len(body["suggestions"]) >= 1
    s = body["suggestions"][0]
    assert s["scope"] == "within_market_within_channel"
    assert "Option:" in (s["rationale_text"] or ""), "framing must be options-not-recommendations"

    # 3. user_b (different org) → 404 on both endpoints per §7.19 don't-leak.
    resp = await authenticated_client_b.get(f"/clients/{client_a.id}/markets/{market_a.id}/pacing")
    assert resp.status_code == 404, resp.text
    resp = await authenticated_client_b.get(
        f"/clients/{client_a.id}/markets/{market_a.id}/reallocation-suggestions"
    )
    assert resp.status_code == 404, resp.text
