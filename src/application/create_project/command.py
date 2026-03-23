from dataclasses import dataclass


@dataclass(frozen=True)
class CreateProjectCommand:
    name: str
    description: str
    org_id: str
    owner_id: str
    tenant_id: str
