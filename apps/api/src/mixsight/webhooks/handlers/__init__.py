"""Clerk webhook event handlers.

One module per Clerk entity family: organization, user, membership.
The dispatcher in `mixsight.webhooks.clerk` looks up handlers by event
type and invokes them with the parsed event data + an `AsyncSession`.

Per §7.19: Clerk is the authentication source of truth; our DB is the
authorization source of truth. Webhook upserts keep the two in sync.

Out-of-order protection: each handler compares the event's `updated_at`
(milliseconds since epoch from Clerk) against the existing entity's
`updated_at`. Stale events are skipped + logged.

The dispatch function lives at `.dispatch.dispatch`. We intentionally do
NOT re-export it here — `from mixsight.webhooks.handlers import dispatch`
would otherwise resolve to the function and shadow the module of the
same name, breaking `dispatch.dispatch(...)` call sites with a confusing
AttributeError.
"""

from mixsight.webhooks.handlers.dispatch import HANDLERS

__all__ = ["HANDLERS"]
