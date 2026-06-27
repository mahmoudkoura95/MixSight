# Backend conventions (apps/api)

FastAPI, Python 3.11+, sqlmodel (SQLAlchemy 2.0), Pydantic v2 per §6.1. **Async throughout.**

**Default to less.** The root `CLAUDE.md` "do the minimum" principle applies here especially. The backend has lots of room for speculative complexity (custom retry decorators, request-context objects, dependency-injection wrappers, etc.). Don't add layers the scope doesn't call for. The skill patterns are starting points — use the simplest form that satisfies the scope section, not the most elaborate.

## Conventions

- **Async everywhere.** No sync `def` on route handlers, no sync DB calls. `AsyncSession` from sqlmodel. `httpx.AsyncClient` for outbound HTTP.
- **Pydantic v2 only.** No v1 syntax. Use `model_config` not `class Config`.
- **Type hints on every function signature.** `mypy --strict` should pass.
- **No raw SQL outside Alembic migrations** unless explicitly needed for performance. Document the reason in a comment.
- **No `print`. No `logger.info` of user data.** Use structured logging with `request_id` correlation. Never log Anthropic API keys, OAuth tokens, or BYOK keys — even via debug.

## Tenancy enforcement (§7.19) — non-negotiable

Every endpoint that takes a `client_id` parameter (path, query, or body) **must** depend on `enforce_client_access`:

```python
@router.get("/clients/{client_id}/snapshots/{snapshot_id}")
async def get_snapshot(
    client_id: UUID,
    snapshot_id: UUID,
    _: None = Depends(enforce_client_access),  # required
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    ...
```

Endpoints that take `organization_id` use `enforce_organization_access`.

The app-startup decorator audit (`apps/api/tenancy/audit.py`) fails app boot if any route is missing the right dependency. The `@pytest.mark.tenancy_isolated` marker on integration tests fails the suite if a cross-tenant case is missing.

**See `.claude/skills/tenancy/` before adding any new route.**

## Audit logging (§7.4) — non-negotiable

Every mutation writes to `AuditLog` via the SQLAlchemy event hook in `apps/api/audit/hooks.py`. The hook is registered at app startup and is not optional. If you find yourself bypassing it for a specific mutation, that's a code smell — fix the underlying model, don't disable the hook.

Audit log fields: `entity_type`, `entity_id`, `action` (created/updated/deleted/restored), `before` (JSONB, nullable on create), `after` (JSONB, nullable on delete), `actor_user_id`, `request_id`, `metadata`. 7-year retention with anonymization at customer deletion per §6.6.

**See `.claude/skills/audit-log/` for the hook pattern.**

## LLM calls (§7.17) — every call has a fallback

Three modes per workspace: default-in-quota, default-overage, BYOK. All three resolved via `apps/api/llm/client.py` which:

1. Resolves the right key (workspace BYOK key from `EncryptedSecret`, or MixSight default).
2. Counts the call against quota if applicable.
3. Wraps the call with retry + timeout per surface.
4. Falls back per surface-specific contract.

**Surface-specific fallback contracts (do not skip):**

- **Plan parser failure** (§7.17): 3 retries with exponential backoff. After exhaustion: UI shows "Parser temporarily unavailable — try again or upload using a template." Source artifact preserved.
- **Drift explanation failure**: row gets "Explanation pending" placeholder. Background retry every 30 min for 4 hours. Then deferred until next batch.
- **Defense kit narrative failure**: 60s timeout. If failed: structural defense kit still generates with **templated narrative**. `DefenseKit.narrative_status = templated_fallback`. **Defense kit never blocks on LLM.** This is non-negotiable.

**BYOK-specific:**
- 401/403: banner in workspace, fall back if `Client.llm_byok_fallback_enabled = true`.
- 429: respect retry-after header. Sustained >30 min: treat as outage.
- 402: notify org admin immediately.

**See `.claude/skills/llm-call/` before any `client.messages.create` call.**

## Connectors (§7.14)

Every connector under `apps/api/connectors/<platform>/` implements the `Connector` Protocol. Credentials are org-level (`ConnectorAuth`); ad accounts are mapped per (client, market) (`AdAccountMapping`).

Three pull schedules, per-market timezone:
- Daily 6 AM local — trailing 7-day rolling re-fetch.
- Weekly Sunday night — trailing 90-day deep.
- Monthly first-of-month — trailing 13-month deep.

Every pull is an idempotent upsert on `(client_id, market_id, channel, campaign_external_id, date, source)`. Every pull writes a `ConnectorPull` row. Every credential lifecycle event writes a `ConnectorAuthEvent` row.

**See `.claude/skills/connector/` and `apps/api/connectors/CLAUDE.md`.**

## Database conventions (§6.2)

- UUIDs via `gen_random_uuid()`.
- Money: `numeric(18, 4)`. **Never `float`.**
- Percentages: `numeric(8, 4)`.
- FX: `numeric(20, 10)`.
- Timestamps: `timestamptz`. Stored UTC, converted at edges.
- JSONB columns: `jsonb`, never `json`. GIN indexes for filtered fields.
- Soft delete: `deleted_at timestamptz` nullable + partial index `WHERE deleted_at IS NULL`.
- Every FK gets an index. Every `(client_id, ...)` query pattern gets a composite index.
- Constraint names: `{table}_{column}_{type}` (e.g., `actuals_unique_pull`).

**See `.claude/skills/migration/` before creating any migration.**

## API surface conventions

- RESTful routes grouped by resource: `/clients`, `/clients/{client_id}/markets`, etc.
- Pagination: cursor-based via `?cursor=...&limit=...`. Default limit 50, max 200.
- Errors: structured JSON. `{"error": {"code": "TENANCY_DENIED", "message": "...", "request_id": "..."}}`.
- OpenAPI schema regenerated on every change. Frontend types regenerated via `scripts/codegen.sh`.
- Background jobs: APScheduler in V1 local; Celery + Redis on deploy. Always wrap job bodies with the same tenancy + audit + LLM patterns as routes.

## Secrets and BYOK

- All credentials (OAuth tokens, BYOK keys) stored as `EncryptedSecret` rows. Never inline columns. Fernet with `key_version` for rotation.
- Master key from environment (`MIXSIGHT_FERNET_KEY`). Never logged. Never returned in API responses.
- BYOK keys: validated via no-op test call at write time. Re-validated nightly. Status surfaced in `/settings/llm`.

## What this directory should NOT contain

- Hand-written API schema. Use Pydantic models; OpenAPI generates from them.
- LLM prompt strings inline in route handlers. Put them in `apps/api/llm/prompts/` with versioning.
- Connector platform-specific imports outside `connectors/<platform>/`.
- Test fixtures in production code paths.
