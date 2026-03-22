from fastapi import APIRouter, Depends, Request, status

from src.application.login_user.command import LoginUserCommand
from src.application.login_user.handler import LoginUserHandler
from src.application.logout_user.command import LogoutCommand
from src.application.logout_user.handler import LogoutHandler
from src.application.refresh_token.command import RefreshTokenCommand
from src.application.refresh_token.handler import RefreshTokenHandler
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.user_schemas import (
    LogoutRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
)
from src.infrastructure.config.container import (
    get_login_user_handler,
    get_logout_handler,
    get_refresh_token_handler,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive access + refresh tokens",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    handler: LoginUserHandler = Depends(get_login_user_handler),
) -> TokenResponse:
    access_token, refresh_token = await handler.handle(
        LoginUserCommand(email=str(body.email), password=body.password)
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange a valid refresh token for new access + refresh tokens",
)
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    handler: RefreshTokenHandler = Depends(get_refresh_token_handler),
) -> TokenResponse:
    access_token, new_refresh_token = await handler.handle(
        RefreshTokenCommand(token=body.refresh_token)
    )
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a refresh token (logout)",
)
@limiter.limit("5/minute")
async def logout(
    request: Request,
    body: LogoutRequest,
    handler: LogoutHandler = Depends(get_logout_handler),
) -> None:
    await handler.handle(LogoutCommand(refresh_token=body.refresh_token))
