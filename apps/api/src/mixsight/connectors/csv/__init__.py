"""CSV-based actuals ingestion.

Per ADR-003: the first implementation of §7.14 Connector Protocol is a CSV
parser, not an API client. Native Meta Ads Manager exports first (Week 3
single-channel scope); normalized template + Google Ads + GA4 land in
Week 4 / Phase 1b as ADR-003 mandated mapping fills in.
"""
