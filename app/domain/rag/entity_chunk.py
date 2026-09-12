
from dataclasses import dataclass, field
import uuid


@dataclass(frozen=True)
class Chunk:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    vector: list[float]