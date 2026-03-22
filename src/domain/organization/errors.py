from src.domain.shared.errors import ConflictError, DomainError, EntityNotFoundError


class OrganizationNotFoundError(EntityNotFoundError):
    def __init__(self, org_id: str) -> None:
        super().__init__(f"Organization '{org_id}' not found.")


class MemberAlreadyExistsError(ConflictError):
    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(f"User '{user_id}' is already a member of organization '{org_id}'.")


class MemberNotFoundError(EntityNotFoundError):
    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(f"User '{user_id}' is not a member of organization '{org_id}'.")


class InsufficientRoleError(DomainError):
    """Raised when the requester's role doesn't allow the operation. Maps to HTTP 403."""

    def __init__(self, message: str = "Insufficient role to perform this operation.") -> None:
        super().__init__(message)


class CannotRemoveLastOwnerError(DomainError):
    def __init__(self) -> None:
        super().__init__("Cannot remove or demote the last owner of an organization.")


class InvitationExpiredError(DomainError):
    def __init__(self) -> None:
        super().__init__("This invitation has expired.")


class InvitationAlreadyAcceptedError(DomainError):
    def __init__(self) -> None:
        super().__init__("This invitation has already been accepted.")


class InvalidOrgNameError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Invalid organization name: {name!r}. Must be 2–100 characters.")


class InvalidOrgSlugError(DomainError):
    def __init__(self, slug: str) -> None:
        super().__init__(
            f"Invalid organization slug: {slug!r}. "
            "Must be 2–63 lowercase alphanumeric chars or hyphens, "
            "cannot start or end with a hyphen."
        )
