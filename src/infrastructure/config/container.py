"""Composition root — wires concrete adapters to application ports.

All factory functions are plain callables so they work both with
FastAPI's Depends() and in plain unit/integration tests.
"""
from src.application.register_user.handler import RegisterUserHandler
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from src.infrastructure.security.password_hasher import BcryptPasswordHasher

# ── Singletons (stateless, safe to share) ────────────────────────────
_password_hasher = BcryptPasswordHasher()


# ── Per-request factories ─────────────────────────────────────────────
def get_uow() -> SqlAlchemyUnitOfWork:
    """New UoW (and therefore a new AsyncSession) per request."""
    return SqlAlchemyUnitOfWork(session_factory=SessionLocal)


def get_register_user_handler() -> RegisterUserHandler:
    return RegisterUserHandler(
        uow=get_uow(),
        password_hasher=_password_hasher,
    )
