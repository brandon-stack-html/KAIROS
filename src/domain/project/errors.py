from src.domain.shared.errors import DomainError, EntityNotFoundError


class ProjectNotFoundError(EntityNotFoundError):
    def __init__(self, project_id: str) -> None:
        super().__init__(f"Project '{project_id}' not found.")


class InvalidProjectNameError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Invalid project name: {name!r}. Must be 2–100 characters.")
