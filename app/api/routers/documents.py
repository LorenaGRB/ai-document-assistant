from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile
from app.application.document.service_upload_document import UploadDocumentService
from app.application.rag.service_process_document import ProcessDocumentService
from app.infrastructure.supabase.supabase_document_storage import SupabaseDocumentStorage
from app.infrastructure.supabase.supabase_document_repository import SupabaseDocumentRepository
from app.infrastructure.extractors.extractor_factory import get_extractor
from app.infrastructure.openai.openai_embedding_provider import OpenAIEmbeddingProvider
from app.infrastructure.pinecone.pinecone_client import get_pinecone_index
from app.infrastructure.pinecone.pinecone_vector_store import PineconeVectorStore
from app.api.schemas.document import DocumentResponse

router = APIRouter()

ALLOWED_TYPES = ["application/pdf", "text/plain"]

def process_document(document_id: str, file_bytes: bytes, content_type: str) -> None:
    service = ProcessDocumentService(
        extractor=get_extractor(content_type),
        embedding=OpenAIEmbeddingProvider(),
        vector_store=PineconeVectorStore(get_pinecone_index()),
         repository=SupabaseDocumentRepository(),
    )
    service.execute(file_bytes, document_id)

@router.post("/documents")
async def upload_document(file: UploadFile, background_tasks: BackgroundTasks) -> DocumentResponse:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and text files are allowed")

    file_bytes = await file.read()

    service = UploadDocumentService(
        storage=SupabaseDocumentStorage(),
        repository=SupabaseDocumentRepository()
    )

    document = service.execute(file.filename, file_bytes, file.content_type)
    background_tasks.add_task(process_document, document.id, file_bytes, file.content_type)

    return DocumentResponse(**document.__dict__)