from typing import Iterator

from app.domain.chat.entity_message import Message, Role
from app.domain.chat.port_llm_client import LLMClient


class ChatService:
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def send_message(self, text: str) -> Iterator[str]:
        messages = [Message(role=Role.USER, content=text)]
        return self._llm_client.stream_reply(messages)
