from dataclasses import dataclass


@dataclass(frozen=True)
class ListProjectsCommand:
    user_id: str
    tenant_id: str
    org_id: str | None = None
