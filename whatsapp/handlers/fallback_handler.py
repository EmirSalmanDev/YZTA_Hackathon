"""
fallback_handler.py — Bilinmeyen komut / hata handler'ı.

Tanınmayan komutlar ve genel hata durumları için handler.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bilinmeyen komutlara yanıt verir."""
    await update.message.reply_text(
        "❓ Bu komutu tanıyamadım.\n\n"
        "Kullanılabilir komutlar için /yardim yazın.",
        parse_mode="Markdown",
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global hata handler'ı — loglar ve kullanıcıya bildirir."""
    logger.error("Bot exception: %s", context.error, exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ İsteğiniz işlenirken bir hata oluştu.\n"
            "Lütfen daha sonra tekrar deneyin."
        )
