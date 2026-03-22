from dataclasses import dataclass


@dataclass(frozen=True)
class ChangeMemberRoleCommand:
    org_id: str
    changer_id: str     # UserId.value of the user performing the change
    user_id: str        # UserId.value of the target user
    new_role: str       # Role.value: "OWNER" | "ADMIN" | "MEMBER"
    tenant_id: str
