"""Platform connectors per §7.14.

Each platform is a submodule. Phase 1a per ADR-003: CSV is the first
implementation of the §7.14 Connector Protocol. API connectors (Meta,
Google Ads, GA4, TikTok) land in Phase 1b/1c as additional implementations
sharing the same `Actuals` table and idempotent upsert key.
"""
