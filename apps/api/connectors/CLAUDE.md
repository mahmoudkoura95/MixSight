# Connector module conventions

Every connector under `apps/api/connectors/<platform>/` implements the §7.14 Protocol. This directory is where most of the operational fragility of Phase 1c lives — be conservative.

## The Protocol (verbatim from §7.14)

```python
class Connector(Protocol):
    async def authenticate(self, organization_id: UUID) -> ConnectorAuth: ...
    async def list_accessible_accounts(self, auth: ConnectorAuth) -> list[Account]: ...
    async def pull_actuals(
        self,
        auth: ConnectorAuth,
        ad_account_id: str,
        market_id: UUID,
        start_date: date,
        end_date: date,
        pull_type: PullType,
    ) -> list[ActualsRecord]: ...
    async def health_check(self, auth: ConnectorAuth) -> ConnectorHealth: ...
    async def refresh_token(self, auth: ConnectorAuth) -> ConnectorAuth: ...
```

Every method is async. Every method handles its own retries and rate limits. No method raises uncaught — all errors flow through `ConnectorPull.status` and `ConnectorAuthEvent`.

## Credential model (do not deviate)

**Authentication is organization-level.** One `ConnectorAuth` row per `(organization, platform)`. An agency authenticates Meta Business Manager once and that auth grants access to all ad accounts under that BM.

**Ad accounts are mapped per (client, market).** `AdAccountMapping` rows. During client/market setup, the AM picks from the list returned by `list_accessible_accounts`.

**One ad account can map to multiple (client, market) tuples** (rare but allowed).

The same model applies to Google Ads MCC, GA4 properties, TikTok Business Center.

## Pull schedules

Three scheduled types per (client, market, platform):

- **Daily** — trailing 7-day rolling. 6 AM per-market local time. Re-fetch + upsert.
- **Weekly** — trailing 90-day deep. Sunday night. Full attribution variants. Reconciliation factors recomputed.
- **Monthly** — trailing 13-month deep. First of month.

Plus:
- **Backfill** on first `AdAccountMapping` creation: max-available capped at 36 months (24 for TikTok). Paced to respect rate limits.
- **Catch-up** after reauth: missed days from `ConnectorAuth.last_validated_at` through now.
- **Manual** — admin-triggered from connector health surface.

## Idempotency

Every actuals upsert keys on `(client_id, market_id, channel, campaign_external_id, date, source)`. If any of those collide, upsert; otherwise insert. Every pull writes a `ConnectorPull` row capturing the window, rows fetched/upserted/revised, status, error.

## Restatement tracking

When an upsert changes a previously-stored value by more than the configurable threshold (default 5%): increment `ConnectorPull.rows_revised`, write an AuditLog entry on the affected `Actuals` row, surface in the connector health audit log.

## Credential lifecycle (§7.14)

**Proactive refresh.** Background job every 6 hours scans `ConnectorAuth` rows. Tokens within 7 days of expiry get refreshed via refresh tokens. Success → update `token_expires_at` and write `ConnectorAuthEvent`. Failure → set `status = reauth_needed`, write `ConnectorAuthEvent`, notify org admin.

**Reauth-needed state** is distinct from connector-failed:
- `reauth_needed` = token expired or revoked; admin must re-OAuth.
- Connector-failed = transient (rate limit, platform outage). Retry automatically.

When `status = reauth_needed`:
- All pulls under that auth pause.
- Data preserved, pacing goes stale.
- Connector health surface shows red banner; pacing screens show same banner inline.
- AMs can flag the issue. Only admins can perform the reauth.

**Catch-up backfill** runs in background after successful reauth. Visible in connector health.

## Per-platform notes

### Meta
- Marketing API current version. Pull at campaign level.
- Attribution windows: pull all available, store in `Actuals.conversions_alt_attributions` JSONB.
- Long-lived tokens expire ~60 days. Refresh proactively.
- Business verification required before Advanced Access. 1-3 week approval window — file in Phase 1a week 1.

### Google Ads
- GAQL query at campaign level via `googleads-python`.
- Attribution models: pull configured model into `conversions`, store `all_conversions` in `conversions_alt_attributions`.
- OAuth refresh tokens stable but revocable by password change or admin action.
- Developer token application: test access immediate, Basic Access 1-2 weeks. File in Phase 1a week 1.
- MCC = the org-level identity. Map child accounts per (client, market).

### GA4
- Data API. Pull `sessions`, `conversions`, `purchaseRevenue` per `sessionSource`/`sessionMedium`.
- **Quota-budgeted from start.** Standard property quota is 10K tokens/day. Multi-client × multi-market × daily × backfill must fit. Backfill paces over multiple days to avoid daily quota exhaustion.
- OAuth similar to Google Ads.
- Property is the unit mapped per market. Multiple markets can share a property if the client's setup uses single-property-multi-stream.

### TikTok
- Marketing API. Day-level campaign aggregates.
- Access tokens short-lived (~24h). Refresh tokens longer-lived.
- OAuth + business app review: 1-2 weeks. File in Phase 1a week 1.
- Backfill cap 24 months (default; the others default to 36). Confirm against TikTok's current API limits at implementation time.

## What you cannot do here

- **No platform SDK imports outside this directory.** Connector internals must not leak to routes, jobs, or the model layer.
- **No direct `Actuals` writes outside the connector pull path.** CSV ingestion writes through a separate adapter that still respects the unique constraint, with `Actuals.source = "csv_upload"`.
- **No synchronous HTTP.** Every outbound call is async via `httpx.AsyncClient`.
- **No silent rate-limit suppression.** When a platform returns 429: respect retry-after, back off exponentially, log to `ConnectorPull.error_message`. Sustained 429 over a configurable window → mark pull failed and notify.
- **No hard-coded credentials.** Even in tests — use the `EncryptedSecret` fixture pattern.

**See `.claude/skills/connector/` before scaffolding a new platform.**
