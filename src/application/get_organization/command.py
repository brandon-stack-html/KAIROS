from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrganizationCommand:
    org_id: str
    tenant_id: str
