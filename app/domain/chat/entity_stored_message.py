from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from app.domain.chat.entity_message import Message


class MessageStatus(str, Enum):
    NEW = "new"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass(frozen=True)
class StoredMessage: 
    message_id: str
    conversation_id: str
    message: Message
    created_at: datetime
    status: MessageStatus
