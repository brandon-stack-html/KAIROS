from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateClientUpdateCommand:
    project_id: str
    tenant_id: str
