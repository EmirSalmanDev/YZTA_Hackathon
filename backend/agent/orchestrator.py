"""
orchestrator.py — KOBİ Pilot AI Agent Orchestrator
LangGraph ReAct agent powered by Gemini.
Handles both customer-facing and admin-facing conversations.
"""

from __future__ import annotations

import logging
import os
from enum import Enum
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from agent.tools import ADMIN_TOOLS, CUSTOMER_TOOLS
from agent.memory import load_memory, save_message

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


CUSTOMER_SYSTEM_PROMPT = """Sen KOBİ Pilot'un müşteri destek asistanısın.
Adın "Pilot". Yardımcı, nazik ve profesyonelsin.

Müşterilere şu konularda yardım edersin:
- Sipariş durumu sorgulama
- Kargo takibi
- Ürün stok bilgisi
- Genel sorular

KURALLAR:
- Her zaman Türkçe yanıt ver.
- Kısa, net ve dostane ol.
- Müşterinin sipariş/takip numarasını bilmiyorsan kibarca sor.
- Stok değiştirme veya sipariş iptal etme gibi admin işlemleri yapma.
- Yapamayacağın bir işlem varsa kibarca açıkla ve işletmeyle iletişime geçmelerini öner."""

ADMIN_SYSTEM_PROMPT = """Sen KOBİ Pilot'un işletme yönetim asistanısın.
İşletme sahibine kapsamlı destek sağlarsın.

Yardım ettiğin konular:
- Sipariş yönetimi ve durum güncelleme
- Stok kontrolü ve kritik stok uyarıları
- Kargo takibi
- Günlük özet ve iş istatistikleri
- Tedarikçi e-postası taslağı hazırlama
- Müşteri bildirim mesajı oluşturma

KURALLAR:
- Her zaman Türkçe yanıt ver.
- Net ve bilgilendirici ol; rakamları ve detayları göster.
- Kritik stok veya bekleyen sipariş varsa proaktif olarak uyar.
- Önemli değişiklikleri (iptal, durum güncelleme) gerçekleştirmeden önce teyit et."""


class KobiAgentOrchestrator:
    """
    Main orchestrator for KOBİ Pilot.
    Uses LangGraph create_react_agent for both customer and admin roles.
    """

    def __init__(self) -> None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")

        self._llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.3,
        )

        self._customer_agent = create_react_agent(
            model=self._llm,
            tools=CUSTOMER_TOOLS,
            prompt=CUSTOMER_SYSTEM_PROMPT,
        )
        self._admin_agent = create_react_agent(
            model=self._llm,
            tools=ADMIN_TOOLS,
            prompt=ADMIN_SYSTEM_PROMPT,
        )

    def run(
        self,
        message: str,
        customer_id: int,
        channel: str = "web",
        role: AgentRole = AgentRole.CUSTOMER,
    ) -> str:
        """Process a message and return the agent's response."""
        # Load history before saving the new message so it does not appear twice.
        # SystemMessages are filtered out — the agent's own prompt already handles that.
        history = [
            m for m in load_memory(customer_id, channel)
            if not isinstance(m, SystemMessage)
        ]

        agent = self._admin_agent if role == AgentRole.ADMIN else self._customer_agent

        try:
            result = agent.invoke({
                "messages": history + [HumanMessage(content=message)]
            })
            last_msg = result["messages"][-1]
            response: str = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        except Exception as exc:
            logging.exception(exc)
            response = f"Üzgünüm, isteğinizi işlerken bir sorun oluştu: {exc}"

        # Persist both turns only after a successful (or gracefully failed) invoke.
        save_message(customer_id, channel, "human", message)
        save_message(customer_id, channel, "ai", response)
        return response


_orchestrator: Optional[KobiAgentOrchestrator] = None


def get_orchestrator() -> KobiAgentOrchestrator:
    """Return the singleton orchestrator, initialising it on first call."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = KobiAgentOrchestrator()
    return _orchestrator
