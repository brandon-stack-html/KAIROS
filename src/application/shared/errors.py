class ApplicationError(Exception):
    """Base class for application-layer errors."""
    pass


class NotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass
