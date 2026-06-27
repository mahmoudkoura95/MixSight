---
description: Render a defense kit against a fixture client locally. Useful for visual regression in Phase 1c. Verifies all sections + structural fallback when LLM is unavailable.
argument-hint: <fixture-name> (e.g., "single-market", "multi-market-rolled-up", "outage-fallback")
---

Render a defense kit against fixture: `$ARGUMENTS`.

Per SCOPE.md §7.13, the defense kit has structural elements and an LLM-generated narrative. The structural elements never block on LLM. This command exercises both the happy path and the templated-fallback path.

1. **Load the fixture** from `apps/api/tests/fixtures/defense_kit/$ARGUMENTS/`. Should contain:
   - A `PacingSnapshot` with `PacingSnapshotLine` rows.
   - A selected `ReallocationSuggestion`.
   - Plan-change audit entries.
   - Optionally: an `outage_fallback: true` flag that simulates LLM unavailability.

2. **Generate the defense kit** via the API route:

   ```bash
   curl -X POST http://localhost:8000/clients/<fixture_client_id>/snapshots/<fixture_snapshot_id>/defense-kit \
     -H "Authorization: Bearer <dev_token>"
   ```

   Or call directly in a Python shell:

   ```python
   from defense_kit.generator import generate_defense_kit
   await generate_defense_kit(snapshot_id, render_mode="per_market")
   ```

3. **Verify HTML rendering.** Open the generated HTML in browser. Verify:
   - Header with agency logo (white-label Layer 1 applied).
   - Top-line summary (LLM-generated or templated, see `narrative_status`).
   - Pacing table grouped per `render_mode`.
   - Top 3 drift callouts.
   - Selected reallocation block.
   - Plan-change audit.
   - Methodology footnote.
   - Next-week outlook.

4. **Verify PDF rendering.** The HTML routes through Playwright headless Chromium. Generated PDF should be byte-identical to the HTML visually. Sanity-check:
   - Page breaks land sensibly.
   - Charts render (not blank).
   - Branding colors match the input `branding_config`.
   - Footer "Powered by MixSight" toggle respected.

5. **If fixture is `outage-fallback`:** verify the LLM-failure path:
   - Defense kit **still generates** with all structural elements.
   - Narrative is replaced with templated fallback: "Top-line summary: [edit this paragraph with your client-facing narrative]."
   - `DefenseKit.narrative_status = templated_fallback`.
   - "Regenerate narrative" button visible.
   - Generation completes within 60s.
   - **The defense kit is usable for the Monday meeting.**

6. **Visual regression.** Compare against the golden PDF in `tests/fixtures/defense_kit/$ARGUMENTS/golden.pdf`. If divergence is intentional (e.g., copy change), update the golden file. If not, investigate.

7. **Render times.** Expected: <10 seconds for HTML, <20 seconds for PDF. If significantly slower, profile Playwright + Chromium memory.

8. **Snapshot the rendered output** under `tests/artifacts/defense_kit/<timestamp>/` for the visual log.

Reminder: defense kit never blocks on LLM. This is the single most-tested fallback in the product — when Anthropic has a Monday outage, this is what determines whether MixSight is usable that morning.
