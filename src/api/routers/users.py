from fastapi import APIRouter, Depends, HTTPException, status

from src.api.schemas.user_schemas import UserCreateRequest, UserResponse
from src.application.register_user.command import RegisterUserCommand
from src.application.register_user.handler import RegisterUserHandler
from src.domain.user.errors import UserAlreadyExistsError
from src.infrastructure.config.container import get_register_user_handler

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    body: UserCreateRequest,
    handler: RegisterUserHandler = Depends(get_register_user_handler),
) -> UserResponse:
    try:
        user_id = await handler.handle(
            RegisterUserCommand(
                email=str(body.email),
                name=body.name,
                password=body.password,
            )
        )
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return UserResponse(
        id=user_id,
        email=str(body.email),
        name=body.name,
        is_active=True,
    )
