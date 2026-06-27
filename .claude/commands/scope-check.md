---
description: Audit current diff or uncommitted work against SCOPE.md. Every change must be traceable to a scope section. Flags anything that isn't.
---

Run a scope-traceability audit on the current work.

1. **Diff inventory.** Run `git status` and `git diff --stat`. List every modified, added, or deleted file.

2. **Per-file citation check.** For each file:
   - What scope section authorizes this change?
   - Is the change confined to the active phase (read `CURRENT_PHASE.md`)?
   - Does it touch a cross-cutting concern (tenancy, audit, LLM, recommendation log, taxonomy, connector) without going through the corresponding skill?

3. **Cross-cutting verification.** Specifically check:
   - New endpoints in `apps/api/routes/` taking `client_id` → `enforce_client_access` in dependency chain.
   - New mutations on existing tables → covered by the SQLAlchemy AuditLog hook.
   - New `client.messages.create` calls → wrapped by `apps/api/llm/client.py` with surface-specific fallback.
   - New migrations → conform to §6.2 conventions.
   - New `ReallocationSuggestion` creation paths → write to `RecommendationLog`.
   - New connector code → in `apps/api/connectors/<platform>/` only, implements §7.14 Protocol.

4. **Flag uncited or out-of-scope changes.** Produce a table:

   | File | Scope section | Phase | Cross-cutting concerns | Status |
   |---|---|---|---|---|

   `Status` is one of: ✓ traced, ⚠ uncited (no scope section identified), ✗ out-of-scope.

5. **Recommend action.** For uncited changes: revert, or add a scope citation to `DECISIONS.md` if this is a deliberate extension. For out-of-scope changes: revert and add to backlog for the correct phase.

This command is intended to run before commits. Treat its output as advisory but take ⚠ and ✗ seriously.
