---
description: Find every Anthropic SDK call in the codebase and verify it has a §7.17 documented fallback. Defense kit calls must have the templated-fallback path. Run before merging anything that adds LLM calls.
---

Run the LLM degraded-operation audit per SCOPE.md §7.17.

## Part 1 — Enumerate LLM call sites

```bash
rg -n "client\.messages\.create|messages\.create|client\.completions" apps/ modeling/
```

For each match, identify:
- The function it lives in
- The surface it powers (plan parser, drift explanation, defense kit narrative, forecast diff narrative, etc.)
- Whether it goes through `apps/api/llm/client.py` (the wrapped client) or directly hits the SDK

**Any direct SDK call outside `apps/api/llm/` is a violation.** All LLM calls must go through the wrapped client so retry, quota, BYOK resolution, and fallback are consistent.

## Part 2 — Fallback contract verification

For each LLM call site, verify the surface-specific fallback from §7.17:

| Surface | Fallback contract | Where to verify |
|---|---|---|
| Plan parser | 3 retries + UI message "Parser temporarily unavailable" + template path | `apps/api/parser/` |
| Drift explanation | "Explanation pending" placeholder + 30-min retry × 4h + deferred to next batch | `apps/api/jobs/drift_explanations.py` |
| Defense kit narrative | 60s timeout + templated fallback + `narrative_status = templated_fallback` — **never blocks** | `apps/api/defense_kit/` |
| Forecast diff narrative (Phase 3e) | Visual diff still renders without narrative | `apps/api/forecasts/` |
| BYOK 401/403 | Banner + fall back if `llm_byok_fallback_enabled` (else surface error) | `apps/api/llm/client.py` |
| BYOK 429 | Respect retry-after + outage treatment if sustained | `apps/api/llm/client.py` |
| BYOK 402 | Immediate org admin notification + outage treatment | `apps/api/llm/client.py` |
| Quota exhaustion | Overage billing OR hard-stop per org config — **defense kit always exempt from hard-stop** | `apps/api/llm/quota.py` |

## Part 3 — Defense kit critical-path test

Run the explicit fallback test:

```bash
cd apps/api && pytest tests/defense_kit/test_llm_outage.py -v
```

The test simulates a complete Anthropic outage and verifies:
1. Defense kit still generates with all structural elements (header, pacing table, reallocation block, plan-change audit, methodology footnote).
2. Narrative section uses templated fallback ("Top-line summary: [edit this paragraph with your client-facing narrative].").
3. `DefenseKit.narrative_status = templated_fallback`.
4. "Regenerate narrative" button is present in the rendered output.
5. PDF generation completes successfully.

**If this test fails, the product is shipping broken.** Defense kit must never block on LLM.

## Part 4 — BYOK audit

For BYOK code paths:

1. Confirm BYOK keys are never logged. Run:

   ```bash
   rg -n "logger\.(info|debug|warning)" apps/api/llm/ | rg -i "key|token|secret"
   ```

   Should return nothing.

2. Confirm BYOK keys are stored only via `EncryptedSecret`:

   ```bash
   rg -n "byok|llm_api_key" apps/api/ | rg -v "encrypted_secret|EncryptedSecret"
   ```

   Inspect every match. None should persist a raw key.

3. Confirm validation: BYOK keys get a no-op test call on save (`apps/api/llm/byok.py::validate_key`) and re-validation nightly (`apps/api/jobs/byok_validation.py`).

## Output

For each LLM call site:

| Surface | Fallback present? | Tested? | Going through wrapped client? |
|---|---|---|---|

Plus a verdict:

- ✓ All call sites have documented fallbacks. Defense kit test passes. BYOK paths clean.
- ✗ N call sites missing fallbacks / M missing tests / K direct SDK calls outside the wrapper.

Anthropic outages on Monday morning are when this matters most. The product cannot block customer workflow on LLM availability — §7.17 is non-negotiable.
