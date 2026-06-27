---
name: connector
description: Use this skill whenever scaffolding, implementing, or modifying a platform connector (Meta, Google Ads, GA4, TikTok, or future LinkedIn/Reddit) in the MixSight project. Triggers include "new connector," "platform integration," "OAuth," "pull actuals," "ConnectorAuth," "AdAccountMapping," "reauth," "rate limit," "backfill." Encodes the SCOPE.md §7.14 Connector Protocol, the organization-level OAuth + per-(client, market) ad account mapping credential model, the three pull schedules (daily 7d / weekly 90d / monthly 13mo), idempotent upserts, ConnectorAuthEvent logging, and the credential lifecycle. Use this skill BEFORE adding any new platform — the contract is non-negotiable.
---

# Connector skill

Every platform connector implements the same Protocol. The credential model is organization-level OAuth + per-(client, market) ad account mapping — fixed in v3.3 of the scope. The pull schedules are non-negotiable: daily 7d trailing + weekly 90d deep + monthly 13mo deep.

## The Protocol (verbatim from §7.14)

```python
from typing import Protocol
from uuid import UUID
from datetime import date


class Connector(Protocol):
    async def authenticate(self, organization_id: UUID) -> ConnectorAuth:
        """Start OAuth flow, persist credentials, write ConnectorAuthEvent."""

    async def list_accessible_accounts(self, auth: ConnectorAuth) -> list[Account]:
        """Return ad accounts/properties accessible via this auth."""

    async def pull_actuals(
        self,
        auth: ConnectorAuth,
        ad_account_id: str,
        market_id: UUID,
        start_date: date,
        end_date: date,
        pull_type: PullType,
    ) -> list[ActualsRecord]:
        """Fetch, parse, upsert. Write ConnectorPull."""

    async def health_check(self, auth: ConnectorAuth) -> ConnectorHealth:
        """Lightweight no-op call to verify auth still works."""

    async def refresh_token(self, auth: ConnectorAuth) -> ConnectorAuth:
        """Refresh OAuth token. Update token_expires_at. Write ConnectorAuthEvent."""
```

Every method is async. Every method handles its own retries and rate limits. No method raises uncaught — errors flow through `ConnectorPull.status` and `ConnectorAuthEvent`.

## Credential model — locked

**Authentication is organization-level.** One `ConnectorAuth` per `(organization, platform)`. Agency authenticates once.

**Ad accounts are mapped per (client, market).** `AdAccountMapping` rows. AM picks from `list_accessible_accounts` during client/market setup.

**Practical implication.** Onboarding time decreases substantially after first client. New client setup is just "create client, map ad accounts." OAuth dance is once per agency per platform.

```python
@router.post("/organizations/{organization_id}/connectors/{platform}/auth")
async def start_auth(
    organization_id: UUID,
    platform: Platform,
    _: None = Depends(enforce_organization_access),
    __: None = Depends(require_role("admin")),
    connector: Connector = Depends(get_connector_for_platform),
) -> AuthRedirect:
    return await connector.authenticate(organization_id)
```

## Pull schedules

Three scheduled types per (client, market, platform):

```python
# apps/api/jobs/connectors.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def register_pull_schedules(scheduler: AsyncIOScheduler, mapping: AdAccountMapping):
    market = mapping.market
    tz = market.local_timezone  # IANA name

    # Daily — trailing N-day rolling re-fetch at 6 AM market-local
    scheduler.add_job(
        run_daily_pull,
        "cron",
        hour=6,
        timezone=tz,
        args=[mapping.id],
        id=f"daily_{mapping.id}",
    )

    # Weekly — trailing 90-day deep, Sunday night
    scheduler.add_job(
        run_weekly_pull,
        "cron",
        day_of_week="sun",
        hour=23,
        timezone=tz,
        args=[mapping.id],
        id=f"weekly_{mapping.id}",
    )

    # Monthly — trailing 13-month deep, 1st of month
    scheduler.add_job(
        run_monthly_pull,
        "cron",
        day=1,
        hour=2,
        timezone=tz,
        args=[mapping.id],
        id=f"monthly_{mapping.id}",
    )
```

