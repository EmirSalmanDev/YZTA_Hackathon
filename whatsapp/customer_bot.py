"""
customer_bot.py — KoopPilot Müşteri Telegram Botu.

Müşteriler için self-servis bot:
- Sipariş durumu sorgulama
- Kargo takip
- Ürün listesi ve stok durumu
- Doğal dil ile soru sorma

Güvenlik: Herkese açık — giriş gerektirmez.
"""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import CUSTOMER_BOT_TOKEN
from handlers.order_handler import order_status_command
from handlers.stock_handler import products_command, stock_query_command
from handlers.fallback_handler import error_handler, unknown_command
from utils.keyboards import customer_main_menu
import api_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Müşteri Bot Handler'ları
# ---------------------------------------------------------------------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Müşteri bot /start komutu."""
    user = update.effective_user
    name = user.first_name if user else "Değerli Müşterimiz"

    await update.message.reply_text(
        f"Merhaba, {name}! 🌿\n\n"
        f"Ben KoopPilot müşteri asistanıyım. Size yardımcı olabileceğim konular:\n\n"
        f"📦 **Sipariş Durumu** — Siparişinizin nerede olduğunu öğrenin\n"
        f"🚚 **Kargo Takip** — Kargonuzun durumunu sorgulayın\n"
        f"🛒 **Ürün Listesi** — Satıştaki ürünleri görüntüleyin\n\n"
        f"Doğrudan mesaj yazabilirsiniz. Örneğin:\n"
        f"_\"Sipariş #42 nerede?\"_\n"
        f"_\"Hangi ürünler satışta?\"_\n\n"
        f"Veya aşağıdaki menüyü kullanın:",
        reply_markup=customer_main_menu(),
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/yardim komutu."""
    await update.message.reply_text(
        "📖 **Kullanılabilir Komutlar:**\n\n"
        "/start — Bot'u başlat, ana menü\n"
        "/siparis `<no>` — Sipariş durumu sorgula\n"
        "/kargo `<takip_no>` — Kargo takip\n"
        "/urunler — Ürün listesi\n"
        "/stok `<ürün>` — Ürün stok durumu\n"
        "/yardim — Bu yardım mesajı\n\n"
        "**Doğal dil sorular da sorabilirsiniz:**\n"
        "• _\"Siparişim nerede?\"_\n"
        "• _\"Domates var mı?\"_\n"
        "• _\"Kargom ne zaman gelecek?\"_",
        parse_mode="Markdown",
    )


async def cargo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/kargo <takip_no> komutu."""
    if not context.args:
        await update.message.reply_text(
            "🚚 Kargo takip için takip numaranızı belirtin:\n\n"
            "Örnek: `/kargo TRK-123456`",
            parse_mode="Markdown",
        )
        return

    tracking_id = context.args[0]
    await update.message.reply_text("⏳ Kargo durumu sorgulanıyor...")
    result = await api_client.track_cargo_by_id(tracking_id)
    await update.message.reply_text(result, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Doğal dil mesajları müşteri agent'a iletir.
    """
    text = update.message.text
    if not text:
        return

    logger.info("Customer message from %s: %s", update.effective_user.id, text[:100])

    await update.message.reply_text("🤔 Sorunuz işleniyor...")

    # Demo: customer_id=1 kullanılıyor
    # Gerçekte: telegram_user_id → customer_id eşleştirmesi yapılmalı (bkz. info.py)
    reply = await api_client.customer_chat(
        text,
        customer_id=1,
        channel="telegram",
    )
    await update.message.reply_text(reply, parse_mode="Markdown")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline keyboard callback handler."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "customer_start":
        await query.edit_message_text(
            "🌿 Ana menüye dönüldü. Aşağıdaki seçeneklerden birini kullanın:",
            reply_markup=customer_main_menu(),
        )

    elif data == "customer_order":
        await query.edit_message_text(
            "📦 Sipariş numaranızı yazın.\n\n"
            "Örnek: `/siparis 42`\n\n"
            "Veya doğrudan _\"Sipariş #42 nerede?\"_ diye sorabilirsiniz.",
            parse_mode="Markdown",
        )

    elif data == "customer_cargo":
        await query.edit_message_text(
            "🚚 Kargo takip numaranızı yazın.\n\n"
            "Örnek: `/kargo TRK-123456`",
            parse_mode="Markdown",
        )

    elif data == "customer_products":
        product_list = await api_client.get_product_list()
        await query.edit_message_text(
            product_list,
            parse_mode="Markdown",
            reply_markup=customer_main_menu(),
        )

    elif data == "customer_help":
        await query.edit_message_text(
            "📖 **Komutlar:**\n\n"
            "/siparis `<no>` — Sipariş sorgula\n"
            "/kargo `<takip_no>` — Kargo takip\n"
            "/urunler — Ürün listesi\n"
            "/yardim — Yardım\n\n"
            "Veya doğrudan mesaj yazın!",
            parse_mode="Markdown",
            reply_markup=customer_main_menu(),
        )

    else:
        await query.edit_message_text(
            "Bilinmeyen seçenek.",
            reply_markup=customer_main_menu(),
        )


# ---------------------------------------------------------------------------
# Bot Oluşturma
# ---------------------------------------------------------------------------

def create_customer_bot() -> Application:
    """Müşteri bot Application nesnesini oluşturur."""
    if not CUSTOMER_BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_CUSTOMER_BOT_TOKEN ayarlanmamış. "
            ".env dosyasına veya dashboard Telegram Bot sayfasından token girin."
        )

    app = Application.builder().token(CUSTOMER_BOT_TOKEN).build()

    # Komut handler'ları
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("siparis", order_status_command))
    app.add_handler(CommandHandler("kargo", cargo_command))
    app.add_handler(CommandHandler("urunler", products_command))
    app.add_handler(CommandHandler("stok", stock_query_command))
    app.add_handler(CommandHandler("yardim", help_command))
    app.add_handler(CommandHandler("help", help_command))

    # Inline keyboard callback
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Doğal dil mesaj handler (catch-all)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Bilinmeyen komut
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Hata handler
    app.add_error_handler(error_handler)

    logger.info("Müşteri bot oluşturuldu ve handler'lar eklendi.")
    return app


def run_customer_bot() -> None:
    """Müşteri bot'u başlatır (polling mode)."""
    logger.info("Müşteri bot başlatılıyor...")
    app = create_customer_bot()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    run_customer_bot()
