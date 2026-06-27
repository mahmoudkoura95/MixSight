"""End-to-end test of POST /clients/{client_id}/markets/{market_id}/csv/actuals.

The tenancy_isolated cross-tenant case (user_b uploads to user_a's client →
404) is the §7.19 contract this test exists for. Happy-path uploads,
parser failure mapping, etc. live in the service test — this file only
proves the route layer wires correctly and tenancy holds.
"""

from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.models import Actuals, Client, Market, User

_CSV = (
    b"Reporting starts,Campaign ID,Campaign name,Amount spent (GBP),"
    b"Impressions,Link clicks\n"
    b"2026-06-23,c_001,Endpoint Test,100.00,1000,50\n"
)


async def _make_client_and_market(
    db: AsyncSession, user: User, *, name: str
) -> tuple[Client, Market]:
    client = Client(organization_id=user.organization_id, name=name)
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
    return client, market


@pytest.mark.asyncio
@pytest.mark.tenancy_isolated
async def test_upload_csv_succeeds_and_blocks_cross_tenant_user(
    db_session: AsyncSession,
    user_a_in_org_1: User,
    user_b_in_org_2: User,
    authenticated_client_a: httpx.AsyncClient,
    authenticated_client_b: httpx.AsyncClient,
) -> None:
    client_a, market_a = await _make_client_and_market(db_session, user_a_in_org_1, name="A")

    # 1. user_a uploads to their own client/market → 200 + Actuals rows persist.
    resp_a = await authenticated_client_a.post(
        f"/clients/{client_a.id}/markets/{market_a.id}/csv/actuals",
        files={"file": ("meta.csv", _CSV, "text/csv")},
    )
    assert resp_a.status_code == 200, resp_a.text
    body = resp_a.json()
    assert body["rows_fetched"] == 1
    assert body["rows_inserted"] == 1
    assert body["currency"] == "GBP"

    rows = (
        (await db_session.execute(select(Actuals).where(col(Actuals.client_id) == client_a.id)))
        .scalars()
        .all()
    )
    assert len(list(rows)) == 1

    # 2. user_b (different org) hits user_a's client → 404 per §7.19
    # (cross-org returns 404 to avoid leaking client existence).
    resp_b = await authenticated_client_b.post(
        f"/clients/{client_a.id}/markets/{market_a.id}/csv/actuals",
        files={"file": ("meta.csv", _CSV, "text/csv")},
    )
    assert resp_b.status_code == 404, resp_b.text
