from src.domain.shared.errors import DomainError


class InvalidEmailError(DomainError):
    def __init__(self, value: str) -> None:
        super().__init__(f"'{value}' is not a valid email address.")


class InvalidUserNameError(DomainError):
    def __init__(self, value: str) -> None:
        super().__init__(f"User name must be 2–100 characters, got '{value}'.")


class UserAlreadyExistsError(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__(f"A user with email '{email}' already exists.")


class UserNotFoundError(DomainError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"User '{identifier}' not found.")
