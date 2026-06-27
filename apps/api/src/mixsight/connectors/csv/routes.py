"""POST /clients/{client_id}/markets/{market_id}/csv/actuals.

The Phase 1a Week 3 entry point for CSV-uploaded actuals per ADR-003.
AM uploads a Meta Ads Manager native CSV; the service parses, upserts to
`Actuals` honoring §7.14 idempotency, and writes the `ConnectorPull` +
`ConnectorAuthEvent` audit trail.

Tenancy: `enforce_client_access` per §7.19. The service additionally
verifies the named market belongs to the client (cross-market within-org
isn't a tenancy breach but is still a routing error → 404).

Failure handling commits before raising so the failed-attempt audit row
(`ConnectorPull(status='failed')` + `ConnectorAuthEvent(success=False)`)
is persisted. Without that commit the get_db cleanup would roll back the
audit and we'd lose evidence of the parse failure — exactly the kind of
silent hole §7.4 exists to prevent.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from mixsight.auth.dependencies import current_user
from mixsight.connectors.csv.meta_ads_manager import (
    MetaCsvParseError,
    MetaCsvSchemaMismatchError,
)
from mixsight.connectors.csv.service import (
    CurrencyMismatchError,
    MarketNotUnderClientError,
    ingest_meta_csv,
)
from mixsight.db import get_db
from mixsight.models.user import User
from mixsight.tenancy import enforce_client_access

router = APIRouter(prefix="/clients", tags=["csv-actuals"])


@router.post("/{client_id}/markets/{market_id}/csv/actuals")
async def upload_meta_csv_actuals(
    client_id: UUID,
    market_id: UUID,
    file: UploadFile = File(...),  # noqa: B008 — FastAPI dependency-style default
    user: User = Depends(current_user),
    _: None = Depends(enforce_client_access),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    body = await file.read()
    try:
        result = await ingest_meta_csv(
            db,
            file_bytes=body,
            organization_id=user.organization_id,
            client_id=client_id,
            market_id=market_id,
            user_id=user.id,
        )
    except MarketNotUnderClientError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "market_not_found", "message": "Market not found"},
        ) from e
    except MetaCsvSchemaMismatchError as e:
        await db.commit()  # persist the failure audit row
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "csv_schema_mismatch", "message": str(e)},
        ) from e
    except MetaCsvParseError as e:
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "csv_parse_failed", "message": str(e)},
        ) from e
    except CurrencyMismatchError as e:
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "csv_currency_mismatch", "message": str(e)},
        ) from e

    await db.commit()
    return {
        "rows_fetched": result.rows_fetched,
        "rows_inserted": result.rows_inserted,
        "rows_revised": result.rows_revised,
        "currency": result.currency,
        "pull_window_start": (
            result.pull_window_start.isoformat() if result.pull_window_start else None
        ),
        "pull_window_end": (result.pull_window_end.isoformat() if result.pull_window_end else None),
    }
