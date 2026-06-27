---
name: llm-call
description: Use this skill whenever invoking the Anthropic API in the MixSight project. Triggers include "Anthropic," "Claude," "client.messages.create," "LLM," "Sonnet," "Opus," "plan parser," "drift explanation," "defense kit narrative," "BYOK," "API key," "fallback," "quota." Encodes the SCOPE.md §7.17 degraded-operation contract: every LLM-dependent surface has an explicit fallback because Anthropic outages happen on Mondays. The defense kit NEVER blocks on LLM. All calls route through the wrapped client at apps/api/llm/client.py — never call the SDK directly. Use this skill BEFORE writing any code that touches messages.create.
---

# LLM call skill

Anthropic outages, rate limits, and BYOK key issues will happen. Monday morning is when an outage hurts most. Every LLM-dependent surface has an explicit fallback. The defense kit is on the critical path and **never blocks on LLM** — this is non-negotiable.

## The wrapped client

All LLM calls go through `apps/api/llm/client.py`. Never call `anthropic.Anthropic()` directly outside this module.

```python
# apps/api/llm/client.py
from anthropic import AsyncAnthropic, APIError, RateLimitError, AuthenticationError


class WrappedLLMClient:
    """Single entry point for all LLM calls. Handles:
    - BYOK key resolution from EncryptedSecret
    - Quota counting (skipped for BYOK)
    - Retry + timeout per surface
    - Surface-specific fallback
    """

    async def call(
        self,
        *,
        workspace_id: UUID,
        surface: Literal["parser", "drift_explanation", "defense_kit", "forecast_diff"],
        prompt: PromptInput,
        model: Literal["sonnet", "opus"] = "sonnet",
        timeout_s: float | None = None,
    ) -> LLMResponse:
        ...
```

`PromptInput` carries the prompt + the schema for structured output. `LLMResponse` carries the result plus a status: `generated` / `templated_fallback` / `failed`.

## Three workspace modes

Per §7.17:

1. **Default — MixSight key, in quota.** Counted against monthly quota. Cached generations don't count.
2. **Default — MixSight key, overage.** Continues at $0.40/generation. Per-org config can hard-stop instead.
3. **BYOK — Customer key.** All calls use customer's key. No quota counting on our side. $200/workspace/month credit applied to billing.

```python
async def resolve_key(workspace_id: UUID) -> tuple[str, KeyMode]:
    workspace = await load_workspace(workspace_id)
    if workspace.byok_key_ref:
        key = await decrypt_secret(workspace.byok_key_ref)
        return key, KeyMode.BYOK
    if await is_in_quota(workspace_id):
        return MIXSIGHT_KEY, KeyMode.DEFAULT_IN_QUOTA
    if workspace.organization.overage_hard_stop:
        raise QuotaExceeded()  # Surface handler decides fallback
    return MIXSIGHT_KEY, KeyMode.DEFAULT_OVERAGE
```

## Surface-specific fallbacks (non-negotiable)

### Plan parser (§7.6, §7.17)

- 3 retries with exponential backoff.
- After exhaustion: UI shows "Parser temporarily unavailable — try again or upload using a template."
- Source artifact preserved at `source_artifact_uri`. Parsing can be retried from upload history.
- AM falls back to template path immediately. **No data loss.**
- Confidence pipeline: Sonnet first; low-confidence rows re-run with Opus.

```python
async def parse_plan(workspace_id, source_artifact_uri):
    for attempt in range(3):
        try:
            return await llm.call(
                workspace_id=workspace_id,
                surface="parser",
                prompt=parser_prompt(source_artifact_uri),
                model="sonnet",
                timeout_s=120,
            )
        except (APIError, RateLimitError) as e:
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
                continue
            return LLMResponse(status="failed", error=e, fallback_action="template_path")
```

### Drift explanation (§7.8, §7.17)

- Batch job on Monday morning. Failed rows get "Explanation pending" placeholder rather than empty.
- Background retry every 30 minutes for 4 hours.
- After exhaustion: deferred until next batch run.
- On-demand regeneration: same retry policy with manual retry button visible.
- Cached explanations from prior weeks remain visible and clearly dated.

```python
async def generate_drift_explanation(snapshot_line_id):
    try:
        return await llm.call(
            workspace_id=...,
            surface="drift_explanation",
            prompt=drift_prompt(snapshot_line_id),
            model="sonnet",
            timeout_s=60,
        )
    except (APIError, RateLimitError) as e:
        await schedule_retry(snapshot_line_id, delay_min=30, max_attempts=8)
        return PlaceholderExplanation("Explanation pending")
```

### Defense kit narrative — the critical path (§7.13, §7.17)

- 60s timeout.
- If LLM call fails or times out:
  - Defense kit **still generates** with all structural elements (header, pacing table, reallocation block, plan-change audit, methodology footnote).
  - Narrative replaced with templated fallback: "Top-line summary: [edit this paragraph with your client-facing narrative]."
  - "Regenerate narrative" button visible to retry when service returns.
  - `DefenseKit.narrative_status = templated_fallback` for audit visibility.
