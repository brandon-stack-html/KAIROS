"""Tenant aggregate root.

Domain rules enforced here:
- Name: 2–100 characters (stripped).
- Slug: 2–63 lowercase alphanumeric chars or hyphens, cannot start/end with hyphen.
  (Follows DNS label rules — safe for subdomains and URL paths.)
- is_active defaults to True on creation.
- Raises TenantCreated domain event on provisioning.
"""
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.tenant_id import TenantId
from src.domain.tenant.errors import InvalidTenantNameError, InvalidTenantSlugError
from src.domain.tenant.events import TenantCreated

_SLUG_RE = re.compile(r"^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$")


@dataclass(eq=False)
class Tenant(AggregateRoot):
    """Tenant aggregate root.

    Field order for @dataclass inheritance:
      id           – inherited from Entity (required)
      _domain_events – AggregateRoot (init=False)
      name / slug  – required
      is_active / created_at – optional (have defaults)
    """

    id: TenantId
    name: str
    slug: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self._validate_name(self.name)
        self._validate_slug(self.slug)

    # ── Factory ───────────────────────────────────────────────────────────

    @classmethod
    def provision(cls, name: str, slug: str) -> "Tenant":
        """Create a new active tenant and raise TenantCreated event."""
        name = name.strip()
        slug = slug.strip().lower()
        cls._validate_name(name)
        cls._validate_slug(slug)

        tenant = cls(id=TenantId.generate(), name=name, slug=slug)
        tenant.add_domain_event(
            TenantCreated(
                tenant_id=tenant.id.value,
                name=tenant.name,
                slug=tenant.slug,
            )
        )
        return tenant

    # ── Behaviour ─────────────────────────────────────────────────────────

    def deactivate(self) -> None:
        self.is_active = False

    def reactivate(self) -> None:
        self.is_active = True

    # ── Validation helpers ────────────────────────────────────────────────

    @staticmethod
    def _validate_name(name: str) -> None:
        if not (2 <= len(name) <= 100):
            raise InvalidTenantNameError(name)

    @staticmethod
    def _validate_slug(slug: str) -> None:
        if not _SLUG_RE.match(slug):
            raise InvalidTenantSlugError(slug)
