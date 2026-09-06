from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatRequest
from app.application.chat.service import ChatService
from app.infrastructure.llm.anthropic_client import AnthropicLLMClient
from functools import lru_cache


router = APIRouter()

@lru_cache #to implement singleton pattern for the chat service
def get_chat_service() -> ChatService:
    return ChatService(llm_client=AnthropicLLMClient())


@router.post("/chat")
async def chat(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    return StreamingResponse(
        chat_service.send_message(request.message), media_type="text/event-stream"
    )
