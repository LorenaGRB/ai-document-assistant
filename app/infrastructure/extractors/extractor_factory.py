from app.infrastructure.extractors.pdf_extractor import PdfExtractor
from app.infrastructure.extractors.text_extractor import TextExtractor
from app.domain.documents.port_document_extractor import DocumentExtractor


def get_extractor(content_type: str) -> DocumentExtractor:
    if content_type == "application/pdf":
        return PdfExtractor()
    return TextExtractor()