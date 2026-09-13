from app.domain.documents.port_document_storage import DocumentStorage
from app.domain.documents.port_document_repository import DocumentRepository

class UploadDocumentService:
    def __init__(self, storage: DocumentStorage, repository: DocumentRepository):
        self._storage = storage
        self._repository = repository

    def execute(self, filename: str, file_bytes: bytes, content_type: str) -> dict:
        storage_path = self._storage.upload_document(filename, file_bytes, content_type)
        return self._repository.save(filename, storage_path)