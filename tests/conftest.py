"""Shared pytest fixtures for all test suites.

Strategy:
- Use SQLite in-memory via aiosqlite — no external services needed.
- Each test function gets a fresh, isolated database (function-scoped session).
- The imperative mappers are registered once per test session (idempotent).
- An AsyncClient wrapping the FastAPI app is provided for integration tests.
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.persistence.sqlalchemy.database import metadata

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# ── Mappers (session-scoped — registering twice would raise) ──────────────────

@pytest.fixture(scope="session", autouse=True)
def register_mappers():
    from src.infrastructure.persistence.sqlalchemy.mappers.user_mapper import (
        start_mappers,
    )
    start_mappers()


# ── In-memory database ────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Async SQLite in-memory session, rolled back after each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)

    await engine.dispose()


# ── FastAPI test client ───────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Async HTTP client with the DB session overridden to the test session."""
    from src.infrastructure.api.main import app
    from src.infrastructure.persistence.sqlalchemy.database import get_session

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
