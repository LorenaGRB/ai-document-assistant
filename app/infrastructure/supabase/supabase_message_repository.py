# infrastructure/supabase/supabase_message_repository.py

from datetime import datetime

from app.domain.chat.entity_message import Message, Role
from app.domain.chat.entity_stored_message import MessageStatus, StoredMessage
from app.domain.chat.port_message_repository import MessageRepository
from app.infrastructure.supabase.supabase_client import get_supabase_client


class SupabaseMessageRepository(MessageRepository):
    def __init__(self):
        self._client = get_supabase_client()

    def save_question(self, question: Message, conversation_id: str) -> StoredMessage:
        response = self._client.table("messages").insert({
            "conversation_id": conversation_id,
            "role": question.role.value,
            "content": question.content,
        }).execute()
        return self._to_stored_message(response.data[0])

    def update_status(self, message_id: str, status: MessageStatus) -> StoredMessage:
        response = self._client.table("messages").update({
            "status": status.value,
        }).eq("id", message_id).execute()
        if not response.data:
            raise ValueError(f"Message '{message_id}' not found")
        return self._to_stored_message(response.data[0])

    def read_history_by_conversation_id(self, conversation_id: str) -> list[StoredMessage]:
        response = (
            self._client.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .eq("status", MessageStatus.COMPLETED.value)
            .order("created_at", desc=False)
            .execute()
        )
        return [self._to_stored_message(row) for row in response.data]

    def complete_exchange(self, question: StoredMessage, response: Message) -> StoredMessage:
        result = self._client.rpc("complete_exchange", {
            "p_question_id": question.message_id,
            "p_conversation_id": question.conversation_id,
            "p_content": response.content,
        }).execute()
        # A function that returns one row may come back as an object or as a one-item list.
        row = result.data[0] if isinstance(result.data, list) else result.data
        return self._to_stored_message(row)

    @staticmethod
    def _to_stored_message(row: dict) -> StoredMessage:
        return StoredMessage(
            message_id=row["id"],
            conversation_id=row["conversation_id"],
            message=Message(role=Role(row["role"]), content=row["content"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            status=MessageStatus(row["status"]),
        )