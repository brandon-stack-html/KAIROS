from src.application.delete_message.command import DeleteMessageCommand
from src.application.send_message.ports import IMessagingUnitOfWork
from src.domain.message.errors import MessageNotFoundError, MessageNotOwnedError
from src.domain.shared.message_id import MessageId
from src.domain.user.user import UserId


class DeleteMessageHandler:
    def __init__(self, uow: IMessagingUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: DeleteMessageCommand) -> None:
        async with self._uow:
            message_id = MessageId.from_str(command.message_id)
            message = await self._uow.messages.find_by_id(message_id)
            if message is None:
                raise MessageNotFoundError(command.message_id)

            if message.sender_id != UserId(command.requester_id):
                raise MessageNotOwnedError()

            await self._uow.messages.delete(message_id)
