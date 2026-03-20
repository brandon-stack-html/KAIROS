"""Global domain exception handler for FastAPI.

Maps the domain error hierarchy to HTTP status codes with a consistent
JSON error envelope. Routes never need their own try/except for domain errors.

Error schema:
    {"error": {"type": "UserNotFoundError", "message": "User 'x' not found."}}
"""
from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.shared.errors import ConflictError, DomainError, EntityNotFoundError
from src.infrastructure.api.logging import get_logger

_logger = get_logger(__name__)

_STATUS_MAP = {
    EntityNotFoundError: 404,
    ConflictError: 409,
    DomainError: 400,
}


async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    # Walk MRO to find the most specific registered status code
    for exc_class in type(exc).__mro__:
        if exc_class in _STATUS_MAP:
            status_code = _STATUS_MAP[exc_class]
            break
    else:
        status_code = 400

    _logger.warning(
        "domain_error",
        error_type=type(exc).__name__,
        error_message=str(exc),
        status_code=status_code,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status_code,
        content={"error": {"type": type(exc).__name__, "message": str(exc)}},
    )
