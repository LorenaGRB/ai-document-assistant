from app.domain.documents.port_document_extractor import DocumentExtractor
from app.domain.documents.port_document_notifier import DocumentNotifier
from app.domain.documents.port_document_repository import DocumentRepository
from app.domain.rag.port_embedding import Embedding
from app.domain.rag.port_vector_store import VectorStore
from app.domain.rag.entity_chunk import Chunk
from app.domain.rag.service_chunking import chunk
import logging

logger = logging.getLogger(__name__)

class ProcessDocumentService:
    def __init__(self, extractor: DocumentExtractor, embedding: Embedding, vector_store: VectorStore, repository: DocumentRepository,
                 notifier: DocumentNotifier):
        self._extractor = extractor
        self._embedding = embedding
        self._vector_store = vector_store
        self._repository = repository
        self._notifier = notifier

    def execute(self, file_bytes: bytes, document_id: str) -> None:
        try:
            text = self._extractor.extract(file_bytes)
            chunked_list = chunk(text, chunk_size=2000, overlap=200)

            chunks = [
                Chunk(
                    text=chunked_text,
                    vector=self._embedding.embed(chunked_text),
                    document_id=document_id,
                    chunk_index=index
                )
                for index, chunked_text in enumerate(chunked_list)
            ]

            self._vector_store.add(chunks)
            self._repository.update_status(document_id, "processed")
            self._notifier.notify(document_id, "processed")
        except Exception as e:
            logger.error(f"Error occurred while processing document {document_id}: {e}")
            self._repository.update_status(document_id, "failed")
            self._notifier.notify(document_id, "failed")