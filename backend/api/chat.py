from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from database.connection import get_session
from database.models import Channel, Conversation

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    customer_id: int
    channel: Channel


class ChatResponse(BaseModel):
    reply: str
    agent_used_tool: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
) -> ChatResponse:
    # Upsert conversation record so the dashboard always shows the latest message
    conv = session.exec(
        select(Conversation).where(
            Conversation.customer_id == request.customer_id,
            Conversation.channel == request.channel,
        )
    ).first()
    if conv:
        conv.last_message = request.message
        conv.updated_at = datetime.utcnow()
    else:
        conv = Conversation(
            customer_id=request.customer_id,
            channel=request.channel,
            last_message=request.message,
        )
    session.add(conv)
    session.commit()

    # --- Agent call placeholder — teammate plugs in here ---
    reply: str = ""
    agent_used_tool: str = ""
    # -------------------------------------------------------

    return ChatResponse(reply=reply, agent_used_tool=agent_used_tool)


if __name__ == "__main__":
    print("smoke ok")
