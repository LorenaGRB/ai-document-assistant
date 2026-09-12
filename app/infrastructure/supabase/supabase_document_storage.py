from app.infrastructure.supabase.supabase_client import get_supabase_client
from app.domain.documents.port_document_storage import DocumentStorage

class SupabaseDocumentStorage(DocumentStorage):
    def __init__(self):
        self._client = get_supabase_client()
        self._bucket = "AI_DOCUMENT_ASSISTANT"

    def upload_document(self, file_path: str, file_bytes: bytes, content_type: str) -> str:
        client = self._client                      # the already-authenticated Supabase client
        storage_api = client.storage                # the Storage sub-API within the client
        bucket = storage_api.from_(self._bucket)    # reference to your specific bucket
        bucket.upload(file_path, file_bytes, file_options={"content-type": content_type})  # uploads the bytes to that path
        return file_path