Trailing window for daily is `Client.daily_refresh_window_days` (default 7, range 3-14).

## Backfill on first authentication

When an `AdAccountMapping` is first created, MixSight triggers a backfill targeting maximum-available, capped per platform:

- Meta: 36 months
- Google Ads: 36 months (capped from 4+ year API max for cost control)
- GA4: since property creation, capped at 36 months
- TikTok: 24 months

Backfill is **paced** to respect rate limits. Especially for GA4 — the daily token quota (10K) cannot be exhausted by historical pulls; the backfill spreads across days.

```python
async def schedule_backfill(mapping: AdAccountMapping, connector: Connector):
    cap_months = PLATFORM_BACKFILL_CAPS[mapping.platform]
    chunks = compute_paced_chunks(cap_months, mapping.platform)
    # Spread chunks across days so daily quota isn't exhausted
    for chunk in chunks:
        scheduler.add_job(
            run_backfill_chunk,
            "date",
            run_date=chunk.scheduled_for,
            args=[mapping.id, chunk.start_date, chunk.end_date],
        )
```

## Idempotency

Every `Actuals` upsert keys on `(client_id, market_id, channel, campaign_external_id, date, source)`. The §7.14 idempotency constraint:

```python
from sqlalchemy.dialects.postgresql import insert

stmt = insert(Actuals).values(records)
stmt = stmt.on_conflict_do_update(
    constraint="actuals_unique_pull",
    set_={
        "spend_local": stmt.excluded.spend_local,
        "spend_reporting": stmt.excluded.spend_reporting,
        "impressions": stmt.excluded.impressions,
        "clicks": stmt.excluded.clicks,
        "conversions": stmt.excluded.conversions,
        "conversions_value": stmt.excluded.conversions_value,
        "conversions_alt_attributions": stmt.excluded.conversions_alt_attributions,
        "labels": stmt.excluded.labels,
        "pull_timestamp": stmt.excluded.pull_timestamp,
        "pull_window_start": stmt.excluded.pull_window_start,
        "pull_window_end": stmt.excluded.pull_window_end,
        "fx_rate_used": stmt.excluded.fx_rate_used,
    },
)
```

Every pull writes a `ConnectorPull` row capturing: window, rows fetched / upserted / revised, status, error message, attempted_at, completed_at.

## Restatement tracking

When an upsert changes a previously-stored value by more than the threshold (default 5%, configurable):
- Increment `ConnectorPull.rows_revised`.
- Write an `AuditLog` entry on the affected `Actuals` row.
- Surface in the connector health audit log.
- Compute reconciliation factor delta if applicable (`ReconciliationFactor` rows updated).

## Credential lifecycle

**Proactive refresh.** Background job every 6 hours scans `ConnectorAuth` rows. Tokens within 7 days of expiry get refreshed via `connector.refresh_token`. Success → update `token_expires_at`, write `ConnectorAuthEvent(event_type="refresh", success=True)`. Failure → set `status = reauth_needed`, write `ConnectorAuthEvent(event_type="refresh", success=False, error_code=...)`.

**Reauth-needed state** is distinct from connector-failed:
- `reauth_needed`: token expired or revoked. Admin must re-OAuth.
- Connector-failed: transient (rate limit, platform outage). Retry automatically.

When `status = reauth_needed`:
- All pulls under that auth pause.
- Data preserved; pacing goes stale.
- Connector health surface shows red banner: "Reauth needed — {platform}. Last good data: {date}."
- Inline banner on pacing screens.
- AMs can flag the issue. **Only admins can perform the reauth.**
- Org admins notified per their notification preferences (immediate / daily digest / weekly digest).

