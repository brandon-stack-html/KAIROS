from dataclasses import dataclass


@dataclass(frozen=True)
class ListOrganizationsCommand:
    user_id: str    # UserId.value
    tenant_id: str
