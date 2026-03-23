"""RefreshToken — domain value object.

Treated as immutable: revoke() returns a new instance instead of
mutating in place. The `token` UUID string is the natural primary key
for persistence, but this class does NOT extend Entity (it has no
separate `id` field and is not an aggregate root).

Note: NOT a frozen dataclass — SQLAlchemy's imperative mapper needs to
set attributes during reconstruction from the DB.
"""

import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta

from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


@dataclass
class RefreshToken:
    token: str
    user_id: UserId
    tenant_id: TenantId
    expires_at: datetime
    is_revoked: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # ── Factories ─────────────────────────────────────────────────────────

    @classmethod
    def issue(
        cls,
        user_id: UserId,
        tenant_id: TenantId,
        ttl_days: int,
    ) -> "RefreshToken":
        """Issue a fresh, non-revoked refresh token."""
        now = datetime.now(UTC)
        return cls(
            token=str(uuid.uuid4()),
            user_id=user_id,
            tenant_id=tenant_id,
            expires_at=now + timedelta(days=ttl_days),
            is_revoked=False,
            created_at=now,
        )

    # ── Behaviour ─────────────────────────────────────────────────────────

    def revoke(self) -> "RefreshToken":
        """Return a new RefreshToken with is_revoked=True."""
        return replace(self, is_revoked=True)

    def is_expired(self) -> bool:
        now = datetime.now(UTC)
        expires = self.expires_at
        # SQLite returns naive datetimes — normalise to UTC for comparison.
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        return now >= expires