**Reauth flow:**
1. Admin clicks "Reauth Meta" in `/settings/connectors` or the connector health surface.
2. OAuth handshake.
3. On success: new tokens stored, status set to `active`, paused pulls resume.
4. Catch-up backfill of missed days runs in background; visible in connector health.
5. `ConnectorAuthEvent(event_type="reauth", success=True)`.

**Edge cases:**
- Original AM who authed has left the agency → any user with `admin` role can reauth.
- Partial revocation (some ad accounts under one connection revoked) → detected and surfaced per-ad-account.
- Platform-level access entirely revoked (e.g., Meta business verification revoked) → distinct error, surfaced as "platform-level access revoked" with link to platform help docs. Reauth alone won't fix this.

## Rate-limit handling

Per-platform module in `apps/api/connectors/<platform>/rate_limits.py` declares:
- Requests per minute / hour / day
- Concurrent connection limits
- Backoff strategy (exponential with jitter)
- Retry-after header handling

429 responses: respect `Retry-After` header, back off exponentially. Sustained 429s (>30 min): mark pull failed, notify.

## CSV ingestion (Phase 1c, shallow)

AM uploads CSV of actuals for periods predating API window or to fill gaps. Stored with `Actuals.source = "csv_upload"`. Phase 2 extends to deep CSV (offline conversions, in-store sales, CRM).

CSV path still respects the §7.14 unique constraint. Use:

```python
async def ingest_csv_actuals(file, client_id, market_id):
    records = parse_csv(file)
    for record in records:
        record.source = "csv_upload"
    await upsert_actuals(records)
```

## Per-platform quick-reference

### Meta
- Marketing API current version. Campaign-level pulls.
- Long-lived tokens expire ~60 days.
- Attribution: store all variants in `conversions_alt_attributions` JSONB.
- Business verification required for Advanced Access. File Phase 1a week 1.

### Google Ads
- GAQL via `googleads-python`. Campaign-level.
- Attribution: configured model → `conversions`, all_conversions → `conversions_alt_attributions`.
- OAuth refresh tokens stable but revocable.
- Developer token: test access immediate; Basic Access 1-2 weeks. File Phase 1a week 1.
- MCC = the org-level identity.

### GA4
- Data API. `sessions`, `conversions`, `purchaseRevenue` per `sessionSource`/`sessionMedium`.
- **Quota-budgeted from start.** 10K tokens/day per standard property.
- Backfill paces over multiple days.

### TikTok
- Marketing API. Day-level campaign aggregates.
- Access tokens ~24h; refresh tokens longer.
- App review: 1-2 weeks. File Phase 1a week 1.
- Backfill cap 24 months.

## Workflow when scaffolding a new platform

1. Verify scope (which phase? Meta = 1a, GA4 = 1b, Google + TikTok = 1c, LinkedIn = Phase 4).
2. File platform API approval — these have lead times.
3. Create the directory structure under `apps/api/connectors/<platform>/`.
4. Implement the Protocol methods.
5. Implement rate limits + backoff in `rate_limits.py`.
6. Wire schedules in `apps/api/jobs/connectors.py`.
7. Wire the proactive refresh job to include the new platform.
8. Add per-platform notes to `apps/api/connectors/CLAUDE.md`.
9. Add fixtures (recorded API responses) for tests.
10. Write tests covering auth, pull (happy + paginated + 429 + auth-expired), refresh, health check.
11. Wire to connector health surface (registry-driven; no manual addition usually).

## What you cannot do

- No platform SDK imports outside the connector directory.
- No direct `Actuals` writes outside the connector pull path or CSV adapter.
- No synchronous HTTP. Use `httpx.AsyncClient`.
- No silent rate-limit suppression. Respect retry-after, log to ConnectorPull.
- No hard-coded credentials in tests. Use `EncryptedSecret` fixture.
- No skipping the proactive refresh registration for a new platform.
- No skipping `ConnectorAuthEvent` writes on any credential lifecycle event.
