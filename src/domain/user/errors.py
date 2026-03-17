from src.domain.shared.errors import ConflictError, EntityNotFoundError


class InvalidEmailError(Exception):
    def __init__(self, value: str) -> None:
        super().__init__(f"'{value}' is not a valid email address.")


class InvalidUserNameError(Exception):
    def __init__(self, value: str) -> None:
        super().__init__(f"User name must be 2–100 characters, got '{value}'.")


class UserAlreadyExistsError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__(f"A user with email '{email}' already exists.")


class UserNotFoundError(EntityNotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"User '{identifier}' not found.")
