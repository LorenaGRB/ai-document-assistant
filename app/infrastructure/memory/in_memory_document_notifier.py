import asyncio
from collections import defaultdict
from functools import lru_cache
from app.domain.documents.port_document_notifier import DocumentNotifier

class InMemoryDocumentNotifier(DocumentNotifier):
    def __init__(self):
        self._queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    def notify(self, document_id: str, status: str) -> None:
        self._queues[document_id].put_nowait(status)

    async def subscribe(self, document_id: str):
        queue = self._queues[document_id]
        status = await queue.get()
        yield status
        
@lru_cache
def get_document_notifier() -> DocumentNotifier:
    return InMemoryDocumentNotifier()