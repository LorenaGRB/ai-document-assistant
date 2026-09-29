from typing import Iterator

from app.application.service_retrieval import RetrievalService
from app.domain.chat.entity_message import Message, Role
from app.domain.chat.port_llm_client import LLMClient


class ChatService:
    def __init__(self, llm_client: LLMClient, retrieval_service: RetrievalService):
        self._llm_client = llm_client
        self._retrieval_service = retrieval_service
    def send_message(self, text: str) -> Iterator[str]:
        chunks = self._retrieval_service.retrieve(text)
        rag_content = "\n".join([f"[{chunk.document_filename}, chunk {chunk.chunk_index}] {chunk.text}" for chunk in chunks])
        messages = [Message(role=Role.USER, content=text)]
        return self._llm_client.stream_reply(messages, rag_content)
