from dataclasses import dataclass


@dataclass(frozen=True)
class ListDeliverablesCommand:
    project_id: str
    tenant_id: str
