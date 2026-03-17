class DomainError(Exception):
    """Base class for all domain errors."""


class EntityNotFoundError(DomainError):
    """Raised when a requested entity does not exist. Maps to HTTP 404."""


class ConflictError(DomainError):
    """Raised when an operation violates a uniqueness constraint. Maps to HTTP 409."""
