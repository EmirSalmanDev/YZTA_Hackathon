"""
chat.py — FastAPI endpoint for the KOBİ Pilot Web Chat Agent
POST /api/chat       — Customer chat
POST /api/chat/admin — Admin/owner chat
GET  /api/chat/history/{customer_id} — Fetch message history
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlmodel import select

from agent.orchestrator import get_orchestrator, AgentRole
from agent.memory import load_memory, clear_memory
from database.connection import get_session
from database.models import Customer

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    customer_id: int = Field(..., description="Customer ID from database")
    channel: str = Field(default="web", description="Channel: web | whatsapp | dashboard")
    session_id: Optional[str] = Field(default=None, description="Optional session identifier")


class AdminChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    admin_id: int = Field(default=1, description="Admin/owner identifier")
    channel: str = Field(default="dashboard")


class ChatResponse(BaseModel):
    response: str
    customer_id: int
    channel: str
    timestamp: str
    status: str = "ok"


class HistoryMessage(BaseModel):
    role: str   # "human" | "ai" | "system"
    content: str


class HistoryResponse(BaseModel):
    customer_id: int
    channel: str
    messages: list[HistoryMessage]
    count: int


# ---------------------------------------------------------------------------
# Helper: validate customer exists
# ---------------------------------------------------------------------------

def _require_customer(customer_id: int) -> Customer:
    with get_session() as session:
        customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer #{customer_id} not found.")
    return customer


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=ChatResponse, summary="Customer chat endpoint")
async def customer_chat(req: ChatRequest):
    """
    Main customer-facing chat endpoint.
    Accepts a message, runs it through the KOBİ Pilot customer agent, returns response.
    """
    _require_customer(req.customer_id)

    orchestrator = get_orchestrator()

    response_text = orchestrator.run(
        message=req.message,
        customer_id=req.customer_id,
        channel=req.channel,
        role=AgentRole.CUSTOMER,
    )

    return ChatResponse(
        response=response_text,
        customer_id=req.customer_id,
        channel=req.channel,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.post("/admin", response_model=ChatResponse, summary="Admin/owner chat endpoint")
async def admin_chat(req: AdminChatRequest):
    """
    Business owner dashboard chat endpoint.
    Has access to all tools including order updates, stats, notifications, etc.
    """
    orchestrator = get_orchestrator()

    response_text = orchestrator.run(
        message=req.message,
        customer_id=req.admin_id,
        channel=req.channel,
        role=AgentRole.ADMIN,
    )

    return ChatResponse(
        response=response_text,
        customer_id=req.admin_id,
        channel=req.channel,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get(
    "/history/{customer_id}",
    response_model=HistoryResponse,
    summary="Get conversation history",
)
async def get_history(customer_id: int, channel: str = "web"):
    """
    Retrieve the conversation history for a customer on a given channel.
    Useful for the dashboard to display previous messages.
    """
    _require_customer(customer_id)

    messages = load_memory(customer_id, channel)

    from langchain.schema import HumanMessage, AIMessage, SystemMessage

    history = []
    for m in messages:
        if isinstance(m, HumanMessage):
            history.append(HistoryMessage(role="human", content=m.content))
        elif isinstance(m, AIMessage):
            history.append(HistoryMessage(role="ai", content=m.content))
        elif isinstance(m, SystemMessage):
            history.append(HistoryMessage(role="system", content=m.content))

    return HistoryResponse(
        customer_id=customer_id,
        channel=channel,
        messages=history,
        count=len(history),
    )


@router.delete(
    "/history/{customer_id}",
    summary="Clear conversation history",
)
async def clear_history(customer_id: int, channel: str = "web"):
    """Clear the conversation memory for a customer (e.g. start new session)."""
    _require_customer(customer_id)
    clear_memory(customer_id, channel)
    return {"message": f"Memory cleared for customer #{customer_id} on channel '{channel}'.", "status": "ok"}


@router.get("/health", summary="Agent health check")
async def health():
    """Check that the agent orchestrator is initializable."""
    try:
        get_orchestrator()
        return {"status": "ok", "agent": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Agent not ready: {str(e)}")