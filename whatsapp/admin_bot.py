"""
admin_bot.py — KoopPilot Admin Telegram Botu.

İşletme sahibi için tam yetkili yönetim botu.
Doğal dil konuşma akışında stok yönetimi, sipariş takibi,
istatistik sorgulama gibi işlemleri yapar.

Güvenlik: Sadece TELEGRAM_ADMIN_USER_IDS listesindeki kullanıcılar erişebilir.
"""

import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import ADMIN_BOT_TOKEN
from handlers.admin_handler import (
    handle_callback,
    handle_message,
    help_command,
    orders_command,
    start_command,
    stock_command,
    summary_command,
)
from handlers.fallback_handler import error_handler, unknown_command

logger = logging.getLogger(__name__)


def create_admin_bot() -> Application:
    """Admin bot Application nesnesini oluşturur ve handler'ları ekler."""
    if not ADMIN_BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_ADMIN_BOT_TOKEN ayarlanmamış. "
            ".env dosyasına veya dashboard Telegram Bot sayfasından token girin."
        )

    app = Application.builder().token(ADMIN_BOT_TOKEN).build()

    # Komut handler'ları
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stok", stock_command))
    app.add_handler(CommandHandler("siparisler", orders_command))
    app.add_handler(CommandHandler("ozet", summary_command))
    app.add_handler(CommandHandler("yardim", help_command))
    app.add_handler(CommandHandler("help", help_command))

    # Inline keyboard callback handler
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Doğal dil mesaj handler'ı (en son eklenmeli — catch-all)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Bilinmeyen komut handler'ı
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Global hata handler
    app.add_error_handler(error_handler)

    logger.info("Admin bot oluşturuldu ve handler'lar eklendi.")
    return app


def run_admin_bot() -> None:
    """Admin bot'u başlatır (polling mode)."""
    logger.info("Admin bot başlatılıyor...")
    app = create_admin_bot()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    run_admin_bot()
