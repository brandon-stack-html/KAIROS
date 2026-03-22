"""RegisterUserHandler — use case / application service.

Orchestrates:
  1. Duplicate-email guard
  2. Password hashing (delegated to injected port)
  3. Domain object creation (User.register)
  4. Persistence via Unit of Work
  5. Welcome email (fire-and-forget — never fails the request)
"""
import structlog

from src.application.register_user.command import RegisterUserCommand
from src.application.register_user.ports import IUserUnitOfWork
from src.application.shared.email_sender import (
    AbstractEmailSender,
    EmailTemplate,
    build_email,
)
from src.application.shared.password_hasher import AbstractPasswordHasher
from src.domain.shared.tenant_id import TenantId
from src.domain.user.errors import UserAlreadyExistsError
from src.domain.user.user import User, UserEmail, UserName

logger = structlog.get_logger()


class RegisterUserHandler:
    def __init__(
        self,
        uow: IUserUnitOfWork,
        password_hasher: AbstractPasswordHasher,
        email_sender: AbstractEmailSender,
    ) -> None:
        self._uow = uow
        self._hasher = password_hasher
        self._email_sender = email_sender

    async def handle(self, command: RegisterUserCommand) -> str:
        """Returns the new user's UUID string."""
        async with self._uow:
            email = UserEmail(command.email)

            if await self._uow.users.exists_by_email(email):
                raise UserAlreadyExistsError(command.email)

            user = User.register(
                email=email,
                name=UserName(command.name),
                hashed_password=self._hasher.hash(command.password),
                tenant_id=TenantId.from_str(command.tenant_id),
            )

            await self._uow.users.save(user)

        # Fire-and-forget: email failure must never block registration.
        try:
            msg = build_email(
                EmailTemplate.WELCOME,
                {
                    "to": command.email,
                    "user_name": command.name,
                    "app_name": command.app_name,
                },
            )
            await self._email_sender.send(msg)
        except Exception:
            logger.warning(
                "email.welcome_failed",
                user_id=user.id.value,
                email=command.email,
            )

        return user.id.value
