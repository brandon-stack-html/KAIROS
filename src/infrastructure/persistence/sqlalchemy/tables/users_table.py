"""users table — pure SQLAlchemy Table definition.

No ORM class here. The mapping to the domain User entity is done
imperatively in mappers/user_mapper.py.
"""
from sqlalchemy import Boolean, Column, DateTime, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    UserEmailType,
    UserIdType,
    UserNameType,
)

users_table = Table(
    "users",
    metadata,
    Column("id", UserIdType, primary_key=True),
    Column("email", UserEmailType, unique=True, nullable=False, index=True),
    Column("name", UserNameType, nullable=False),
    Column("hashed_password", nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
    ),
)
