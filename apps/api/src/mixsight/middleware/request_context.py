"""Request-context ASGI middleware.

Sets the `request_id` contextvar at the start of every request and stamps the
response with `x-request-id`. `actor_user_id` is set to None here and re-set
later by `current_user` once the JWT has resolved to a User row — keeping the
contextvar consistent across both authenticated and anonymous requests.

The middleware is implemented as **pure ASGI** rather than via Starlette's
`BaseHTTPMiddleware`: BaseHTTPMiddleware copies the request context into an
inner task group, which historically broke contextvar visibility for inner
code. The AuditLog hook in `mixsight.audit.hooks` runs inside a SQLAlchemy
flush (far from any Request), so we need the contextvar to actually travel.
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from mixsight.audit.context import set_actor_user_id, set_request_id

Scope = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        set_actor_user_id(None)
        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        inbound_id = headers.get(b"x-request-id", b"").decode()
        request_id = inbound_id or str(uuid.uuid4())
        set_request_id(request_id)

        async def send_with_header(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                existing = list(message.get("headers", []))
                existing.append((b"x-request-id", request_id.encode()))
                message["headers"] = existing
            await send(message)

        await self.app(scope, receive, send_with_header)
