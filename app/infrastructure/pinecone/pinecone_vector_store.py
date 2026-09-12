from typing import List
from app.domain.rag.entity_chunk import Chunk
from app.domain.rag.port_vector_store import VectorStore


class PineconeVectorStore(VectorStore):
    def __init__(self, pinecone_index):
        self._pinecone_index = pinecone_index

    def add(self, chunks: List[Chunk]) -> None:
        vectors = [
            {
                "id": chunk.id,
                "values": chunk.vector,
                "metadata": {"text": chunk.text, "document_id": chunk.document_id},
            }
            for chunk in chunks
        ]
        self._pinecone_index.upsert(vectors=vectors)