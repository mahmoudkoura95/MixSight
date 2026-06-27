"""Seed script for the New Balance EMEA / Brave Bison demo scenario.

Idempotent: re-running upserts every row by natural keys (clerk_organization_id,
client.name, market.code, plan.version, plan_line.(channel, campaign_label),
actuals.unique_pull). Safe to run repeatedly during development; one row per
business entity persists regardless of how many times the script fires.

Phase 1a Week 3 scope per CURRENT_PHASE.md decision (rich generator):
  - 1 Organization: Brave Bison Agency
  - 1 Client: New Balance EMEA
  - 1 Market: UK / GBP
  - 1 active Plan covering the current Monday–Sunday week
  - 6 PlanLines (Meta channel only — single-channel per §7.3)
  - 14 days of Actuals per campaign, shaped so pacing has visible
    donors (overpacing + underperforming) AND receivers (underpacing +
    overperforming) — exercises the §7.10 reallocation algorithm.

Used by integration tests + Week 4 internal-acceptance demo. Phase 1b will
extend with real Brave Bison data via API connectors; this script becomes
the synthetic-fallback for tests that should not depend on prod data.
"""

from __future__ import annotations

import asyncio
import random
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.config import get_settings
from mixsight.db import engine
from mixsight.models import (
    Actuals,
    Client,
    Market,
    Organization,
    Plan,
    PlanLine,
)

# Stable seed so re-runs produce identical Actuals; lets tests assert
# specific values instead of just shapes. Deterministic test data is not
# a security boundary — S311 doesn't apply.
_RNG = random.Random(20260626)  # noqa: S311

_ORG_CLERK_ID = "seed_org_brave_bison"
_CLIENT_NAME = "New Balance EMEA"
_MARKET_CODE = "UK"


# (campaign_id, label, objective_type, planned_spend_weekly_GBP, planned_kpi,
#  actuals_spend_modifier, actuals_kpi_modifier)
#
# spend_modifier > 1.0 → campaign overpaces (donor candidate)
# kpi_modifier   > 1.0 → campaign overperforms (receiver candidate)
_CAMPAIGNS: list[tuple[str, str, str, Decimal, Decimal, float, float]] = [
    # donor: overpaces, underperforms
    (
        "nb_uk_brand_search",
        "NB UK · Brand Search",
        "conversions",
        Decimal("1400.00"),
        Decimal("280"),
        1.25,
        0.70,
    ),
    # receiver: underpaces, overperforms
    (
        "nb_uk_prospecting_pmax",
        "NB UK · Prospecting PMax",
        "conversions",
        Decimal("2100.00"),
        Decimal("180"),
        0.65,
        1.45,
    ),
    # on-pace, mid-performance
    (
        "nb_uk_retargeting_dpa",
        "NB UK · Retargeting DPA",
        "conversions",
        Decimal("980.00"),
        Decimal("220"),
        1.02,
        0.98,
    ),
    # donor: overpaces, underperforms
    (
        "nb_uk_video_views",
        "NB UK · Video Views",
        "video_views",
        Decimal("560.00"),
        Decimal("180000"),
        1.18,
        0.78,
    ),
    # receiver: underpaces, overperforms
    (
        "nb_uk_advantage_plus",
        "NB UK · Advantage+ Shopping",
        "conversions",
        Decimal("1750.00"),
        Decimal("310"),
        0.72,
        1.35,
    ),
    # on-pace, on-performance
    (
        "nb_uk_reach",
        "NB UK · Reach Top-Funnel",
        "reach",
        Decimal("420.00"),
        Decimal("950000"),
        1.01,
        1.00,
    ),
]


def _current_week_window(today: date) -> tuple[date, date]:
    """Monday → Sunday containing `today`."""
    monday = today - timedelta(days=today.weekday())
    return monday, monday + timedelta(days=6)


