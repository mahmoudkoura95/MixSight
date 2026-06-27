"""Meta Ads Manager native CSV parser.

Phase 1a Week 3 first §7.14 Protocol impl per ADR-003. Accepts the CSV
export Meta produces from Ads Manager when broken down by Day at campaign
level. Liberal header matching (case + whitespace insensitive, accepts
common Meta variants like "Link clicks" vs "Clicks (all)") with strict
required-column validation.

Currency is extracted from the spend column header — Meta always suffixes
it like "Amount spent (USD)" / "Amount spent (GBP)" — so the caller knows
which `Market.local_currency` the spend values are in without trusting
the AM to tag it.

Schema mismatches and bad row data raise specific exceptions the
ingestion service maps to the §7.4 / ADR-003 ConnectorAuthEvent types
(`schema_mismatch` vs `csv_parse_failed`).
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


class MetaCsvSchemaMismatchError(Exception):
    """Header is missing a required column or the spend column has no currency suffix."""


class MetaCsvParseError(Exception):
    """CSV body row is malformed (bad date, non-numeric spend, etc.)."""


@dataclass(frozen=True)
class MetaActualsRecord:
    campaign_external_id: str
    campaign_label: str
    date: date
    spend_local: Decimal
    impressions: int | None
    clicks: int | None
    conversions: Decimal | None
    conversions_value: Decimal | None


@dataclass(frozen=True)
class MetaCsvParseResult:
    records: list[MetaActualsRecord]
    currency: str  # ISO 4217, extracted from the spend column header


# Header → candidate column names. Match is case-insensitive on stripped value.
_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "date": ("reporting starts", "day"),
    "campaign_external_id": ("campaign id",),
    "campaign_label": ("campaign name",),
}

# Spend column matches via regex because the currency code is embedded.
_SPEND_HEADER_RE = re.compile(r"^amount spent\s*\(([A-Za-z]{3})\)$")

# Optional fields — first match wins per tuple.
_OPTIONAL_FIELDS: dict[str, tuple[str, ...]] = {
    "impressions": ("impressions",),
    "clicks": ("link clicks", "clicks (all)"),
    "conversions": ("results", "purchases"),
    "conversions_value": ("purchases conversion value", "conversion value"),
}


def _normalize(header: str) -> str:
    return header.strip().lower()


def _resolve_column_indices(headers: list[str]) -> tuple[dict[str, int], str]:
    norm = [_normalize(h) for h in headers]
    resolved: dict[str, int] = {}

    for field, candidates in _REQUIRED_FIELDS.items():
        for cand in candidates:
            if cand in norm:
                resolved[field] = norm.index(cand)
                break
        if field not in resolved:
            raise MetaCsvSchemaMismatchError(
                f"Required column for '{field}' not found. "
                f"Expected one of {list(candidates)}; got {headers}"
            )

    # Spend + currency.
    currency: str | None = None
    for idx, h in enumerate(norm):
        m = _SPEND_HEADER_RE.match(h)
        if m:
            resolved["spend_local"] = idx
            currency = m.group(1).upper()
            break
    if currency is None:
        raise MetaCsvSchemaMismatchError(
            "Spend column missing or has no currency suffix. "
            "Expected 'Amount spent (USD)' style header."
        )

    for field, candidates in _OPTIONAL_FIELDS.items():
        for cand in candidates:
            if cand in norm:
                resolved[field] = norm.index(cand)
                break

    return resolved, currency


def _parse_date(value: str) -> date:
    # Meta exports use ISO-style YYYY-MM-DD; tolerate trailing whitespace.
    try:
        return date.fromisoformat(value.strip())
    except ValueError as e:
        raise MetaCsvParseError(f"Invalid date {value!r}: {e}") from e


def _parse_decimal(value: str, *, field: str) -> Decimal | None:
    s = value.strip()
    if not s:
        return None
    # Meta exports include thousands separators in some locales; strip commas.
    s = s.replace(",", "")
    try:
        return Decimal(s)
    except InvalidOperation as e:
        raise MetaCsvParseError(f"Invalid {field} value {value!r}") from e


def _parse_int(value: str, *, field: str) -> int | None:
    s = value.strip().replace(",", "")
    if not s:
        return None
    try:
        return int(s)
    except ValueError as e:
        raise MetaCsvParseError(f"Invalid {field} value {value!r}") from e


def parse_meta_csv(file_bytes: bytes) -> MetaCsvParseResult:
    """Parse a Meta Ads Manager native CSV export into typed records.

    Raises `MetaCsvSchemaMismatchError` for header problems (maps to
    `ConnectorAuthEvent(event_type='schema_mismatch')`) and
    `MetaCsvParseError` for body row problems (maps to `csv_parse_failed`).
    Currency is returned alongside records so the caller can flag a
    Market.local_currency mismatch instead of silently writing wrong values.
    """
    # Meta exports are UTF-8 with BOM more often than not.
    text = file_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(text))
    try:
        headers = next(reader)
    except StopIteration as e:
        raise MetaCsvSchemaMismatchError("CSV is empty") from e

    cols, currency = _resolve_column_indices(headers)
    records: list[MetaActualsRecord] = []
    for line_no, row in enumerate(reader, start=2):
        if not row or all(not c.strip() for c in row):
            continue  # tolerate blank trailing lines
        try:
            records.append(
                MetaActualsRecord(
                    campaign_external_id=row[cols["campaign_external_id"]].strip(),
                    campaign_label=row[cols["campaign_label"]].strip(),
                    date=_parse_date(row[cols["date"]]),
                    spend_local=(
                        _parse_decimal(row[cols["spend_local"]], field="spend") or Decimal(0)
                    ),
                    impressions=(
                        _parse_int(row[cols["impressions"]], field="impressions")
                        if "impressions" in cols
                        else None
                    ),
                    clicks=(
                        _parse_int(row[cols["clicks"]], field="clicks")
                        if "clicks" in cols
                        else None
                    ),
                    conversions=(
                        _parse_decimal(row[cols["conversions"]], field="conversions")
                        if "conversions" in cols
                        else None
                    ),
                    conversions_value=(
                        _parse_decimal(row[cols["conversions_value"]], field="conversions_value")
                        if "conversions_value" in cols
                        else None
                    ),
                )
            )
        except IndexError as e:
            raise MetaCsvParseError(f"Line {line_no}: row shorter than header") from e
        except MetaCsvParseError as e:
            raise MetaCsvParseError(f"Line {line_no}: {e}") from e

    return MetaCsvParseResult(records=records, currency=currency)
