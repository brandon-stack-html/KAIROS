from fastapi import APIRouter, Depends, status

from src.application.register_user.command import RegisterUserCommand
from src.application.register_user.handler import RegisterUserHandler
from src.infrastructure.api.schemas.user_schemas import UserCreateRequest, UserResponse
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
    # Domain errors (UserAlreadyExistsError, etc.) bubble up to the
    # global exception handler — no try/except needed here.
    user_id = await handler.handle(
        RegisterUserCommand(
            email=str(body.email),
            name=body.name,
            password=body.password,
        )
    )
    return UserResponse(id=user_id, email=str(body.email), name=body.name, is_active=True)
