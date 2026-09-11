from abc import ABC, abstractmethod

class DocumentStorage(ABC):
    @abstractmethod
    def upload_document(self, document: bytes, filename: str, content_type: str) -> str:
        ...

