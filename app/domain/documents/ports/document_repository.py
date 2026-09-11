from abc import ABC, abstractmethod

class DocumentRepository(ABC):
    @abstractmethod
    def save(self,filename: str, storage_path: str) -> dict:
        ...