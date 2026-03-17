from collections.abc import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.infrastructure.config.settings import settings

# Shared MetaData used by all imperative Table() definitions.
metadata = MetaData()

# Async engine — pool_pre_ping recycles stale connections automatically.
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# DeclarativeBase is kept for any infrastructure-only ORM models
# (e.g. alembic version table). Domain entities are never mapped here.
class Base(DeclarativeBase):
    metadata = metadata


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
