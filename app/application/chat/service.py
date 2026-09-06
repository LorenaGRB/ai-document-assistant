from typing import Iterator

from app.domain.chat.entities import Message, Role
from app.domain.chat.ports import LLMClient


class ChatService:
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def send_message(self, text: str) -> Iterator[str]:
        messages = [Message(role=Role.USER, content=text)]
        return self._llm_client.stream_reply(messages)
