"""refresh_tokens table — pure SQLAlchemy Table definition.

No ORM class here. Mapping to the domain RefreshToken is done
imperatively in mappers/refresh_token_mapper.py.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import TenantIdType, UserIdType

refresh_tokens_table = Table(
    "refresh_tokens",
    metadata,
    Column("token", String(36), primary_key=True),
    Column(
        "user_id",
        UserIdType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("tenant_id", TenantIdType, nullable=False, index=True),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("is_revoked", Boolean, nullable=False, default=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    # Fast lookup of active tokens per user
    Index("ix_refresh_tokens_user_id_is_revoked", "user_id", "is_revoked"),
)
