from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatRequest
from app.application.chat.service import ChatService
from app.infrastructure.llm.anthropic_client import AnthropicLLMClient

router = APIRouter()


def get_chat_service() -> ChatService:
    return ChatService(llm_client=AnthropicLLMClient())


@router.post("/chat")
async def chat(request: ChatRequest):
    chat_service = get_chat_service()
    return StreamingResponse(
        chat_service.send_message(request.message), media_type="text/event-stream"
    )
