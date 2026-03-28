from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.conversation.repository import IConversationRepository
from src.domain.message.repository import IMessageRepository


class IMessagingUnitOfWork(AbstractUnitOfWork, ABC):
    conversations: IConversationRepository
    messages: IMessageRepository
