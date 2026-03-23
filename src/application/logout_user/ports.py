from abc import ABC, abstractmethod

from src.application.logout_user.command import LogoutCommand


class ILogoutUseCase(ABC):
    @abstractmethod
    async def handle(self, command: LogoutCommand) -> None: ...
