"""LogoutHandler — revokes the given refresh token.

No error is raised if the token is already revoked or unknown,
making logout idempotent (safe to call multiple times).
"""
from src.application.logout_user.command import LogoutCommand
from src.application.register_user.ports import IUserUnitOfWork


class LogoutHandler:
    def __init__(self, uow: IUserUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: LogoutCommand) -> None:
        async with self._uow:
            await self._uow.refresh_tokens.revoke(command.refresh_token)
