from abc import ABC, abstractmethod

from app.domain.chat.entity_message import Message
from app.domain.chat.entity_stored_message import MessageStatus, StoredMessage


class MessageRepository(ABC):
    @abstractmethod
    def save_question(self, question: Message, conversation_id: str) -> StoredMessage:
        ...

    @abstractmethod
    def update_status(self, message_id: str, status: MessageStatus) -> StoredMessage:
        ...

    @abstractmethod
    def read_history_by_conversation_id(self, conversation_id: str) -> list[StoredMessage]:
        ...

    @abstractmethod
    def complete_exchange(self, question: StoredMessage, response: Message) -> StoredMessage:
        ...