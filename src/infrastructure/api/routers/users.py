from fastapi import APIRouter, Depends, Request, status

from src.application.get_current_user.command import GetCurrentUserCommand
from src.application.get_current_user.handler import GetCurrentUserHandler
from src.application.register_user.command import RegisterUserCommand
from src.application.register_user.handler import RegisterUserHandler
from src.infrastructure.api.dependencies import get_current_user
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.user_schemas import UserCreateRequest, UserResponse
from src.infrastructure.config.container import (
    get_current_user_handler,
    get_register_user_handler,
)
from src.infrastructure.config.settings import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
@limiter.limit("3/minute")
async def register_user(
    request: Request,
    body: UserCreateRequest,
    handler: RegisterUserHandler = Depends(get_register_user_handler),
) -> UserResponse:
    # Domain errors (UserAlreadyExistsError, etc.) bubble up to the
    # global exception handler — no try/except needed here.
    user_id = await handler.handle(
        RegisterUserCommand(
            email=str(body.email),
            name=body.name,
            password=body.password,
            tenant_id=body.tenant_id,
            app_name=settings.app_name,
        )
    )
    return UserResponse(
        id=user_id, email=str(body.email), name=body.name, is_active=True
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the current authenticated user",
)
@limiter.limit("60/minute")
async def get_me(
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: GetCurrentUserHandler = Depends(get_current_user_handler),
) -> UserResponse:
    tenant_id: str = request.state.tenant_id
    user_id: str = payload["sub"]
    user = await handler.handle(
        GetCurrentUserCommand(user_id=user_id, tenant_id=tenant_id)
    )
    return UserResponse(
        id=user.id.value,
        email=user.email.value,
        name=user.name.value,
        is_active=user.is_active,
    )
