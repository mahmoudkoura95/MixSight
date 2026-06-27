"""CSV actuals ingestion service.

The orchestration around `parse_meta_csv`: load → validate currency
against Market → per-row upsert into `Actuals` honoring the §7.14
idempotency unique constraint → write one `ConnectorPull` row capturing
the window + outcome → emit a `ConnectorAuthEvent` of the matching ADR-003
type (`csv_uploaded` / `csv_parse_failed` / `schema_mismatch` /
`partial_ingestion`).

Per-row ORM upsert (SELECT-by-key → UPDATE or INSERT) is chosen over a
bulk `INSERT ... ON CONFLICT` so the §7.4 audit hook fires per row. The
audit-log skill explicitly calls out bulk SQL as a hook bypass; for
Phase 1a CSV uploads (≤ a few hundred rows weekly) the per-row latency
is fine. When bulk perf is actually measured, switch to bulk SQL + manual
AuditLog writes per the skill's bypass guidance.

Restatement-threshold tracking (§7.14 `rows_revised`) lands in Phase 1c
alongside the connector health surface — Phase 1a counts every UPDATE as
a revision without the >5% threshold filter.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.connectors.csv.meta_ads_manager import (
    MetaActualsRecord,
    MetaCsvParseError,
    MetaCsvParseResult,
    MetaCsvSchemaMismatchError,
    parse_meta_csv,
)
from mixsight.logging import get_logger
from mixsight.models import Actuals, ConnectorAuthEvent, ConnectorPull, Market

log = get_logger("mixsight.connectors.csv")

_CHANNEL_META = "meta"
_SOURCE_CSV_UPLOAD = "csv_upload"
_PULL_TYPE_CSV_UPLOAD = "csv_upload"
_PLATFORM_META = "meta"


@dataclass(frozen=True)
class CsvIngestionResult:
    rows_fetched: int
    rows_inserted: int
    rows_revised: int
    pull_window_start: datetime | None
    pull_window_end: datetime | None
    currency: str


class CurrencyMismatchError(Exception):
    """CSV's spend column currency doesn't match the Market.local_currency."""


class MarketNotUnderClientError(Exception):
    """The named market exists but doesn't belong to the named client. A
    routing error, not a tenancy breach — the route maps it to 404."""


async def _emit_event(
    db: AsyncSession,
    *,
    organization_id: UUID,
    user_id: UUID | None,
    event_type: str,
    success: bool,
    error_message: str | None = None,
) -> None:
    db.add(
        ConnectorAuthEvent(
            organization_id=organization_id,
            platform=_PLATFORM_META,
            connector_auth_id=None,  # CSV upload has no OAuth credential
            event_type=event_type,
            user_id=user_id,
            success=success,
            error_message=error_message,
        )
    )


async def _upsert_actuals_row(
    db: AsyncSession,
    *,
    organization_id: UUID,
    client_id: UUID,
    market_id: UUID,
    record: MetaActualsRecord,
    pull_timestamp: datetime,
    pull_window_start: datetime,
    pull_window_end: datetime,
) -> bool:
    """Insert or update one Actuals row on the §7.14 idempotency key.
    Returns True if a new row was inserted, False if an existing one was
    updated."""
    stmt = select(Actuals).where(
        col(Actuals.client_id) == client_id,
        col(Actuals.market_id) == market_id,
        col(Actuals.channel) == _CHANNEL_META,
        col(Actuals.campaign_external_id) == record.campaign_external_id,
        col(Actuals.date) == record.date,
        col(Actuals.source) == _SOURCE_CSV_UPLOAD,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is None:
        db.add(
            Actuals(
                organization_id=organization_id,
                client_id=client_id,
                market_id=market_id,
                channel=_CHANNEL_META,
                campaign_external_id=record.campaign_external_id,
                campaign_label=record.campaign_label,
                date=record.date,
                spend_local=record.spend_local,
                impressions=record.impressions,
                clicks=record.clicks,
                conversions=record.conversions,
                conversions_value=record.conversions_value,
                source=_SOURCE_CSV_UPLOAD,
                pull_timestamp=pull_timestamp,
                pull_window_start=pull_window_start.date(),
                pull_window_end=pull_window_end.date(),
            )
        )
        return True

    existing.campaign_label = record.campaign_label
    existing.spend_local = record.spend_local
    existing.impressions = record.impressions
    existing.clicks = record.clicks
    existing.conversions = record.conversions
    existing.conversions_value = record.conversions_value
    existing.pull_timestamp = pull_timestamp
    existing.pull_window_start = pull_window_start.date()
    existing.pull_window_end = pull_window_end.date()
    db.add(existing)
    return False


async def ingest_meta_csv(
    db: AsyncSession,
    *,
    file_bytes: bytes,
    organization_id: UUID,
    client_id: UUID,
    market_id: UUID,
    user_id: UUID | None,
) -> CsvIngestionResult:
    """End-to-end ingestion. Caller is responsible for tenancy checks (the
    route's `enforce_client_access` dep) and for committing the session.

    On parse / schema failure: writes a failed `ConnectorPull` + a
    `ConnectorAuthEvent` (csv_parse_failed or schema_mismatch) into the
    session, then re-raises so the route layer can return 4xx. The caller
    still commits so the audit trail of the failed attempt persists.
    """
    pull_timestamp = datetime.now(UTC)
    market = await db.get(Market, market_id)
    if market is None or market.client_id != client_id:
        # Not a tenant breach (enforce_client_access already passed) and not a
        # connector failure either — just a market that isn't under this
        # client. No ConnectorAuthEvent; the route maps this to 404.
        raise MarketNotUnderClientError(
            f"market_id {market_id} does not belong to client_id {client_id}"
        )

    try:
        parsed: MetaCsvParseResult = parse_meta_csv(file_bytes)
    except MetaCsvSchemaMismatchError as e:
        await _emit_event(
            db,
            organization_id=organization_id,
            user_id=user_id,
            event_type="schema_mismatch",
            success=False,
            error_message=str(e),
        )
        db.add(
            ConnectorPull(
                organization_id=organization_id,
                client_id=client_id,
                market_id=market_id,
                platform=_PLATFORM_META,
                pull_window_start=pull_timestamp.date(),
                pull_window_end=pull_timestamp.date(),
                pull_type=_PULL_TYPE_CSV_UPLOAD,
                status="failed",
                error_message=str(e)[:500],
                attempted_at=pull_timestamp,
                completed_at=datetime.now(UTC),
            )
        )
        raise
    except MetaCsvParseError as e:
        await _emit_event(
            db,
            organization_id=organization_id,
            user_id=user_id,
            event_type="csv_parse_failed",
            success=False,
            error_message=str(e),
        )
        db.add(
            ConnectorPull(
                organization_id=organization_id,
                client_id=client_id,
                market_id=market_id,
                platform=_PLATFORM_META,
                pull_window_start=pull_timestamp.date(),
                pull_window_end=pull_timestamp.date(),
                pull_type=_PULL_TYPE_CSV_UPLOAD,
                status="failed",
                error_message=str(e)[:500],
                attempted_at=pull_timestamp,
                completed_at=datetime.now(UTC),
            )
        )
        raise

    if market.local_currency and parsed.currency != market.local_currency:
        msg = (
            f"CSV currency {parsed.currency} does not match Market.local_currency "
            f"{market.local_currency}"
        )
        await _emit_event(
            db,
            organization_id=organization_id,
            user_id=user_id,
            event_type="schema_mismatch",
            success=False,
            error_message=msg,
        )
        db.add(
            ConnectorPull(
                organization_id=organization_id,
                client_id=client_id,
                market_id=market_id,
                platform=_PLATFORM_META,
                pull_window_start=pull_timestamp.date(),
                pull_window_end=pull_timestamp.date(),
                pull_type=_PULL_TYPE_CSV_UPLOAD,
                status="failed",
                error_message=msg,
                attempted_at=pull_timestamp,
                completed_at=datetime.now(UTC),
            )
        )
        raise CurrencyMismatchError(msg)

    if not parsed.records:
        await _emit_event(
            db,
            organization_id=organization_id,
            user_id=user_id,
            event_type="partial_ingestion",
            success=True,
            error_message="CSV had no data rows",
        )
        db.add(
            ConnectorPull(
                organization_id=organization_id,
                client_id=client_id,
                market_id=market_id,
                platform=_PLATFORM_META,
                pull_window_start=pull_timestamp.date(),
                pull_window_end=pull_timestamp.date(),
                pull_type=_PULL_TYPE_CSV_UPLOAD,
                status="partial",
                rows_fetched=0,
                rows_upserted=0,
                attempted_at=pull_timestamp,
                completed_at=datetime.now(UTC),
            )
        )
        return CsvIngestionResult(
            rows_fetched=0,
            rows_inserted=0,
            rows_revised=0,
            pull_window_start=None,
            pull_window_end=None,
            currency=parsed.currency,
        )

    _midnight = datetime.min.time()
    window_start = datetime.combine(min(r.date for r in parsed.records), _midnight).replace(
        tzinfo=UTC
    )
    window_end = datetime.combine(max(r.date for r in parsed.records), _midnight).replace(
        tzinfo=UTC
    )
    inserted = 0
    revised = 0
    for record in parsed.records:
        is_new = await _upsert_actuals_row(
            db,
            organization_id=organization_id,
            client_id=client_id,
            market_id=market_id,
            record=record,
            pull_timestamp=pull_timestamp,
            pull_window_start=window_start,
            pull_window_end=window_end,
        )
        if is_new:
            inserted += 1
        else:
            revised += 1

    db.add(
        ConnectorPull(
            organization_id=organization_id,
            client_id=client_id,
            market_id=market_id,
            platform=_PLATFORM_META,
            pull_window_start=window_start.date(),
            pull_window_end=window_end.date(),
            pull_type=_PULL_TYPE_CSV_UPLOAD,
            status="success",
            rows_fetched=len(parsed.records),
            rows_upserted=inserted + revised,
            rows_revised=revised,
            attempted_at=pull_timestamp,
            completed_at=datetime.now(UTC),
        )
    )
    await _emit_event(
        db,
        organization_id=organization_id,
        user_id=user_id,
        event_type="csv_uploaded",
        success=True,
    )
    log.info(
        "csv.ingest.success",
        client_id=str(client_id),
        market_id=str(market_id),
        rows_fetched=len(parsed.records),
        rows_inserted=inserted,
        rows_revised=revised,
        currency=parsed.currency,
    )
    return CsvIngestionResult(
        rows_fetched=len(parsed.records),
        rows_inserted=inserted,
        rows_revised=revised,
        pull_window_start=window_start,
        pull_window_end=window_end,
        currency=parsed.currency,
    )
