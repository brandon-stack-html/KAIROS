from src.application.send_message.command import SendMessageCommand
from src.application.send_message.ports import IMessagingUnitOfWork
from src.domain.conversation.errors import ConversationNotFoundError
from src.domain.message.message import Message
from src.domain.shared.conversation_id import ConversationId
from src.domain.user.user import UserId


class SendMessageHandler:
    def __init__(self, uow: IMessagingUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: SendMessageCommand) -> Message:
        async with self._uow:
            conversation_id = ConversationId.from_str(command.conversation_id)
            conversation = await self._uow.conversations.find_by_id(conversation_id)
            if conversation is None:
                raise ConversationNotFoundError(command.conversation_id)

            message = Message.create(
                conversation_id=conversation_id,
                sender_id=UserId(command.sender_id),
                content=command.content,
            )
            await self._uow.messages.save(message)

        return message
