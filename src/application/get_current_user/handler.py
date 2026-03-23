from src.application.get_current_user.command import GetCurrentUserCommand
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.shared.errors import EntityNotFoundError
from src.domain.user.user import User, UserId


class GetCurrentUserHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: GetCurrentUserCommand) -> User:
        async with self._uow:
            user = await self._uow.users.find_by_id(UserId(command.user_id))
            if user is None:
                raise EntityNotFoundError(f"User '{command.user_id}' not found.")
            return user
