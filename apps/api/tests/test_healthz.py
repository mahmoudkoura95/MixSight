"""Smoke test: /healthz returns 200 and reflects the configured environment.

Requires Postgres to be reachable (CI brings up the docker-compose service
before running pytest).
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from mixsight.main import app


@pytest.mark.asyncio
async def test_healthz_ok() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] in {"development", "staging", "production"}
