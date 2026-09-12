from typing import Iterator

from anthropic import Anthropic

from app.domain.chat.entity_message import Message
from app.domain.chat.port_llm_client import LLMClient


class AnthropicLLMClient(LLMClient):
    def __init__(self, model: str = "claude-sonnet-5", max_tokens: int = 1024):
        self._client = Anthropic()
        self._model = model
        self._max_tokens = max_tokens

    def stream_reply(self, messages: list[Message]) -> Iterator[str]:
        anthropic_messages = [
            {"role": message.role.value, "content": message.content}
            for message in messages
        ]
        with self._client.messages.stream(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=anthropic_messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
