"""LoginUserHandler — use case / application service.

Orchestrates:
  1. Resolve user by email
  2. Verify plain password against stored hash
  3. Delegate token generation to ITokenGenerator port (infra concern)

Raises UserNotFoundError for both "user does not exist" and "wrong password"
to avoid leaking user enumeration information.
"""
from src.application.login_user.command import LoginUserCommand
from src.application.login_user.ports import ITokenGenerator
from src.application.register_user.ports import IUserUnitOfWork
from src.application.shared.password_hasher import AbstractPasswordHasher
from src.domain.user.errors import UserNotFoundError
from src.domain.user.user import UserEmail


class LoginUserHandler:
    def __init__(
        self,
        uow: IUserUnitOfWork,
        password_hasher: AbstractPasswordHasher,
        token_generator: ITokenGenerator,
    ) -> None:
        self._uow = uow
        self._hasher = password_hasher
        self._token_generator = token_generator

    async def handle(self, command: LoginUserCommand) -> str:
        """Returns a signed access token string."""
        async with self._uow:
            email = UserEmail(command.email)
            user = await self._uow.users.find_by_email(email)

            if user is None or not self._hasher.verify(command.password, user.hashed_password):
                raise UserNotFoundError(command.email)

            return self._token_generator.generate(
                user_id=user.id.value,
                email=user.email.value,
            )
