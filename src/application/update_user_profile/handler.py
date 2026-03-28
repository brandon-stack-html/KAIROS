from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.application.update_user_profile.command import UpdateUserProfileCommand
from src.domain.shared.errors import EntityNotFoundError
from src.domain.user.user import User, UserId


class UpdateUserProfileHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: UpdateUserProfileCommand) -> User:
        async with self._uow:
            user = await self._uow.users.find_by_id(UserId(command.user_id))
            if user is None:
                raise EntityNotFoundError(f"User '{command.user_id}' not found.")

            user.update_profile(
                full_name=command.full_name,
                avatar_url=command.avatar_url,
            )
            await self._uow.users.save(user)

        return user
