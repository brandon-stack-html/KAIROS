from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class InvoiceIssued(DomainEvent):
    invoice_id: str
    title: str
    amount: str  # str to avoid Decimal in events
    org_id: str
    tenant_id: str
    issued_by: str


@dataclass(frozen=True, kw_only=True)
class InvoicePaid(DomainEvent):
    invoice_id: str
    org_id: str
    tenant_id: str
