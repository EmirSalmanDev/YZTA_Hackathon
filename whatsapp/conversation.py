"""
conversation.py — Telegram Bot Konuşma Yönetimi.

Rate limiting ve konuşma state yönetimi.
"""

import time
from collections import defaultdict
from typing import Optional

from config import MIN_MESSAGE_INTERVAL

# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------

_last_message_time: dict[int, float] = defaultdict(float)


def check_rate_limit(user_id: int) -> bool:
    """
    Kullanıcının mesaj gönderme sıklığını kontrol eder.
    True: mesaj gönderilebilir.
    False: çok hızlı — beklemesi gerekir.
    """
    now = time.time()
    last = _last_message_time[user_id]

    if now - last < MIN_MESSAGE_INTERVAL:
        return False

    _last_message_time[user_id] = now
    return True


# ---------------------------------------------------------------------------
# Konuşma State
# ---------------------------------------------------------------------------

_conversation_state: dict[int, dict] = {}


def get_state(user_id: int) -> dict:
    """Kullanıcının konuşma state'ini döner."""
    if user_id not in _conversation_state:
        _conversation_state[user_id] = {
            "customer_id": None,
            "awaiting_input": None,
            "context": {},
        }
    return _conversation_state[user_id]


def set_customer_id(user_id: int, customer_id: int) -> None:
    """Telegram user_id → customer_id eşleştirmesini kaydet."""
    state = get_state(user_id)
    state["customer_id"] = customer_id


def get_customer_id(user_id: int) -> Optional[int]:
    """Eşleştirilmiş customer_id döner."""
    return get_state(user_id).get("customer_id")


def clear_state(user_id: int) -> None:
    """Konuşma state'ini temizle."""
    _conversation_state.pop(user_id, None)
