---
name: defense-kit
description: Use this skill whenever building, modifying, or testing the defense kit feature in the MixSight project. Triggers include "defense kit," "Monday morning artifact," "client-facing PDF," "narrative generation," "render mode," "templated fallback," "Playwright PDF," "per-market rendering," "rolled-up rendering." Encodes the SCOPE.md §7.13 contract: HTML server-rendered + PDF via Playwright, two render modes, structural elements always generate regardless of LLM availability, templated narrative on outage, narrative_status field for audit visibility. Defense kit is the single most-tested fallback path because Anthropic outages on Monday morning are when this matters most. Use this skill BEFORE touching defense-kit code.
---

# Defense kit skill

The defense kit is MixSight's Monday-morning client-facing deliverable. It's the most user-visible LLM-touched surface and **the most critical path for §7.17 degraded operation**. When Anthropic has an outage on a Monday morning, the defense kit must still generate, or MixSight is unusable that morning. Non-negotiable.

## What the defense kit is (§7.13)

An HTML page + a PDF rendered via Playwright. Per `Client.defense_kit_template` setting, rendered in one of two modes:

- **`per_market`** — separate kit per market (US, UK, DE generates three kits).
- **`rolled_up`** — single multi-market kit (one PDF covering all markets).

## Required sections

Every defense kit contains:

1. **Header** — agency logo (white-label Layer 1 applied), client name, week-of date, render mode.
2. **Top-line summary** — LLM-generated narrative paragraph (or templated fallback). Editable rich-text.
3. **Pacing table** — by market and channel, grouped per `render_mode`.
4. **Top 3 drift callouts** — auto-picked highest-impact drift rows.
5. **Selected reallocation block** — the suggestion the AM has implemented (if any), with rationale + projected delta. If multiple suggestions implemented, all shown.
6. **Plan-change audit** — what plan changes happened this week, who authorized them.
7. **Methodology footnote** — explanation of dual-mode evidence (Mode A + Mode B), data freshness, attribution disclosure.
8. **Next-week outlook** — LLM-generated short paragraph (or templated fallback). Editable.

## The data model

```python
class DefenseKit(SQLModel, table=True):
    id: UUID
    snapshot_id: UUID  # FK to PacingSnapshot
    render_mode: Literal["per_market", "rolled_up"]
    narrative_status: Literal["generated", "templated_fallback", "failed", "regenerating"]
    narrative_text: str  # LLM-generated or templated
    outlook_text: str  # LLM-generated or templated
    html_uri: str  # S3 or local path
    pdf_uri: str
    generated_at: datetime
    generated_by_user_id: UUID | None  # null if scheduled batch
    ...
```

`narrative_status` is **always set**. It's the audit signal for whether the AM should review the narrative more carefully.

## Generation flow

```python
async def generate_defense_kit(snapshot_id: UUID, render_mode: str) -> DefenseKit:
    # 1. Build structural data
    snapshot = await load_snapshot_with_lines(snapshot_id)
    drift_callouts = pick_top_drift(snapshot, n=3)
    implemented_suggestions = await load_implemented_suggestions(snapshot)
    plan_changes = await load_plan_changes(snapshot.client_id, snapshot.week_of)

    # 2. Attempt LLM narrative — but never block on it
    narrative_text, narrative_status = await maybe_generate_narrative(snapshot, drift_callouts)
    outlook_text, outlook_status = await maybe_generate_outlook(snapshot)

    # 3. Render HTML — purely structural, deterministic
    html = await render_html(
        snapshot=snapshot,
        drift_callouts=drift_callouts,
        suggestions=implemented_suggestions,
        plan_changes=plan_changes,
        narrative_text=narrative_text,
        outlook_text=outlook_text,
        render_mode=render_mode,
        branding=snapshot.client.organization.branding_config,
    )

    # 4. Render PDF via Playwright
    pdf_bytes = await playwright_pdf(html)

    # 5. Persist
    kit = DefenseKit(
        snapshot_id=snapshot_id,
        render_mode=render_mode,
        narrative_status=narrative_status,
        narrative_text=narrative_text,
        outlook_text=outlook_text,
        html_uri=await store(html),
        pdf_uri=await store(pdf_bytes),
        generated_at=datetime.now(timezone.utc),
    )
    db.add(kit)
    await db.commit()
    return kit
```

## The templated fallback (the non-negotiable part)

```python
TEMPLATED_NARRATIVE = (
    "Top-line summary: [edit this paragraph with your client-facing narrative]. "
    "Pacing and drift detail below. Reallocation suggestions are listed where applicable."
)

TEMPLATED_OUTLOOK = (
    "Next-week outlook: [edit with the action items for the coming week]."
)


async def maybe_generate_narrative(snapshot, drift_callouts) -> tuple[str, str]:
    try:
        async with asyncio.timeout(60):
            response = await llm.call(
                workspace_id=snapshot.client.organization_id,
                surface="defense_kit",
                prompt=narrative_prompt(snapshot, drift_callouts),
                model="sonnet",
            )
        return response.text, "generated"
    except (APIError, RateLimitError, asyncio.TimeoutError, QuotaExceeded):
        return TEMPLATED_NARRATIVE, "templated_fallback"
    except Exception:
        return TEMPLATED_NARRATIVE, "failed"  # Don't let any error block kit generation
```

