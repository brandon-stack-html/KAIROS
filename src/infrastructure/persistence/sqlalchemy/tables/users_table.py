"""users table — pure SQLAlchemy Table definition.

No ORM class here. The mapping to the domain User entity is done
imperatively in mappers/user_mapper.py.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Table, Text

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    TenantIdType,
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
    Column("hashed_password", String, nullable=False),
    Column(
        "tenant_id",
        TenantIdType,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,  # nullable for safe migration of pre-existing rows
        index=True,
    ),
    Column("avatar_url", Text, nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    # Composite index for tenant-scoped queries
    Index("ix_users_tenant_id_email", "tenant_id", "email"),
)
