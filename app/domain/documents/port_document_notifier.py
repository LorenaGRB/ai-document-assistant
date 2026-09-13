from abc import ABC, abstractmethod

class DocumentNotifier(ABC):
    @abstractmethod
    def notify(self, document_id: str, status: str) -> None:
        ...

    @abstractmethod
    async def subscribe(self, document_id: str):
        ...