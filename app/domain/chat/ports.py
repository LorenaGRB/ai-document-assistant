from abc import ABC, abstractmethod
from typing import Iterator

from app.domain.chat.entities import Message


class LLMClient(ABC):
    @abstractmethod
    def stream_reply(self, messages: list[Message]) -> Iterator[str]:
        ...
