from dataclasses import dataclass


@dataclass(frozen=True)
class IssueInvoiceCommand:
    title: str
    amount: str  # str at the HTTP boundary; handler converts to Decimal
    org_id: str
    issuer_id: str
    tenant_id: str
