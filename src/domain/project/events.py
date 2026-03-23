from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ProjectCreated(DomainEvent):
    project_id: str
    name: str
    org_id: str
    tenant_id: str
    owner_id: str
