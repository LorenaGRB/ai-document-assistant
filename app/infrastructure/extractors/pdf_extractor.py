from app.domain.documents.port_document_extractor import DocumentExtractor
from pypdf import PdfReader
from io import BytesIO

class PdfExtractor(DocumentExtractor):
    def extract(self, file_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text(extraction_mode="layout")
        return text