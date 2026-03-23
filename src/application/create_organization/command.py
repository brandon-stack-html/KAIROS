from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrganizationCommand:
    name: str
    slug: str
    owner_id: str  # UserId.value
    tenant_id: str  # TenantId.value
