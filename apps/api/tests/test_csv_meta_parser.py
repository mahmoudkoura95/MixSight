"""Unit tests for the Meta Ads Manager native CSV parser.

The parser's contract:
- Required columns: campaign id, campaign name, reporting starts, amount spent (CCY).
- Optional columns: impressions, link clicks/clicks (all), results/purchases,
  purchases conversion value.
- Currency code extracted from the spend column header.
- Schema problems raise `MetaCsvSchemaMismatchError`; body problems raise
  `MetaCsvParseError` — the service maps each to the matching
  `ConnectorAuthEvent` type from ADR-003.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from mixsight.connectors.csv.meta_ads_manager import (
    MetaCsvParseError,
    MetaCsvSchemaMismatchError,
    parse_meta_csv,
)

_HEADER = (
    "Reporting starts,Reporting ends,Campaign ID,Campaign name,"
    "Amount spent (GBP),Impressions,Link clicks,Results,"
    "Purchases conversion value\n"
)


def _csv(*rows: str) -> bytes:
    return (_HEADER + "\n".join(rows) + "\n").encode("utf-8")


def test_happy_path_parses_all_optional_fields() -> None:
    body = _csv(
        "2026-06-23,2026-06-23,c_001,Brand Search UK,123.4500,12000,450,7.5,1899.99",
        "2026-06-24,2026-06-24,c_002,Prospecting UK,2,500.50,98000,2100,12,3000.00",
    )
    # Note row 2 has a thousands-separator in spend — parser strips commas.
    body = (
        _HEADER
        + "2026-06-23,2026-06-23,c_001,Brand Search UK,123.4500,12000,450,7.5,1899.99\n"
        + '2026-06-24,2026-06-24,c_002,Prospecting UK,"2,500.50",98000,2100,12,3000.00\n'
    ).encode("utf-8")

    result = parse_meta_csv(body)

    assert result.currency == "GBP"
    assert len(result.records) == 2
    r1, r2 = result.records
    assert r1.campaign_external_id == "c_001"
    assert r1.campaign_label == "Brand Search UK"
    assert r1.date == date(2026, 6, 23)
    assert r1.spend_local == Decimal("123.4500")
    assert r1.impressions == 12000
    assert r1.clicks == 450
    assert r1.conversions == Decimal("7.5")
    assert r1.conversions_value == Decimal("1899.99")
    assert r2.spend_local == Decimal("2500.50")  # thousands-separator stripped


def test_currency_extracted_from_header() -> None:
    body = (
        b"Reporting starts,Campaign ID,Campaign name,Amount spent (USD)\n"
        b"2026-06-23,c_x,Test,100.00\n"
    )
    result = parse_meta_csv(body)
    assert result.currency == "USD"
    assert len(result.records) == 1


def test_utf8_bom_is_tolerated() -> None:
    body = (
        "﻿"
        "Reporting starts,Campaign ID,Campaign name,Amount spent (EUR)\n"
        "2026-06-23,c_y,Bom Test,50.00\n"
    ).encode()
    result = parse_meta_csv(body)
    assert result.currency == "EUR"
    assert len(result.records) == 1


def test_blank_trailing_lines_skipped() -> None:
    body = (
        b"Reporting starts,Campaign ID,Campaign name,Amount spent (GBP)\n"
        b"2026-06-23,c_z,Trailing,100.00\n"
        b"\n"
        b",,,\n"
    )
    result = parse_meta_csv(body)
    assert len(result.records) == 1


def test_missing_required_column_raises_schema_mismatch() -> None:
    body = (
        b"Reporting starts,Campaign name,Amount spent (GBP)\n"  # missing Campaign ID
        b"2026-06-23,Test,100.00\n"
    )
    with pytest.raises(MetaCsvSchemaMismatchError, match="campaign_external_id"):
        parse_meta_csv(body)


def test_missing_currency_suffix_raises_schema_mismatch() -> None:
    body = (
        b"Reporting starts,Campaign ID,Campaign name,Amount spent\n"  # no (CCY) suffix
        b"2026-06-23,c_x,Test,100.00\n"
    )
    with pytest.raises(MetaCsvSchemaMismatchError, match="currency"):
        parse_meta_csv(body)


def test_invalid_date_raises_parse_error() -> None:
    body = (
        b"Reporting starts,Campaign ID,Campaign name,Amount spent (GBP)\n"
        b"not-a-date,c_x,Test,100.00\n"
    )
    with pytest.raises(MetaCsvParseError, match="Line 2.*Invalid date"):
        parse_meta_csv(body)


def test_invalid_spend_raises_parse_error() -> None:
    body = (
        b"Reporting starts,Campaign ID,Campaign name,Amount spent (GBP)\n"
        b"2026-06-23,c_x,Test,not-a-number\n"
    )
    with pytest.raises(MetaCsvParseError, match="Line 2.*Invalid spend"):
        parse_meta_csv(body)


def test_empty_csv_raises_schema_mismatch() -> None:
    with pytest.raises(MetaCsvSchemaMismatchError, match="empty"):
        parse_meta_csv(b"")


def test_header_matching_is_case_insensitive() -> None:
    body = (
        b"REPORTING STARTS,CAMPAIGN ID,Campaign Name,amount spent (GBP)\n"
        b"2026-06-23,c_x,Test,100.00\n"
    )
    result = parse_meta_csv(body)
    assert len(result.records) == 1
    assert result.records[0].campaign_label == "Test"
