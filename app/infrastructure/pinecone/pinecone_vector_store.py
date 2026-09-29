from typing import List
from app.domain.rag.entity_chunk import Chunk
from app.domain.rag.entity_retrieved_chunk import RetrievedChunk
from app.domain.rag.port_vector_store import VectorStore


class PineconeVectorStore(VectorStore):
    def __init__(self, pinecone_index):
        self._pinecone_index = pinecone_index

    def add(self, chunks: List[Chunk]) -> None:
        vectors = [
            {
                "id": chunk.id,
                "values": chunk.vector,
                "metadata": {"text": chunk.text, "document_id": chunk.document_id, "chunk_index": chunk.chunk_index, "document_filename": chunk.document_filename},
            }
            for chunk in chunks
        ]
        self._pinecone_index.upsert(vectors=vectors)

    def search(self, query_vector: List[float], top_k: int=5) -> List[RetrievedChunk]:
        response = self._pinecone_index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        return [
            RetrievedChunk(
                text=match.metadata["text"],
                document_id=match.metadata["document_id"],
                chunk_index=int(match.metadata["chunk_index"]),
                score=match.score,
                document_filename=match.metadata["document_filename"]
            )
            for match in response.matches
        ]