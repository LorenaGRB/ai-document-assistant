from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.domain.rag.entity_chunk import Chunk
from app.domain.rag.entity_retrieved_chunk import RetrievedChunk

class VectorStore(ABC):
    @abstractmethod
    def add(self, chunks: List[Chunk]) -> None:
        pass
    @abstractmethod
    def search(self, query_vector: List[float], top_k: int=5) -> List[RetrievedChunk]:
        pass