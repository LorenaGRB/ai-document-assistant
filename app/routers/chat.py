from anthropic import Anthropic
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest

router = APIRouter()
client = Anthropic()

def generate(message: str):
    with client.messages.stream(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": message}],
    ) as stream:
        for text in stream.text_stream:
            yield text

@router.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(generate(request.message),media_type="text/event-stream")