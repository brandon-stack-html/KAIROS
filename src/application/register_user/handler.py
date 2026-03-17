"""RegisterUserHandler — use case / application service.

Orchestrates:
  1. Duplicate-email guard
  2. Password hashing (delegated to injected port)
  3. Domain object creation (User.register)
  4. Persistence via Unit of Work
  5. (Optional) Domain-event publishing – wired in via IEventPublisher

The handler raises domain errors on business-rule violations so the
API layer can translate them to HTTP responses.
"""
from src.application.register_user.command import RegisterUserCommand
from src.application.register_user.ports import IUserUnitOfWork
from src.application.shared.password_hasher import AbstractPasswordHasher
from src.domain.user.errors import UserAlreadyExistsError
from src.domain.user.user import User, UserEmail, UserName


class RegisterUserHandler:
    def __init__(
        self,
        uow: IUserUnitOfWork,
        password_hasher: AbstractPasswordHasher,
    ) -> None:
        self._uow = uow
        self._hasher = password_hasher

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
            )

            await self._uow.users.save(user)
            # Events could be published here via an IEventPublisher port.
            # Omitted for brevity – add when messaging infra is wired up.

        return user.id.value
