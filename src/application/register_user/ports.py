"""IUserUnitOfWork — application-level port used by RegisterUserHandler.

Extends AbstractUnitOfWork with the users repository so that
the handler can remain fully infrastructure-agnostic.
"""
from abc import ABC, abstractmethod

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.user.repository import IUserRepository


class IUserUnitOfWork(AbstractUnitOfWork, ABC):
    users: IUserRepository
