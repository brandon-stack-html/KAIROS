from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class DeliverableSubmitted(DomainEvent):
    deliverable_id: str
    title: str
    project_id: str
    tenant_id: str
    submitted_by: str


@dataclass(frozen=True, kw_only=True)
class DeliverableApproved(DomainEvent):
    deliverable_id: str
    project_id: str
    tenant_id: str
    approved_by: str


@dataclass(frozen=True, kw_only=True)
class ChangesRequested(DomainEvent):
    deliverable_id: str
    project_id: str
    tenant_id: str
    reviewed_by: str
