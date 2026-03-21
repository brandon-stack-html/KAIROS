from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.domain.shared.errors import DomainError
from src.infrastructure.api.logging import configure_logging
from src.infrastructure.api.middleware.exception_handler import domain_exception_handler
from src.infrastructure.api.middleware.security_headers import SecurityHeadersMiddleware
from src.infrastructure.api.middleware.tracing import TracingMiddleware
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.config.settings import settings

configure_logging(log_level="DEBUG" if settings.debug else "INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Register imperative mappers (idempotent).
    from src.infrastructure.persistence.sqlalchemy.mappers.user_mapper import (
        start_mappers,
    )
    start_mappers()

    # 2. Create tables (development only — use Alembic in production).
    if settings.debug:
        from src.infrastructure.persistence.sqlalchemy.database import (
            engine,
            metadata,
        )
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# ── Rate limiter state ─────────────────────────────────────────────────
app.state.limiter = limiter

# ── Middleware (outermost first) ───────────────────────────────────────
# HTTPS redirect — only in production to avoid breaking local dev & tests
if settings.environment == "production":
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TracingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Correlation-ID"],
    max_age=600,
)

# ── Exception handlers ────────────────────────────────────────────────
app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Routers ───────────────────────────────────────────────────────────
from src.infrastructure.api.routers import auth, users  # noqa: E402

app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
