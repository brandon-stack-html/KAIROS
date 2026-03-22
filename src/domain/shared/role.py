from enum import Enum


class Role(str, Enum):
    """Member roles within an organization.

    Inherits from str so the value serializes cleanly to/from DB and JSON.
    """

    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

    def can_invite(self) -> bool:
        """OWNER and ADMIN can invite new members."""
        return self in (Role.OWNER, Role.ADMIN)

    def can_delete_org(self) -> bool:
        """Only the OWNER can dissolve an organization."""
        return self is Role.OWNER
