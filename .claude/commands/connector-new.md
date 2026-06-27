---
description: Scaffold a new platform connector implementing the §7.14 Protocol. Wires auth, ad-account mapping, three pull schedules, ConnectorAuthEvent logging, rate-limit handling, and per-platform notes.
argument-hint: <platform> (e.g., "tiktok", "linkedin")
---

Scaffold a new connector for platform: `$ARGUMENTS`.

1. **Load the connector skill** at `.claude/skills/connector/SKILL.md`. Follow it exactly — the §7.14 Protocol is non-negotiable.

2. **Verify scope.** Which phase is this connector? Meta is Phase 1a. GA4 is Phase 1b. Google Ads + TikTok are Phase 1c. LinkedIn + Reddit are Phase 4. **Stop and ask if this isn't authorized for the active phase.**

3. **Verify pre-build dependencies.** Read SCOPE.md §5.1. Does this platform's API approval lifecycle (test access, basic access, business app review) need to be in motion? File the application now if not.

4. **Create the directory structure:**

   ```
   apps/api/connectors/$ARGUMENTS/
   ├── __init__.py
   ├── connector.py          # Implements the Connector Protocol
   ├── auth.py               # OAuth handshake + token refresh
   ├── client.py             # Wrapped HTTP client with rate limit + retry
   ├── models.py             # Platform-specific response types
   ├── parsing.py            # Platform response → ActualsRecord
   ├── rate_limits.py        # Platform-specific limits + backoff
   ├── tests/
   │   ├── test_connector.py
   │   ├── test_auth.py
   │   ├── test_parsing.py
   │   ├── test_rate_limits.py
   │   └── fixtures/         # Recorded API responses
   └── README.md             # Per-platform operational notes
   ```

5. **Implement the Protocol methods.** All async:
   - `authenticate(organization_id)` → starts OAuth flow, persists `ConnectorAuth`, writes `ConnectorAuthEvent` with `event_type=initial_auth`.
   - `list_accessible_accounts(auth)` → returns ad accounts/properties accessible via this auth. Used by `AdAccountMapping` setup UI.
   - `pull_actuals(auth, ad_account_id, market_id, start_date, end_date, pull_type)` → fetches, parses, upserts `Actuals`, writes `ConnectorPull`.
   - `health_check(auth)` → lightweight no-op call. Returns `ConnectorHealth`.
   - `refresh_token(auth)` → refreshes OAuth token, updates `ConnectorAuth.token_expires_at`, writes `ConnectorAuthEvent`.

6. **Wire idempotent upserts.** Every `Actuals` insert is an upsert on `(client_id, market_id, channel, campaign_external_id, date, source)`. Restatement detection: if existing value differs by >5% (or configured threshold), increment `ConnectorPull.rows_revised` and write AuditLog entry on the affected row.

7. **Wire rate-limit handling.** Per-platform module declares the limits (RPM, quota tokens, concurrent connections). Exponential backoff on 429 with retry-after honored. Sustained 429 over a configurable window → mark pull failed, log error, notify.

8. **Wire schedule registration.** Register the three schedules with APScheduler:
   - Daily 6 AM per-market local — trailing `Client.daily_refresh_window_days` (default 7).
   - Weekly Sunday night — trailing 90 days.
   - Monthly first-of-month — trailing 13 months.
   - Backfill on first `AdAccountMapping` creation — max-available, capped per `apps/api/connectors/$ARGUMENTS/rate_limits.py`.
   - Catch-up after reauth — missed window since `ConnectorAuth.last_validated_at`.

9. **Wire credential lifecycle.** Proactive refresh job (every 6h) covers this platform. Reauth-needed state distinct from connector-failed. Reauth flow is admin-only — AMs can flag, not execute.

10. **Add per-platform notes** to `apps/api/connectors/CLAUDE.md` covering: token lifetimes, attribution model handling, quota considerations, known quirks.

11. **Add fixtures.** Recorded API responses for the common cases (campaign-level pull, paginated pull, rate-limit response, auth-expired response). Use these in tests so we don't hit the real API.

12. **Wire to connector health surface.** `apps/api/health/` exposes per-(client, market, platform) status. The new platform should appear automatically once registered with the connector registry.

13. **Run the test suite:**

    ```bash
    cd apps/api && pytest connectors/$ARGUMENTS/tests/ -v
    ```

14. **Update `SHIPPED.md`** when the connector is operationally ready (passes health checks against real account in dev).

Stop and confirm before deploying to any environment.
