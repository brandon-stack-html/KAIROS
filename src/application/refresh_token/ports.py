"""Ports for the refresh_token use case."""
from abc import ABC, abstractmethod

from src.application.refresh_token.command import RefreshTokenCommand


class IRefreshTokenUseCase(ABC):
    @abstractmethod
    async def handle(self, command: RefreshTokenCommand) -> tuple[str, str]:
        """Return (new_access_token, new_refresh_token)."""
        ...
