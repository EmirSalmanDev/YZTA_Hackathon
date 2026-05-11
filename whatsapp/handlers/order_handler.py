"""
order_handler.py — Sipariş Handler'ları (Müşteri Bot İçin).

Müşterilerin sipariş durumu sorgulaması.
"""

import logging
import re

from telegram import Update
from telegram.ext import ContextTypes

import api_client

logger = logging.getLogger(__name__)


async def order_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /siparis <sipariş_no> komutu.
    Müşterinin belirli bir siparişinin durumunu sorgular.
    """
    if not context.args:
        await update.message.reply_text(
            "📦 Sipariş sorgulamak için sipariş numaranızı belirtin:\n\n"
            "Örnek: `/siparis 42`",
            parse_mode="Markdown",
        )
        return

    order_input = " ".join(context.args)

    # Sipariş numarasını ayıkla
    match = re.search(r"\d+", order_input)
    if not match:
        await update.message.reply_text(
            "❌ Geçerli bir sipariş numarası giriniz.\n"
            "Örnek: `/siparis 42`",
            parse_mode="Markdown",
        )
        return

    order_id = match.group()

    await update.message.reply_text("⏳ Sipariş bilgisi sorgulanıyor...")

    # AI agent üzerinden sorgula — doğal dil yanıtı için
    # customer_id olarak 1 kullanılıyor (demo); gerçekte telegram_user_id → customer_id eşleştirmesi lazım
    reply = await api_client.customer_chat(
        f"Sipariş #{order_id}'in durumu nedir?",
        customer_id=1,
        channel="telegram",
    )
    await update.message.reply_text(reply, parse_mode="Markdown")
