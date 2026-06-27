---
description: Kick off a new phase or sub-phase. Reads scope, enumerates deliverables, updates CURRENT_PHASE.md, and produces a one-page plan before any code is written.
argument-hint: [phase] (e.g., "1a", "1b", "1c", "2a", "2b", "2c", "2d", "3a", "3b", "3c", "3d", "3e", "4")
---

We are starting Phase $ARGUMENTS.

Walk through this checklist before any code is written:

1. **Read `SCOPE.md`** — the section corresponding to Phase $ARGUMENTS. Specifically:
   - Phase 1: §7.3 sub-phase sequencing + §7.4 data model + relevant §7.x feature sections
   - Phase 2: §8.3 sub-phase sequencing + §8.2 modeling approach
   - Phase 3: §9.3 sub-phase sequencing + §9.2 components
   - Phase 4: §10.2 components

2. **Read `CURRENT_PHASE.md`** — current state. If the previous phase isn't complete, ask the user whether to proceed anyway.

3. **Enumerate deliverables** for Phase $ARGUMENTS, citing the scope section for each.

4. **Identify entities and migrations.** Cross-check against §7.4. Note any tables that were provisioned empty in Phase 1a and now need columns or population.

5. **Identify the cross-cutting concerns** for this phase:
   - Which surfaces add LLM calls? Each needs a §7.17 fallback.
   - Which surfaces add endpoints with `client_id`? Each needs tenancy enforcement.
   - Which surfaces introduce mutations on existing tables? Each needs AuditLog coverage.
   - Which surfaces add `ReallocationSuggestion` paths? Each needs `RecommendationLog`.
   - Which surfaces add charts or pacing views? Each needs empty-state coverage from §7.18.

6. **Check out-of-scope** — read §7.20 (Phase 1), §8.5 (Phase 2), §9.4 (Phase 3), §10.3 (Phase 4) and confirm we're not about to build something deferred.

7. **Check phase risks** — read §7.21 / §8.6 / §9.5 / §10.4 for the relevant phase. Note any mitigations that need to be in place before substantive work begins.

8. **Read pre-build dependencies** — §5. Any external dependencies (API approvals, accounts, SOC 2 engagement) that need to be in motion?

9. **Produce a one-page plan** — week-by-week deliverables, dependencies, decision points. Reference scope sections throughout.

10. **Update `CURRENT_PHASE.md`** — phase marker, week, deliverable checklist, out-of-scope reminders, blockers.

11. **Ask the user to confirm the plan before any code is written.**

If Phase $ARGUMENTS is 1b: refuse to proceed if `DESIGN_PARTNER_COMMITTED: false` in `CURRENT_PHASE.md`. Per §5.7 failure-mode response, broaden target profile or extend Phase 1a outreach instead.

If Phase $ARGUMENTS is 2a: confirm SOC 2 engagement is scheduled per §5.6.

If Phase $ARGUMENTS is 2 or later: confirm Phase 1 success criteria (§7.22) were met.
