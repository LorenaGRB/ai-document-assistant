from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Document:
    id: str
    filename: str
    storage_path: str
    status: str
    created_at: datetime