`maybe_generate_outlook` is identical with `TEMPLATED_OUTLOOK`.

**The catch-all exception is intentional.** The defense kit must generate. Any LLM-side failure flows to templated fallback. The structural elements are deterministic and cannot fail (if they do, you have a deeper bug to fix — they shouldn't depend on anything that can be down).

## Quota exhaustion exemption

Per §7.17, hard-stop quota mode never applies to defense kit narrative. If the org is at quota with hard-stop:

```python
async def call_for_defense_kit(workspace_id, prompt):
    try:
        return await llm.call(workspace_id=workspace_id, surface="defense_kit", prompt=prompt)
    except QuotaExceededHardStop:
        # Defense kit exempt — narrative falls back to templated, but kit still generates
        raise  # Caught by maybe_generate_narrative, becomes templated
```

The defense kit is a structural artifact. It must always generate. Templated narrative is acceptable; missing defense kit is not.

## Rendering

HTML is generated server-side in Python (Jinja2 or similar). The PDF is generated by Playwright headless Chromium loading the HTML.

```python
async def playwright_pdf(html: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        pdf = await page.pdf(
            format="A4",
            margin={"top": "20mm", "right": "15mm", "bottom": "20mm", "left": "15mm"},
            print_background=True,
        )
        await browser.close()
        return pdf
```

PDFs are byte-identical to the HTML visually. CSS uses print-aware rules (page breaks, font sizing).

## White-label application

Per §6.4:
- **Layer 1 (Growth+)** — logo + colors + PDF branding. Read from `Organization.branding_config`. Applied at render time.
- **Layer 2 (Agency)** — branded email-from on defense kit delivery emails.
- **Layer 3 (Enterprise, Phase 4)** — fully custom templates, sub-processor branding.

For Layer 1, the renderer reads:
- `branding_config.logo_url`
- `branding_config.primary_color`
- `branding_config.accent_color`
- `branding_config.font_family` (limited safe set)
- `branding_config.show_powered_by_mixsight` (Agency tier and above can toggle off)

## The frontend preview

`/clients/{client_id}/snapshots/{snapshot_id}/defense-kit` shows an interactive preview that visually matches the PDF. Editable surfaces:
- Narrative paragraph (rich-text editor)
- Outlook paragraph (rich-text editor)
- Comments per pacing row, drift callout, suggestion

Structural surfaces (read-only structure):
- Pacing table grid (cells are commentable but not editable)
- Drift callout selection (the top-3 algorithm picks; AM can swap via "Edit selected callouts")
- Plan-change audit (read-only — those changes already happened)
- Methodology footnote (template; AM can override per-org under Settings)

## Regeneration

AM clicks "Regenerate" → re-runs `maybe_generate_narrative` and `maybe_generate_outlook`. If both succeed, status is updated; if one or both fall back, status reflects.

Regeneration during outage: same fallback applies. The button remains visible so the AM can retry later when Anthropic comes back.

## Status indicators in UI

| `narrative_status` | UI indicator |
|---|---|
| `generated` | ✓ green checkmark, "AI-generated narrative" |
| `templated_fallback` | ⚠ amber warning, "Templated narrative — edit before sending" |
| `failed` | ✗ red, "Narrative generation failed — edit manually or retry" |
| `regenerating` | ⏳ spinner, "Regenerating..." |

The AM sees status at a glance and knows whether to invest editing time.

## Testing

**Critical-path tests:**
1. Happy-path generation (`tests/defense_kit/test_happy_path.py`) — verifies all sections render, narrative is LLM-generated, status is `generated`.
2. LLM outage simulation (`tests/defense_kit/test_llm_outage.py`) — simulates Anthropic 500/503/timeout, verifies kit still generates with `templated_fallback` status.
3. BYOK invalid key (`tests/defense_kit/test_byok_invalid.py`) — verifies kit still generates with templated fallback, banner shows in UI.
4. Quota exhaustion with hard-stop (`tests/defense_kit/test_quota_hardstop.py`) — verifies defense kit still generates regardless.
5. Visual regression (`tests/defense_kit/test_visual_regression.py`) — compares rendered PDF against golden file. Updates require explicit commit message.

**If any of these tests fail, do not merge.** The defense kit is the product's user-trust anchor.

## Workflow when modifying defense-kit code

1. Read §7.13 in full.
2. If touching narrative generation: verify the fallback path stays intact. Run the outage test.
3. If touching rendering: visual-regression test must pass.
4. If touching the data model: migration follows §6.2; AuditLog hook fires per `audit-log` skill.
5. If adding a new section: decide whether it's structural (always renders) or LLM-augmented (renders with fallback).
6. Run `/defense-kit-render outage-fallback` slash command to verify locally before commit.

## What you cannot do

- **No code path where the defense kit fails to generate because of an LLM problem.**
- **No swallowing of structural-rendering errors.** Structural failure is a bug to fix, not catch.
- **No removing or weakening `narrative_status`.** It's the audit signal AMs and admins rely on.
- **No PDF generation outside Playwright** — keeping a single rendering pipeline keeps visual parity with HTML.
- **No inline LLM prompts.** Prompts live in `apps/api/llm/prompts/defense_kit/vN.py`.
