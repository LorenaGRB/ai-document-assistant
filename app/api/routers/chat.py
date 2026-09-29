from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatRequest
from app.application.service_chat import ChatService
from app.application.service_retrieval import RetrievalService
from app.infrastructure.anthropic.anthropic_client import AnthropicLLMClient
from app.infrastructure.openai.openai_embedding_provider import OpenAIEmbeddingProvider
from app.infrastructure.pinecone.pinecone_vector_store import PineconeVectorStore
from app.infrastructure.pinecone.pinecone_client import get_pinecone_index
from functools import lru_cache


router = APIRouter()

@lru_cache #to implement singleton pattern for the chat service
def get_chat_service() -> ChatService:
    return ChatService(llm_client=AnthropicLLMClient(), retrieval_service=RetrievalService(embedding=OpenAIEmbeddingProvider(),vector_store=PineconeVectorStore(get_pinecone_index())) )


@router.post("/chat")
async def chat(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    return StreamingResponse(
        chat_service.send_message(request.message), media_type="text/event-stream"
    )
