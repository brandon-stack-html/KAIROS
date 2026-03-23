"""LoginUserHandler — use case / application service.

Orchestrates:
  1. Resolve user by email
  2. Verify plain password against stored hash
  3. Issue a short-lived access token (via ITokenGenerator)
  4. Issue and persist a long-lived refresh token (via uow.refresh_tokens)

Raises UserNotFoundError for both "user does not exist" and "wrong password"
to avoid leaking user enumeration information.
"""

from src.application.login_user.command import LoginUserCommand
from src.application.login_user.ports import ITokenGenerator
from src.application.register_user.ports import IUserUnitOfWork
from src.application.shared.password_hasher import AbstractPasswordHasher
from src.domain.shared.refresh_token import RefreshToken
from src.domain.user.errors import UserNotFoundError
from src.domain.user.user import UserEmail
from src.infrastructure.config.settings import settings


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

    async def handle(self, command: LoginUserCommand) -> tuple[str, str]:
        """Return (access_token, refresh_token_uuid)."""
        async with self._uow:
            email = UserEmail(command.email)
            user = await self._uow.users.find_by_email(email)

            if user is None or not self._hasher.verify(
                command.password, user.hashed_password
            ):
                raise UserNotFoundError(command.email)

            access_token = self._token_generator.generate(
                user_id=user.id.value,
                email=user.email.value,
                tenant_id=user.tenant_id.value if user.tenant_id else "",
            )

            refresh_token = RefreshToken.issue(
                user_id=user.id,
                tenant_id=user.tenant_id,  # type: ignore[arg-type]
                ttl_days=settings.refresh_token_ttl_days,
            )
            await self._uow.refresh_tokens.save(refresh_token)

            return access_token, refresh_token.token
