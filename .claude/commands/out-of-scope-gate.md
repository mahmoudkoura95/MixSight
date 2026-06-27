---
description: Read the phase's explicit out-of-scope section and check the current branch against it. Run before merging large branches.
---

Run an out-of-scope gate on the current branch.

1. **Identify active phase** from `CURRENT_PHASE.md`.

2. **Read the explicit out-of-scope section** for the active phase:
   - Phase 1: SCOPE.md §7.20
   - Phase 2: SCOPE.md §8.5 (Out of scope subsection)
   - Phase 3: SCOPE.md §9.4 (Out of scope subsection)
   - Phase 4: SCOPE.md §10.3 (constraints)

3. **Read the branch.** Run `git diff main...HEAD --stat` (or against the appropriate base branch). Identify added or substantially modified surfaces.

4. **Cross-check each surface against the out-of-scope list.** Specifically:
   - Real-time / sub-daily refresh paths beyond daily?
   - Auto-execution of reallocations? Anywhere?
   - Ad-set or creative-level performance surfaces?
   - MMM code outside `modeling/engines/stub/` in Phase 1?
   - Audience overlap, MTA, server-side conversion tracking?
   - A/B test or experiment management UI?
   - Cross-client benchmarking?
   - Plan generation from brief?
   - DV360 or The Trade Desk connectors?
   - A third "blended" allocation mode anywhere?
   - Public-facing accuracy reporting?
   - Lift test design surfaces (before Phase 3)?
   - Agentic auto-trading?
   - Multi-model BYOK?
   - Deep CSV ingestion in Phase 1 (only shallow in 1c per §7.14)?
   - Custom SAML SSO or Layer 3 white-label (before Phase 4)?
   - Self-serve Enterprise tier (before Phase 4)?

5. **Cut-of-last-resort check.** If we're in Phase 1c and time is tight, the current week view (§7.16) is the documented cut. Has anyone been pulled toward cutting something else?

6. **Produce a verdict.** Either:
   - ✓ Branch is in scope. Recommend proceeding to merge.
   - ⚠ Branch contains arguably-borderline work. List items, recommend `DECISIONS.md` entry.
   - ✗ Branch contains out-of-scope work. List items, recommend revert or extraction to a future-phase branch.

7. **If ✗:** be specific. Reverting feels expensive but unsticking phase discipline pays back tenfold.

Be honest. The whole virtue of this scope is that §7.20 et al. say "no" out loud — don't soften that.
