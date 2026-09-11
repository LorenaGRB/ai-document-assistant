# infrastructure/supabase/supabase_document_repository.py

from app.domain.documents.entities import Document
from app.domain.documents.ports.document_repository import DocumentRepository
from app.infrastructure.supabase.supabase_client import get_supabase_client

class SupabaseDocumentRepository(DocumentRepository):
    def __init__(self):
        self._client = get_supabase_client()

   
    def save(self, filename: str, storage_path: str) -> Document:
        response = self._client.table("documents").insert({
            "filename": filename,
            "storage_path": storage_path,
            "status": "processing"
        }).execute()
        row = response.data[0]
        return Document(
            id=row["id"],
            filename=row["filename"],
            storage_path=row["storage_path"],
            status=row["status"],
            created_at=row["created_at"]
        )