from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # TODO: forward to agent orchestrator
    return ChatResponse(reply="", session_id=request.session_id)


if __name__ == "__main__":
    print("smoke ok")
