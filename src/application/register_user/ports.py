"""IUserUnitOfWork — application-level port used by auth use cases.

Extends AbstractUnitOfWork with the repositories / stores that the
auth flow needs so handlers remain fully infrastructure-agnostic.
"""

from abc import ABC

from src.application.shared.refresh_token_store import AbstractRefreshTokenStore
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.user.repository import IUserRepository


class IUserUnitOfWork(AbstractUnitOfWork, ABC):
    users: IUserRepository
    refresh_tokens: AbstractRefreshTokenStore
