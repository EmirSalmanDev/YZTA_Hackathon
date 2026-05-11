"""
stock_handler.py — Stok Sorgulama Handler'ı (Müşteri Bot İçin).

Müşterilerin ürün listesi ve stok durumu sorgulaması.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

import api_client

logger = logging.getLogger(__name__)


async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /urunler komutu.
    Satıştaki tüm ürünlerin listesini gösterir.
    """
    await update.message.reply_text("⏳ Ürün listesi yükleniyor...")
    product_list = await api_client.get_product_list()
    await update.message.reply_text(product_list, parse_mode="Markdown")


async def stock_query_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /stok <ürün_adı> komutu.
    Belirli bir ürünün stok durumunu sorgular.
    """
    if not context.args:
        await update.message.reply_text(
            "🛒 Ürün stok durumunu sorgulamak için ürün adını belirtin:\n\n"
            "Örnek: `/stok domates`",
            parse_mode="Markdown",
        )
        return

    product_name = " ".join(context.args)
    await update.message.reply_text(f"⏳ '{product_name}' stok durumu sorgulanıyor...")

    reply = await api_client.customer_chat(
        f"{product_name} stok durumu nedir?",
        customer_id=1,
        channel="telegram",
    )
    await update.message.reply_text(reply, parse_mode="Markdown")
