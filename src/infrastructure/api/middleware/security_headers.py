"""SecurityHeadersMiddleware — injects OWASP-recommended HTTP security headers.

Headers added to every response:
- X-Content-Type-Options: prevent MIME sniffing
- X-Frame-Options: prevent clickjacking
- X-XSS-Protection: legacy XSS filter hint
- Strict-Transport-Security: enforce HTTPS in browsers (HSTS)
- Referrer-Policy: limit referrer information leakage
- Permissions-Policy: disable sensitive browser APIs
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        return response
