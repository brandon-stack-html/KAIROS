"""TenantMiddleware — extracts and validates tenant context from JWT.

For every request that is NOT a public route:
  1. Reads the Bearer token from Authorization header.
  2. Decodes it and extracts the 'tid' (tenant_id) claim.
  3. Binds tenant_id to structlog context for all log lines in this request.
  4. Stores tenant_id in request.state so downstream dependencies can use it.

Public routes (no tenant enforcement):
  - GET  /health
  - POST /api/v1/auth/login
  - POST /api/v1/users   (registration — tenant_id comes from body)
"""

import jwt
import structlog
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.infrastructure.security.jwt_handler import decode_token

_PUBLIC_PATHS: set[tuple[str, str]] = {
    ("GET", "/health"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/refresh"),  # uses refresh token, not JWT
    ("POST", "/api/v1/auth/logout"),  # token revocation — no JWT needed
    ("POST", "/api/v1/users"),
    ("POST", "/api/v1/users/"),  # trailing-slash variant
}

_PUBLIC_PREFIXES: tuple[str, ...] = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/tenants",  # tenant lookup + creation are public (pre-auth)
)


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path
        route_key = (request.method.upper(), path)

        # Skip tenant enforcement for public routes
        if route_key in _PUBLIC_PATHS or path.startswith(_PUBLIC_PREFIXES):
            return await call_next(request)

        # Extract Bearer token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": {"message": "Authorization header missing or malformed."}
                },
            )

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"error": {"message": "Token has expired."}},
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"error": {"message": "Invalid token."}},
            )

        tenant_id: str = payload.get("tid", "")
        if not tenant_id:
            return JSONResponse(
                status_code=401,
                content={"error": {"message": "Token is missing tenant claim (tid)."}},
            )

        # Bind to structlog context (visible in all log lines for this request)
        structlog.contextvars.bind_contextvars(tenant_id=tenant_id)

        # Store in request state for FastAPI dependencies
        request.state.tenant_id = tenant_id

        return await call_next(request)
