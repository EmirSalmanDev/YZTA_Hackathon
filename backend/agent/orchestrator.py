"""
orchestrator.py — KOBİ Pilot AI Agent Orchestrator
LangChain ReAct agent powered by Gemini Pro.
Handles both customer-facing and admin-facing conversations.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool

from agent.tools import ALL_TOOLS, CUSTOMER_TOOLS, ADMIN_TOOLS
from agent.memory import get_langchain_memory, save_message


# Agent Roles

class AgentRole(str, Enum):
    CUSTOMER = "customer"   # Web chat / WhatsApp customer support
    ADMIN = "admin"         # Dashboard — business owner


# System prompts

CUSTOMER_SYSTEM_PROMPT = """Sen KOBİ Pilot'un müşteri destek asistanısın. 
Adın "Pilot". Yardımcı, nazik ve profesyonelsin.

Müşterilere şu konularda yardım edersin:
- Sipariş durumu sorgulama
- Kargo takibi
- Ürün stok bilgisi
- Genel sorular

KURALLLAR:
- Her zaman Türkçe yanıt ver.
- Kısa, net ve dostane ol.
- Müşterinin sipariş/takip numarasını bilmiyorsan kibarca sor.
- Stok değiştirme veya sipariş iptal etme gibi admin işlemleri yapma.
- Yapamayacağın bir işlem varsa kibarca açıkla ve işletmeyle iletişime geçmelerini öner.

Mevcut araçlar:
{tools}

Araç isimleri: {tool_names}

Sohbet geçmişi:
{chat_history}

Kullanıcı mesajı: {input}

Düşünce süreci:
{agent_scratchpad}"""

ADMIN_SYSTEM_PROMPT = """Sen KOBİ Pilot'un işletme yönetim asistanısın.
İşletme sahibine kapsamlı destek sağlarsın.

Yardım ettiğin konular:
- Sipariş yönetimi ve durum güncelleme
- Stok kontrolü ve kritik stok uyarıları
- Kargo takibi
- Müşteri arama
- Günlük özet ve iş istatistikleri
- Tedarikçi e-postası taslağı hazırlama
- Müşteri bildirim mesajı oluşturma

KURALLAR:
- Her zaman Türkçe yanıt ver.
- Net ve bilgilendirici ol; rakamları ve detayları göster.
- Kritik stok veya bekleyen sipariş varsa proaktif olarak uyar.
- İşlemleri gerçekleştirmeden önce önemli değişiklikleri (iptal, durum güncelleme) teyit et.

Mevcut araçlar:
{tools}

Araç isimleri: {tool_names}

Sohbet geçmişi:
{chat_history}

Kullanıcı mesajı: {input}

Düşünce süreci:
{agent_scratchpad}"""


# Orchestrator class

class KobiAgentOrchestrator:
    """
    Main orchestrator for KOBİ Pilot.
    Creates and manages LangChain ReAct agents for customer and admin roles.
    """

    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")

        self._llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3,
            convert_system_message_to_human=True,  # Gemini requirement
        )

        self._customer_agent = self._build_agent(
            tools=CUSTOMER_TOOLS,
            system_prompt=CUSTOMER_SYSTEM_PROMPT,
        )
        self._admin_agent = self._build_agent(
            tools=ADMIN_TOOLS,
            system_prompt=ADMIN_SYSTEM_PROMPT,
        )

    # Public

    def run(
        self,
        message: str,
        customer_id: int,
        channel: str = "web",
        role: AgentRole = AgentRole.CUSTOMER,
    ) -> str:
        """
        Process a message and return the agent's response.
        Automatically handles memory load/save.
        """
        # Save incoming human message
        save_message(customer_id, channel, "human", message)

        # Load LangChain memory
        memory = get_langchain_memory(customer_id, channel)

        # Select agent
        agent_executor = (
            self._admin_agent if role == AgentRole.ADMIN else self._customer_agent
        )

        try:
            result = agent_executor.invoke({
                "input": message,
                "chat_history": memory.load_memory_variables({})["chat_history"],
            })
            response = result.get("output", "Bir hata oluştu, lütfen tekrar deneyin.")
        except Exception as e:
            response = f"Üzgünüm, isteğinizi işlerken bir sorun oluştu: {str(e)}"

        # Save AI response to memory
        save_message(customer_id, channel, "ai", response)

        return response

    # Private

    def _build_agent(
        self,
        tools: list[BaseTool],
        system_prompt: str,
    ) -> AgentExecutor:
        prompt = PromptTemplate.from_template(system_prompt)

        agent = create_react_agent(
            llm=self._llm,
            tools=tools,
            prompt=prompt,
        )

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,           # Set False in production
            max_iterations=8,
            handle_parsing_errors=True,
            return_intermediate_steps=False,
        )


# Module-level singleton (lazy init)

_orchestrator: Optional[KobiAgentOrchestrator] = None


def get_orchestrator() -> KobiAgentOrchestrator:
    """Return the singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = KobiAgentOrchestrator()
    return _orchestrator