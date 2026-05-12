"""
memory.py — Conversation memory management for KOBİ Pilot Agent
Stores per-customer/per-channel message history in DB + in-memory cache.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from sqlmodel import Session, select

from database.connection import get_session
from database.models import Channel, Conversation

# memory.py — dosyanın en üstüne ekle
import re

_SKIP_AI_PATTERNS = [
    r'\d+\s*kg',
    r'\d+\s*adet',
    r'\d+\s*ton',
    r'stoğunuz\s+\d+',
    r'stok.*\d+',
    r'sipariş.*#\d+',
]

def _should_skip_ai_message(content: str) -> bool:
    for pattern in _SKIP_AI_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def save_message(
    customer_id: int,
    channel: str,
    role: str,
    content: str,
    window: int = 20,
) -> None:
    # ← YENİ: stok/miktar içeren AI cevaplarını memory'e yazma
    if role == "ai" and _should_skip_ai_message(content):
        return

    key = _cache_key(customer_id, channel)
    # ... geri kalan kod tamamen aynı kalıyor

# In-memory cache: { "{customer_id}:{channel}" -> list[BaseMessage] }
_memory_cache: dict[str, list[BaseMessage]] = {}


def _to_channel(channel: str) -> Channel:
    try:
        return Channel(channel)
    except ValueError:
        return Channel.web


def _cache_key(customer_id: int, channel: str) -> str:
    return f"{customer_id}:{channel}"


# Public API

def load_memory(customer_id: int, channel: str) -> list[BaseMessage]:
    """Load conversation history for a customer+channel pair."""
    key = _cache_key(customer_id, channel)
    if key in _memory_cache:
        return _memory_cache[key]

    # Try to hydrate from DB
    ch = _to_channel(channel)
    with get_session() as session:
        conv = session.exec(
            select(Conversation)
            .where(Conversation.customer_id == customer_id)
            .where(Conversation.channel == ch)
        ).first()

    if conv and conv.last_message:
        try:
            raw: list[dict] = json.loads(conv.last_message)
            messages = _deserialize_messages(raw)
        except Exception:
            messages = []
    else:
        messages = []

    _memory_cache[key] = messages
    return messages


def save_message(
    customer_id: int,
    channel: str,
    role: str,          # "human" | "ai" | "system"
    content: str,
    window: int = 20,   # keep last N messages
) -> None:
    """Append a message to memory and persist summary to DB."""
    key = _cache_key(customer_id, channel)
    messages = _memory_cache.get(key, [])

    msg = _make_message(role, content)
    messages.append(msg)

    # Trim to window
    if len(messages) > window:
        messages = messages[-window:]

    _memory_cache[key] = messages

    # Persist serialized history to DB
    serialized = json.dumps(_serialize_messages(messages))
    ch = _to_channel(channel)
    with get_session() as session:
        conv = session.exec(
            select(Conversation)
            .where(Conversation.customer_id == customer_id)
            .where(Conversation.channel == ch)
        ).first()

        if conv:
            conv.last_message = serialized
            conv.updated_at = datetime.utcnow()
            session.add(conv)
        else:
            conv = Conversation(
                customer_id=customer_id,
                channel=ch,
                last_message=serialized,
                updated_at=datetime.utcnow(),
            )
            session.add(conv)
        session.commit()


def clear_memory(customer_id: int, channel: str) -> None:
    """Clear conversation memory (e.g. on session end)."""
    key = _cache_key(customer_id, channel)
    _memory_cache.pop(key, None)


def get_langchain_memory(
    customer_id: int,
    channel: str,
    window: int = 10,
) -> list[BaseMessage]:
    """Return conversation history as a list of LangChain messages."""
    history = load_memory(customer_id, channel)
    return history[-window:]


# Serialization helpers

def _serialize_messages(messages: list[BaseMessage]) -> list[dict]:
    out = []
    for m in messages:
        if isinstance(m, HumanMessage):
            out.append({"role": "human", "content": m.content})
        elif isinstance(m, AIMessage):
            out.append({"role": "ai", "content": m.content})
        elif isinstance(m, SystemMessage):
            out.append({"role": "system", "content": m.content})
    return out


def _deserialize_messages(raw: list[dict]) -> list[BaseMessage]:
    messages = []
    for item in raw:
        role = item.get("role")
        content = item.get("content", "")
        messages.append(_make_message(role, content))
    return messages


def _make_message(role: str, content: str) -> BaseMessage:
    if role == "human":
        return HumanMessage(content=content)
    elif role == "ai":
        return AIMessage(content=content)
    else:
        return SystemMessage(content=content)