"""TracingMiddleware — attaches a correlation_id to every request.

The ID is:
1. Read from the incoming X-Correlation-ID header (if present, lets callers
   propagate their own trace through multiple services).
2. Generated as a fresh UUID4 if the header is absent.

The ID is then:
- Bound to structlog's context vars so every log line in this request
  automatically includes it.
- Injected into the response headers as X-Correlation-ID.
"""

import re
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

CORRELATION_HEADER = "X-Correlation-ID"


class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Only accept valid UUID4 format from clients — reject arbitrary strings
        # to prevent log injection attacks.
        _UUID_RE = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        provided = request.headers.get(CORRELATION_HEADER, "")
        correlation_id = (
            provided
            if provided and _UUID_RE.match(provided.lower())
            else str(uuid.uuid4())
        )

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)
        response.headers[CORRELATION_HEADER] = correlation_id
        return response
