"""
auth_handler.py — Telegram Bot Kimlik Doğrulama Handler'ı.

Admin botuna sadece kayıtlı işletme sahipleri erişebilir.
Müşteri botuna herkes erişebilir.
"""

import logging
from functools import wraps
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_IDS

logger = logging.getLogger(__name__)


def admin_required(func: Callable):
    """
    Admin bot handler'ları için dekoratör.
    Sadece ADMIN_USER_IDS listesindeki kullanıcılar erişebilir.

    ADMIN_USER_IDS boşsa, ilk /start yapan kullanıcı otomatik admin olur
    (demo kolaylığı için).
    """

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return

        # Admin listesi boşsa (demo modu): herkese izin ver ama uyar
        if not ADMIN_USER_IDS:
            logger.warning(
                "TELEGRAM_ADMIN_USER_IDS boş — demo modunda herkes admin. "
                "Üretim ortamında .env'ye admin ID'lerini ekleyin."
            )
            return await func(update, context, *args, **kwargs)

        if user.id not in ADMIN_USER_IDS:
            await update.message.reply_text(
                "⛔ Bu bota erişim yetkiniz yok.\n\n"
                "Bu bot sadece kayıtlı işletme sahipleri tarafından kullanılabilir.\n"
                "Telegram User ID'niz: `{}`\n\n"
                "İşletme sahibiyseniz, sistem yöneticisinden ID'nizi eklemesini isteyin.".format(user.id),
                parse_mode="Markdown",
            )
            logger.warning("Unauthorized admin access attempt by user %d (%s)", user.id, user.full_name)
            return

        return await func(update, context, *args, **kwargs)

    return wrapper


async def get_user_info(update: Update) -> dict:
    """Telegram kullanıcı bilgisini sözlük olarak döner."""
    user = update.effective_user
    if not user:
        return {}
    return {
        "telegram_id": user.id,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "full_name": user.full_name or "",
        "username": user.username or "",
        "language_code": user.language_code or "tr",
    }
