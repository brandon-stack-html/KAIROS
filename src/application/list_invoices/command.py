from dataclasses import dataclass


@dataclass(frozen=True)
class ListInvoicesCommand:
    org_id: str
    tenant_id: str
