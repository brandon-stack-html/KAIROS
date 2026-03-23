from dataclasses import dataclass


@dataclass(frozen=True)
class RequestChangesCommand:
    deliverable_id: str
    reviewer_id: str
    tenant_id: str
