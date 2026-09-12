from app.domain.documents.port_document_extractor import DocumentExtractor
from app.domain.rag.port_embedding import Embedding
from app.domain.rag.port_vector_store import VectorStore
from app.domain.rag.entity_chunk import Chunk
from app.domain.rag.service_chunking import chunk


class ProcessDocumentService:
    def __init__(self, extractor: DocumentExtractor, embedding: Embedding, vector_store: VectorStore):
        self._extractor = extractor
        self._embedding = embedding
        self._vector_store = vector_store

    def execute(self, file_bytes: bytes, document_id: str) -> None:
        text = self._extractor.extract(file_bytes)
        chunked_list = chunk(text, chunk_size=500, overlap=50)

        chunks = [
            Chunk(
                text=chunk,
                vector=self._embedding.embed(chunk),
                document_id=document_id,
            )
            for chunk in chunked_list
        ]

        self._vector_store.add(chunks)