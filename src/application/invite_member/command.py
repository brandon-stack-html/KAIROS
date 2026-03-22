from dataclasses import dataclass


@dataclass(frozen=True)
class InviteMemberCommand:
    org_id: str
    inviter_id: str     # UserId.value
    invitee_email: str
    role: str           # Role.value: "OWNER" | "ADMIN" | "MEMBER"
    tenant_id: str
    frontend_url: str = "http://localhost:3000"  # used to build accept_url in the email