- The AM walks into the meeting with the structural defense kit. The LLM polish is an enhancement, not a dependency.

```python
async def generate_defense_kit_narrative(defense_kit_id):
    try:
        async with asyncio.timeout(60):
            response = await llm.call(
                workspace_id=...,
                surface="defense_kit",
                prompt=narrative_prompt(defense_kit_id),
                model="sonnet",
            )
        await update_defense_kit_narrative(defense_kit_id, response.text, status="generated")
    except (APIError, RateLimitError, asyncio.TimeoutError):
        await update_defense_kit_narrative(
            defense_kit_id,
            "Top-line summary: [edit this paragraph with your client-facing narrative].",
            status="templated_fallback",
        )
```

**THE DEFENSE KIT MUST GENERATE.** If you find code that can fail the defense kit generation because of an LLM problem, fix it. This is non-negotiable.

### Forecast diff narrative (Phase 3e)

- LLM narrative is optional. Phase 3c ships visual diff only.
- When LLM narrative is enabled (3e): timeout, retry, fallback to "Narrative unavailable" placeholder. Visual diff still renders.

## BYOK failure modes

- **401/403 (key invalid).** Treat as auth failure. Banner: "BYOK key invalid — update in /settings/llm." If `Client.llm_byok_fallback_enabled = true`, fall back to MixSight key with quota counting and overage billing. Default: `false` (strict BYOK).
- **429 (rate limited).** Respect retry-after header, wait, retry. Sustained 429s (>30 min): treat as outage with same fallback option.
- **402 (insufficient credit on customer's Anthropic account).** Notify org admin immediately. Treat as outage. Fall back if `llm_byok_fallback_enabled = true`.

```python
async def handle_byok_error(error, workspace_id, surface):
    if error.status_code in (401, 403):
        await notify_admin_invalid_byok(workspace_id)
        if await fallback_enabled(workspace_id):
            return await call_with_mixsight_key(workspace_id, surface)
        raise BYOKKeyInvalid()
    if error.status_code == 429:
        # retry-after honored at the SDK call site
        ...
    if error.status_code == 402:
        await notify_admin_byok_insufficient_credit(workspace_id)
        if await fallback_enabled(workspace_id):
            return await call_with_mixsight_key(workspace_id, surface)
        raise BYOKInsufficientCredit()
```

## Quota exhaustion

At quota: continue with overage billing OR hard-stop based on org-level config. **Hard-stop never applies to defense kit narrative** — defense kit is structural artifact, must always generate. If hard-stop enabled and quota exhausted, defense kit narrative falls back to templated.

## Caching

Drift explanations are cached by content hash. Regenerate only on data change. Cache miss → generate; cache hit → free. Cached generations don't count against quota.

```python
async def maybe_cached_drift_explanation(snapshot_line):
    hash_key = sha256(json.dumps(snapshot_line.relevant_inputs())).hexdigest()
    cached = await cache.get(f"drift_explanation:{hash_key}")
    if cached:
        return cached
    explanation = await generate_drift_explanation(snapshot_line.id)
    await cache.set(f"drift_explanation:{hash_key}", explanation, ttl=timedelta(days=14))
    return explanation
```

## Cost dashboard

Per §7.17, per-feature cost dashboard for workspace admins regardless of mode. Counts:
- Generations by surface.
- Cached vs fresh.
- BYOK vs MixSight-paid.
- Cumulative monthly cost.

## What you cannot do

- **No direct SDK call outside `apps/api/llm/`.** Use the wrapped client.
- **No LLM call without a documented fallback for the surface.**
- **No `client.messages.create` on the defense kit critical path that can block.**
- **No logging of API keys, BYOK keys, OAuth tokens, or token volume.** Customer's BYOK key is sacred — we never see token counts.
- **No BYOK key persisted outside `EncryptedSecret`.**
- **No model upgrade without a retry safety net.** Switching from Sonnet to Opus or to a newer model is a versioned migration with a rollback path.
- **No prompts inline in route handlers.** Prompts live in `apps/api/llm/prompts/` with version numbers. This is for diff-ability and for the calibration loop later.

## Workflow when adding a new LLM-dependent surface

1. Identify the surface and read its §7.17 fallback contract (or define one if it's new).
2. Add the prompt to `apps/api/llm/prompts/<surface>/vN.py`.
3. Wrap the call in `WrappedLLMClient.call` with the right `surface` string.
4. Handle the failure case explicitly — set the right status, surface the right UI affordance.
5. Test the failure path. Use `pytest tests/llm/test_outage.py::<surface>` to simulate.
6. If on critical path (defense kit), verify structural generation completes regardless.
7. Add the surface to `/llm-degraded-audit` slash command's audit table.
