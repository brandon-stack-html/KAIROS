from dataclasses import dataclass


@dataclass(frozen=True)
class RemoveMemberCommand:
    org_id: str
    remover_id: str  # UserId.value of the user performing the removal
    user_id: str  # UserId.value of the user being removed
    tenant_id: str
