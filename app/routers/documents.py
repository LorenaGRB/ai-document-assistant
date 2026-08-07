from fastapi import APIRouter, UploadFile

router = APIRouter()

@router.post("/documents")
async def upload_document(file: UploadFile):
    return {"filename": file.filename, "status": "uploaded successfully"}