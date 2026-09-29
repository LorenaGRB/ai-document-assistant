from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    document_id: str
    chunk_index: int
    score: float
    document_filename: str