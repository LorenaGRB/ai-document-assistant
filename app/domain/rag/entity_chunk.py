
from dataclasses import dataclass, field
import uuid


@dataclass(frozen=True)
class Chunk:
    text: str
    vector: list[float]
    document_id: str
    chunk_index: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))