async def _upsert_organization(db: AsyncSession, clerk_org_id: str) -> Organization:
    existing = (
        await db.execute(
            select(Organization).where(col(Organization.clerk_organization_id) == clerk_org_id)
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    org = Organization(name="Brave Bison Agency", clerk_organization_id=clerk_org_id)
    db.add(org)
    await db.flush()
    return org


async def _upsert_client(db: AsyncSession, org: Organization) -> Client:
    existing = (
        await db.execute(
            select(Client).where(
                col(Client.organization_id) == org.id,
                col(Client.name) == _CLIENT_NAME,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    client = Client(
        organization_id=org.id,
        name=_CLIENT_NAME,
        reporting_currency="GBP",
        default_allocation_mode="mode_a",
    )
    db.add(client)
    await db.flush()
    return client


async def _upsert_market(db: AsyncSession, org: Organization, client: Client) -> Market:
    existing = (
        await db.execute(
            select(Market).where(
                col(Market.client_id) == client.id,
                col(Market.code) == _MARKET_CODE,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    market = Market(
        organization_id=org.id,
        client_id=client.id,
        code=_MARKET_CODE,
        local_currency="GBP",
        local_timezone="Europe/London",
    )
    db.add(market)
    await db.flush()
    return market


async def _upsert_plan(
    db: AsyncSession, org: Organization, client: Client, period_start: date, period_end: date
) -> Plan:
    existing = (
        await db.execute(
            select(Plan).where(
                col(Plan.client_id) == client.id,
                col(Plan.period_start) == period_start,
                col(Plan.period_end) == period_end,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    plan = Plan(
        organization_id=org.id,
        client_id=client.id,
        version=1,
        source_method="template",
        status="active",
        period_start=period_start,
        period_end=period_end,
        currency_handling="local",
        change_summary="Initial seed plan for NB EMEA UK Meta Phase 1a Week 3 demo.",
    )
    db.add(plan)
    await db.flush()
    return plan


async def _upsert_plan_lines(
    db: AsyncSession,
    org: Organization,
    plan: Plan,
    market: Market,
    period_start: date,
    period_end: date,
) -> list[tuple[PlanLine, tuple[str, str, str, Decimal, Decimal, float, float]]]:
    pairs: list[tuple[PlanLine, tuple[str, str, str, Decimal, Decimal, float, float]]] = []
    for campaign_id, label, objective_type, spend, kpi, _sm, _km in _CAMPAIGNS:
        existing = (
            await db.execute(
                select(PlanLine).where(
                    col(PlanLine.plan_id) == plan.id,
                    col(PlanLine.market_id) == market.id,
                    col(PlanLine.campaign_label) == label,
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            existing = PlanLine(
                organization_id=org.id,
                plan_id=plan.id,
                market_id=market.id,
                channel="meta",
                campaign_label=label,
                period_start=period_start,
                period_end=period_end,
                planned_spend_local=spend,
                planned_spend_reporting=spend,
                objective_type=objective_type,
                kpi_target=kpi,
                extraction_confidence="high",
            )
            db.add(existing)
            await db.flush()
        pairs.append((existing, (campaign_id, label, objective_type, spend, kpi, _sm, _km)))
    return pairs


async def _upsert_actuals(
    db: AsyncSession,
    org: Organization,
    client: Client,
    market: Market,
    plan_lines: list[tuple[PlanLine, tuple[str, str, str, Decimal, Decimal, float, float]]],
    period_start: date,
    period_end: date,
) -> int:
    """Build 14 days of daily Actuals per campaign — the previous week
    plus the current week so insufficient_data thresholds don't trip."""
    pull_timestamp = datetime.now(UTC)
    pull_window_start = period_start - timedelta(days=7)
    pull_window_end = period_end
    inserted = 0

    for _plan_line, params in plan_lines:
        campaign_id, label, _obj, weekly_spend, weekly_kpi, sm, km = params
        daily_spend = (weekly_spend * Decimal(str(sm))) / Decimal(7)
        daily_kpi = (weekly_kpi * Decimal(str(km))) / Decimal(7)

        for day_offset in range(14):
            d = pull_window_start + timedelta(days=day_offset)
            # ±15% jitter so charts look real, deterministic via _RNG seed.
            jitter_spend = Decimal(str(1.0 + _RNG.uniform(-0.15, 0.15)))
            jitter_kpi = Decimal(str(1.0 + _RNG.uniform(-0.15, 0.15)))
            row_spend = (daily_spend * jitter_spend).quantize(Decimal("0.0001"))
            row_kpi = (daily_kpi * jitter_kpi).quantize(Decimal("0.0001"))

            existing = (
                await db.execute(
                    select(Actuals).where(
                        col(Actuals.client_id) == client.id,
                        col(Actuals.market_id) == market.id,
                        col(Actuals.channel) == "meta",
                        col(Actuals.campaign_external_id) == campaign_id,
                        col(Actuals.date) == d,
                        col(Actuals.source) == "csv_upload",
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                db.add(
                    Actuals(
                        organization_id=org.id,
                        client_id=client.id,
                        market_id=market.id,
                        channel="meta",
                        campaign_external_id=campaign_id,
                        campaign_label=label,
                        date=d,
                        spend_local=row_spend,
                        spend_reporting=row_spend,
                        impressions=int(row_kpi * Decimal(120)),  # rough proxy
                        clicks=int(row_kpi * Decimal("2.5")),
                        conversions=row_kpi,
                        conversions_value=row_kpi * Decimal("38.50"),
                        source="csv_upload",
                        pull_timestamp=pull_timestamp,
                        pull_window_start=pull_window_start,
                        pull_window_end=pull_window_end,
                    )
                )
                inserted += 1
            else:
                existing.spend_local = row_spend
                existing.conversions = row_kpi
                existing.conversions_value = row_kpi * Decimal("38.50")
                db.add(existing)
    return inserted


async def seed(*, dry_run: bool = False) -> None:
    print(  # noqa: T201 — seed scripts emit to stdout
        f"[seed] starting at {datetime.now(UTC).isoformat()}", flush=True
    )
    today = date.today()
    period_start, period_end = _current_week_window(today)
    print(f"[seed] week window: {period_start} -> {period_end}", flush=True)  # noqa: T201

    # Local demo: attach the demo data to the operator's real Clerk org (set
    # SEED_CLERK_ORG_ID) so a signed-in user passes the §7.19 tenancy check
    # and can actually load the pacing surface. Falls back to a synthetic id
    # (used by nobody's real login) for pure data-shape seeding.
    clerk_org_id = get_settings().SEED_CLERK_ORG_ID or _ORG_CLERK_ID
    if clerk_org_id == _ORG_CLERK_ID:
        print(  # noqa: T201
            "[seed] WARNING: SEED_CLERK_ORG_ID unset — data attaches to a "
            "synthetic org no real login owns; the pacing page will 404 for "
            "you. Set SEED_CLERK_ORG_ID to your Clerk org id to demo it.",
            flush=True,
        )

    async with AsyncSession(engine, expire_on_commit=False) as db:
        org = await _upsert_organization(db, clerk_org_id)
        client = await _upsert_client(db, org)
        market = await _upsert_market(db, org, client)
        plan = await _upsert_plan(db, org, client, period_start, period_end)
        plan_lines = await _upsert_plan_lines(db, org, plan, market, period_start, period_end)
        inserted_actuals = await _upsert_actuals(
            db, org, client, market, plan_lines, period_start, period_end
        )

        if dry_run:
            await db.rollback()
            print("[seed] dry run — rolled back.", flush=True)  # noqa: T201
            return
        await db.commit()

    pacing_path = f"/clients/{client.id}/markets/{market.id}/pacing"
    print(  # noqa: T201
        f"[seed] done. org={org.id} client={client.id} market={market.id} "
        f"plan={plan.id} plan_lines={len(plan_lines)} new_actuals={inserted_actuals}",
        flush=True,
    )
    print(  # noqa: T201
        f"[seed] demo pacing path: {pacing_path}\n"
        f"[seed]   → set NEXT_PUBLIC_DEMO_PACING_PATH={pacing_path} in .env to "
        f"link it from the home page.",
        flush=True,
    )


def main() -> None:
    import sys

    dry_run = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry_run))


if __name__ == "__main__":
    main()
