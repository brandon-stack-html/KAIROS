from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.application.shared.errors import AiServiceError
from src.domain.shared.errors import DomainError
from src.infrastructure.api.logging import configure_logging
from src.infrastructure.api.middleware.exception_handler import (
    ai_service_exception_handler,
    domain_exception_handler,
)
from src.infrastructure.api.middleware.security_headers import SecurityHeadersMiddleware
from src.infrastructure.api.middleware.tenant import TenantMiddleware
from src.infrastructure.api.middleware.tracing import TracingMiddleware
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.config.settings import settings

configure_logging(log_level="DEBUG" if settings.debug else "INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Register imperative mappers (idempotent).
    from src.infrastructure.persistence.sqlalchemy.mappers.conversation_mapper import (
        start_mappers as start_conversation_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.deliverable_mapper import (
        start_mappers as start_deliverable_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.invitation_mapper import (
        start_mappers as start_invitation_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.invoice_mapper import (
        start_mappers as start_invoice_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.message_mapper import (
        start_mappers as start_message_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.organization_mapper import (
        start_mappers as start_organization_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.project_mapper import (
        start_mappers as start_project_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.refresh_token_mapper import (
        start_mappers as start_refresh_token_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.tenant_mapper import (
        start_mappers as start_tenant_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.user_mapper import (
        start_mappers as start_user_mappers,
    )

    start_tenant_mappers()         # 1 — no FKs
    start_user_mappers()           # 2 — FK → tenants
    start_refresh_token_mappers()  # 3 — FK → users
    start_organization_mappers()   # 4 — FK → tenants + users
    start_invitation_mappers()     # 5 — FK → organizations + users
    start_project_mappers()        # 6 — FK → organizations + tenants
    start_deliverable_mappers()    # 7 — FK → projects + tenants
    start_invoice_mappers()        # 8 — FK → organizations + tenants
    start_conversation_mappers()   # 9 — FK → organizations + projects
    start_message_mappers()        # 10 — FK → conversations

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
app.add_middleware(TenantMiddleware)
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
app.add_exception_handler(AiServiceError, ai_service_exception_handler)
app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Routers ───────────────────────────────────────────────────────────
from src.infrastructure.api.routers import (  # noqa: E402
    auth,
    deliverables,
    invoices,
    organizations,
    projects,
    tenants,
    users,
)

app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tenants.router, prefix="/api/v1")
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(deliverables.router, prefix="/api/v1")
app.include_router(invoices.router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
