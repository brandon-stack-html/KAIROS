class ApplicationError(Exception):
    """Base class for application-layer errors."""
    pass


class NotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class EmailConfigurationError(ApplicationError):
    """Raised when email provider is misconfigured (e.g. missing API key)."""
    pass
