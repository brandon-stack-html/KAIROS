from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.domain.shared.errors import DomainError
from src.infrastructure.api.middleware.exception_handler import domain_exception_handler
from src.infrastructure.config.settings import settings


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

# ── Exception handlers ────────────────────────────────────────────────
app.add_exception_handler(DomainError, domain_exception_handler)

# ── Routers ───────────────────────────────────────────────────────────
from src.infrastructure.api.routers import auth, users  # noqa: E402

app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
