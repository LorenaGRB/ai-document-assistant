from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    created_at: datetime