from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.conversation.repository import IConversationRepository


class IConversationUnitOfWork(AbstractUnitOfWork, ABC):
    conversations: IConversationRepository
