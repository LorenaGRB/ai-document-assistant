from app.domain.documents.port_document_extractor import DocumentExtractor

class TextExtractor(DocumentExtractor):
    def extract(self, file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8")