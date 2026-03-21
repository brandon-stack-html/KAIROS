from fastapi import APIRouter, Depends, Request, status

from src.application.login_user.command import LoginUserCommand
from src.application.login_user.handler import LoginUserHandler
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.user_schemas import LoginRequest, TokenResponse
from src.infrastructure.config.container import get_login_user_handler

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive an access token",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    handler: LoginUserHandler = Depends(get_login_user_handler),
) -> TokenResponse:
    # UserNotFoundError bubbles up to the global exception handler → 404
    token = await handler.handle(
        LoginUserCommand(email=str(body.email), password=body.password)
    )
    return TokenResponse(access_token=token)
