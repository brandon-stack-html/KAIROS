from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class TenantCreated(DomainEvent):
    """Raised when a new tenant is provisioned."""

    tenant_id: str
    name: str
    slug: str
