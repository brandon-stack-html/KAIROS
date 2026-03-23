from dataclasses import dataclass


@dataclass(frozen=True)
class ApproveDeliverableCommand:
    deliverable_id: str
    approver_id: str
    tenant_id: str
