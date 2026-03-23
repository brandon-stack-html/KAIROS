from dataclasses import dataclass


@dataclass(frozen=True)
class GetCurrentUserCommand:
    user_id: str
    tenant_id: str
