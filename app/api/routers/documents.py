from fastapi import APIRouter, HTTPException, UploadFile
from app.application.document.service_upload_document import UploadDocumentService
from app.infrastructure.supabase.supabase_document_storage import SupabaseDocumentStorage
from app.infrastructure.supabase.supabase_document_repository import SupabaseDocumentRepository
from app.api.schemas.document import DocumentResponse

router = APIRouter()

ALLOWED_TYPES = ["application/pdf", "text/plain"]

@router.post("/documents")
async def upload_document(file: UploadFile) -> DocumentResponse:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and text files are allowed")

    file_bytes = await file.read()

    service = UploadDocumentService(
        storage=SupabaseDocumentStorage(),
        repository=SupabaseDocumentRepository()
    )

    document = service.execute(file.filename, file_bytes, file.content_type)
    return DocumentResponse(**document.__dict__)