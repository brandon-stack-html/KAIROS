from dataclasses import dataclass


@dataclass(frozen=True)
class MarkInvoicePaidCommand:
    invoice_id: str
    requester_id: str
    tenant_id: str
