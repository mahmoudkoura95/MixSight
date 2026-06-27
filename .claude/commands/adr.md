---
description: Append a decision record to DECISIONS.md. Use whenever a choice comes up during build that wasn't pre-decided in SCOPE.md §3.
argument-hint: <decision-headline> (e.g., "use_caddy_over_vercel_for_white_label_domains")
---

Append a decision record to `DECISIONS.md`: `$ARGUMENTS`.

ADRs (Architecture Decision Records) capture the moments when you make a choice that isn't pre-decided in SCOPE.md §3. They prevent re-litigation under deadline pressure.

1. **Read `DECISIONS.md`** to check for duplicates or conflicts with existing decisions.

2. **Capture the decision** in this format:

   ```markdown
   ## ADR-NNN: $ARGUMENTS

   **Date:** [today]
   **Phase:** [current phase from CURRENT_PHASE.md]
   **Status:** Accepted | Superseded by ADR-XXX | Rejected
   **Scope reference:** [SCOPE.md section if applicable, or "extension"]

   ### Context

   [What forced this decision. What's the problem we're solving?]

   ### Decision

   [The choice made. State it definitively.]

   ### Alternatives considered

   - Alternative A: [why not]
   - Alternative B: [why not]

   ### Consequences

   - Positive: [what we get]
   - Negative: [what we lose or risk]
   - Reversibility: [easy / moderate / hard]

   ### Related

   - Related ADRs: [#]
   - Related SCOPE.md sections: [§]
   ```

3. **Number the ADR.** Sequential, never reused. If ADR-007 is rejected later, it stays at #007 with status "Superseded by ADR-NNN" — don't renumber.

4. **Be honest about reversibility.** A reversible decision can be revisited cheaply. An irreversible one (data model, public API surface) deserves more scrutiny up front.

5. **Cross-link.** If this ADR supersedes another, edit the prior ADR's status. If it extends a SCOPE.md section, note that in the scope reference.

6. **Append** to `DECISIONS.md` under the appropriate phase heading.

7. **Mention in the next commit message** so the decision is git-traceable.

ADRs are not retroactive paperwork — they're a one-paragraph speed bump that forces explicitness when you're making a choice the future-you (or a future engineer) will want to understand. Use them liberally for anything non-obvious.
