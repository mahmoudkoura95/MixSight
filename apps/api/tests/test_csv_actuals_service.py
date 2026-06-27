"""Integration tests for the CSV actuals ingestion service.

Exercises the full Day 3 service contract: parse + per-row Actuals upsert
honoring §7.14 idempotency + ConnectorPull row + ConnectorAuthEvent per
ADR-003 event types. Bypasses the HTTP layer (covered by
`test_csv_actuals_endpoint`) and calls `ingest_meta_csv` directly so each
contract is asserted in isolation.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.connectors.csv.meta_ads_manager import MetaCsvSchemaMismatchError
from mixsight.connectors.csv.service import CurrencyMismatchError, ingest_meta_csv
from mixsight.models import Actuals, Client, ConnectorAuthEvent, ConnectorPull, Market, Organization

_CSV_HEADER = (
    "Reporting starts,Campaign ID,Campaign name,Amount spent (GBP),"
    "Impressions,Link clicks,Results,Purchases conversion value\n"
)


def _csv(*rows: str) -> bytes:
    return (_CSV_HEADER + "\n".join(rows) + "\n").encode("utf-8")


async def _build_tenant(
    db: AsyncSession, *, suffix: str, local_currency: str = "GBP"
) -> tuple[Organization, Client, Market]:
    org = Organization(name=f"Org {suffix}", clerk_organization_id=f"clerk_org_{suffix}")
    db.add(org)
    await db.commit()
    await db.refresh(org)
    client = Client(organization_id=org.id, name=f"Client {suffix}")
    db.add(client)
    await db.commit()
    await db.refresh(client)
    market = Market(
        organization_id=org.id,
        client_id=client.id,
        code=f"M{suffix}",
        local_currency=local_currency,
    )
    db.add(market)
    await db.commit()
    await db.refresh(market)
    return org, client, market


@pytest.mark.asyncio
async def test_ingest_csv_writes_actuals_pull_and_event(db_session: AsyncSession) -> None:
    org, client, market = await _build_tenant(db_session, suffix="svc1")
    body = _csv(
        "2026-06-23,c_001,Brand Search,100.00,1000,50,2.0,500.00",
        "2026-06-24,c_002,Prospecting,250.00,5000,120,4.0,1200.00",
    )

    result = await ingest_meta_csv(
        db_session,
        file_bytes=body,
        organization_id=org.id,
        client_id=client.id,
        market_id=market.id,
        user_id=None,
    )
    await db_session.commit()

    assert result.rows_fetched == 2
    assert result.rows_inserted == 2
    assert result.rows_revised == 0
    assert result.currency == "GBP"

    actuals = list(
        (
            await db_session.execute(
                select(Actuals).where(col(Actuals.client_id) == client.id).order_by(Actuals.date)
            )
        )
        .scalars()
        .all()
    )
    assert len(actuals) == 2
    assert actuals[0].organization_id == org.id  # Day 1 denormalization holds
    assert actuals[0].source == "csv_upload"
    assert actuals[0].channel == "meta"
    assert actuals[0].spend_local == Decimal("100.00")
    assert actuals[1].clicks == 120

    pull = (
        await db_session.execute(
            select(ConnectorPull).where(col(ConnectorPull.client_id) == client.id)
        )
    ).scalar_one()
    assert pull.status == "success"
    assert pull.rows_fetched == 2
    assert pull.rows_upserted == 2
    assert pull.pull_type == "csv_upload"
    assert pull.platform == "meta"

    event = (
        await db_session.execute(
            select(ConnectorAuthEvent).where(col(ConnectorAuthEvent.organization_id) == org.id)
        )
    ).scalar_one()
    assert event.event_type == "csv_uploaded"
    assert event.success is True


@pytest.mark.asyncio
async def test_reupload_is_idempotent_and_counts_revisions(db_session: AsyncSession) -> None:
    """Second upload of overlapping (campaign, date) tuples updates not duplicates."""
    org, client, market = await _build_tenant(db_session, suffix="svc2")
    first = _csv("2026-06-23,c_001,Initial,100.00,1000,50,2.0,500.00")
    await ingest_meta_csv(
        db_session,
        file_bytes=first,
        organization_id=org.id,
        client_id=client.id,
        market_id=market.id,
        user_id=None,
    )
    await db_session.commit()

    # Same (campaign, date), different values.
    second = _csv("2026-06-23,c_001,Renamed,150.00,2000,80,3.0,700.00")
    result = await ingest_meta_csv(
        db_session,
        file_bytes=second,
        organization_id=org.id,
        client_id=client.id,
        market_id=market.id,
        user_id=None,
    )
    await db_session.commit()
    assert result.rows_inserted == 0
    assert result.rows_revised == 1

    actuals = list(
        (await db_session.execute(select(Actuals).where(col(Actuals.client_id) == client.id)))
        .scalars()
        .all()
    )
    assert len(actuals) == 1
    assert actuals[0].spend_local == Decimal("150.00")
    assert actuals[0].campaign_label == "Renamed"


@pytest.mark.asyncio
async def test_schema_mismatch_persists_failed_pull_and_event(
    db_session: AsyncSession,
) -> None:
    org, client, market = await _build_tenant(db_session, suffix="svc3")
    bad = b"some,other,headers\nnot,really,meta\n"
    with pytest.raises(MetaCsvSchemaMismatchError):
        await ingest_meta_csv(
            db_session,
            file_bytes=bad,
            organization_id=org.id,
            client_id=client.id,
            market_id=market.id,
            user_id=None,
        )
    await db_session.commit()

    pull = (
        await db_session.execute(
            select(ConnectorPull).where(col(ConnectorPull.client_id) == client.id)
        )
    ).scalar_one()
    assert pull.status == "failed"
    event = (
        await db_session.execute(
            select(ConnectorAuthEvent).where(col(ConnectorAuthEvent.organization_id) == org.id)
        )
    ).scalar_one()
    assert event.event_type == "schema_mismatch"
    assert event.success is False


@pytest.mark.asyncio
async def test_currency_mismatch_raises_and_persists_failure(
    db_session: AsyncSession,
) -> None:
    """Market is GBP but the CSV's spend column says USD."""
    org, client, market = await _build_tenant(db_session, suffix="svc4", local_currency="GBP")
    body = (
        b"Reporting starts,Campaign ID,Campaign name,Amount spent (USD)\n"
        b"2026-06-23,c_001,T,100.00\n"
    )
    with pytest.raises(CurrencyMismatchError):
        await ingest_meta_csv(
            db_session,
            file_bytes=body,
            organization_id=org.id,
            client_id=client.id,
            market_id=market.id,
            user_id=None,
        )
    await db_session.commit()

    event = (
        await db_session.execute(
            select(ConnectorAuthEvent).where(col(ConnectorAuthEvent.organization_id) == org.id)
        )
    ).scalar_one()
    assert event.event_type == "schema_mismatch"
    pull = (
        await db_session.execute(
            select(ConnectorPull).where(col(ConnectorPull.client_id) == client.id)
        )
    ).scalar_one()
    assert pull.status == "failed"
