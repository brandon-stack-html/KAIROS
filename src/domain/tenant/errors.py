from src.domain.shared.errors import ConflictError, EntityNotFoundError


class TenantNotFoundError(EntityNotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Tenant '{identifier}' not found.")


class SlugAlreadyTakenError(ConflictError):
    def __init__(self, slug: str) -> None:
        super().__init__(f"Slug '{slug}' is already taken.")


class InvalidTenantNameError(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Tenant name is invalid: {name!r}")


class InvalidTenantSlugError(ValueError):
    def __init__(self, slug: str) -> None:
        super().__init__(
            f"Tenant slug must be 2-63 lowercase alphanumeric chars or hyphens, got: {slug!r}"
        )
