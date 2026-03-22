from dataclasses import dataclass


@dataclass(frozen=True)
class AcceptInvitationCommand:
    invitation_id: str
    user_id: str        # UserId.value of the accepting user
    tenant_id: str
