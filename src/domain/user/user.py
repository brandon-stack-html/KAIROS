"""User aggregate root + value objects.

Domain rules enforced here:
- Email must match RFC-5322-lite regex.
- Name must be 2–100 characters (stripped).
- Password is stored pre-hashed (hashing is an application concern).
- Raising UserRegistered / UserDeactivated domain events is the only
  way to signal state changes to the outside world.
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.tenant_id import TenantId
from src.domain.shared.value_object import ValueObject
from src.domain.user.errors import InvalidEmailError, InvalidUserNameError
from src.domain.user.events import UserDeactivated, UserRegistered

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


# ──────────────────────────────────────────────
# Value Objects
# ──────────────────────────────────────────────


@dataclass(frozen=True)
class UserId(ValueObject):
    value: str

    @classmethod
    def generate(cls) -> "UserId":
        return cls(value=str(uuid.uuid4()))

    def __composite_values__(self) -> tuple[str]:
        """Required by SQLAlchemy composite() mapping."""
        return (self.value,)


@dataclass(frozen=True)
class UserEmail(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise InvalidEmailError(self.value)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)


@dataclass(frozen=True)
class UserName(ValueObject):
    value: str

    def __post_init__(self) -> None:
        stripped = self.value.strip()
        if not (2 <= len(stripped) <= 100):
            raise InvalidUserNameError(stripped)
        # frozen=True prevents normal assignment; use object.__setattr__
        object.__setattr__(self, "value", stripped)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)


# ──────────────────────────────────────────────
# Aggregate Root
# ──────────────────────────────────────────────


@dataclass(eq=False)
class User(AggregateRoot):
    """User aggregate root.

    Field order matters for @dataclass inheritance:
      id             – inherited from Entity (required, no default)
      _domain_events – inherited from AggregateRoot (init=False, excluded)
      email / name / hashed_password / tenant_id – required
      is_active / created_at – optional (have defaults)

    tenant_id is TenantId | None so SQLAlchemy can reconstruct rows that
    pre-date multi-tenancy (NULL in DB). New users always have a tenant_id.
    """

    id: UserId
    email: UserEmail
    name: UserName
    hashed_password: str
    tenant_id: TenantId | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def register(
        cls,
        email: UserEmail,
        name: UserName,
        hashed_password: str,
        tenant_id: TenantId,
    ) -> "User":
        user = cls(
            id=UserId.generate(),
            email=email,
            name=name,
            hashed_password=hashed_password,
            tenant_id=tenant_id,
        )
        user.add_domain_event(UserRegistered(user_id=user.id.value, email=email.value))
        return user

    def deactivate(self) -> None:
        if not self.is_active:
            return
        self.is_active = False
        self.add_domain_event(UserDeactivated(user_id=self.id.value))
