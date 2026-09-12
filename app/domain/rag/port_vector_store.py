from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.domain.rag.entity_chunk import Chunk

class VectorStore(ABC):
    @abstractmethod
    def add(self, chunks: List[Chunk]) -> None:
        pass
