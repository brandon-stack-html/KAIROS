from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateUserProfileCommand:
    user_id: str
    tenant_id: str
    full_name: str | None = None
    avatar_url: str | None = None
