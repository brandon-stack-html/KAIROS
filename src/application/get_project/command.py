from dataclasses import dataclass


@dataclass(frozen=True)
class GetProjectCommand:
    project_id: str
    tenant_id: str
