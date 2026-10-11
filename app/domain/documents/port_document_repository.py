from abc import ABC, abstractmethod
from app.domain.documents.entity_document import Document

class DocumentRepository(ABC):
    @abstractmethod
    def exists_by_filename(self, filename: str) -> bool:
        ...
    
    @abstractmethod
    def save(self,filename: str, storage_path: str) -> dict:
        ...

    @abstractmethod
    def update_status(self, document_id: str, status: str) -> dict:
        ...

    @abstractmethod
    def list_all(self) -> list[Document]:
        ...
