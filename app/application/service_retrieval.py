from typing import List

from app.domain.rag.port_embedding import Embedding
from app.domain.rag.port_vector_store import VectorStore
from app.domain.rag.entity_retrieved_chunk import RetrievedChunk


class RetrievalService:
    def __init__(self, embedding: Embedding, vector_store: VectorStore, min_score: float = 0.3, top_k: int = 5):
        self._embedding = embedding
        self._vector_store = vector_store
        self._min_score = min_score
        self._top_k = top_k

    def retrieve(self, question: str) -> List[RetrievedChunk]:
        query_vector = self._embedding.embed(question)
        matches = self._vector_store.search(query_vector, self._top_k)
        return [
            match for match in matches 
            if match.score >= self._min_score
        ]