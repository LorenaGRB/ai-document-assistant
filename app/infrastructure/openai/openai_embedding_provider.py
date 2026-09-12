from openai import OpenAI
from app.domain.rag.port_embedding import Embedding

class OpenAIEmbeddingProvider(Embedding):
    def __init__(self):
        self._client = OpenAI()

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding