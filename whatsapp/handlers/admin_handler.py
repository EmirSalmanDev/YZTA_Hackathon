"""
admin_handler.py — Admin Bot Komut ve Mesaj Handler'ları.

İşletme sahibi için:
- /start — Hoşgeldin + ana menü
- /stok — Kritik stok özeti
- /siparisler — Bekleyen siparişler
- /ozet — Günlük iş özeti
- /yardim — Komut listesi
- Doğal dil mesajlar → Admin AI Agent
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from handlers.auth_handler import admin_required
from utils.keyboards import admin_main_menu
import api_client

logger = logging.getLogger(__name__)


@admin_required
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin bot /start komutu."""
    user = update.effective_user
    name = user.first_name if user else "Admin"

    await update.message.reply_text(
        f"Merhaba, {name}! 🌿\n\n"
        f"Ben KoopPilot Admin Asistanınız. İşletmenizi yönetmenize yardımcı olabilirim.\n\n"
        f"**Yapabileceklerim:**\n"
        f"📦 Stok yönetimi (ekle, güncelle, sorgula)\n"
        f"🛒 Sipariş takibi ve yönetimi\n"
        f"📊 İş istatistikleri ve raporlar\n"
        f"🚚 Kargo takibi\n\n"
        f"Doğal dil ile mesaj yazabilirsiniz. Örneğin:\n"
        f"_\"100 kilo domates stoğu ekle\"_\n"
        f"_\"Bugünkü sipariş özeti ver\"_\n\n"
        f"Veya aşağıdaki menüyü kullanabilirsiniz:",
        reply_markup=admin_main_menu(),
        parse_mode="Markdown",
    )


@admin_required
async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stok komutu — kritik stok uyarıları."""
    await update.message.reply_text("⏳ Stok durumu kontrol ediliyor...")
    summary = await api_client.get_stock_summary()
    await update.message.reply_text(summary, parse_mode="Markdown")


@admin_required
async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/siparisler komutu — bekleyen siparişler."""
    await update.message.reply_text("⏳ Bekleyen siparişler yükleniyor...")
    summary = await api_client.get_orders_summary()
    await update.message.reply_text(summary, parse_mode="Markdown")


@admin_required
async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ozet komutu — günlük iş özeti (AI agent üzerinden)."""
    await update.message.reply_text("⏳ Günlük özet hazırlanıyor...")
    reply = await api_client.admin_chat("Bugünkü detaylı iş özetini hazırla.")
    await update.message.reply_text(reply, parse_mode="Markdown")


@admin_required
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/yardim komutu — komut listesi."""
    await update.message.reply_text(
        "📖 **KoopPilot Admin Bot Komutları:**\n\n"
        "/start — Bot'u başlat, ana menü\n"
        "/stok — Kritik stok uyarıları\n"
        "/siparisler — Bekleyen siparişler\n"
        "/ozet — Günlük iş özeti\n"
        "/yardim — Bu yardım mesajı\n\n"
        "**Doğal dil komutlar:**\n"
        "• _\"Domates stok durumu nedir?\"_\n"
        "• _\"100 kg domates stoğu ekle\"_\n"
        "• _\"Sipariş #42'nin durumunu göster\"_\n"
        "• _\"Bugünkü satış özeti\"_\n"
        "• _\"Kritik stokları göster\"_\n"
        "• _\"Geciken kargoları listele\"_\n",
        parse_mode="Markdown",
    )


@admin_required
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Doğal dil mesajları AI agent'a iletir.
    Kullanıcının yazdığı her mesaj admin agent tarafından işlenir.
    """
    text = update.message.text
    if not text:
        return

    logger.info("Admin message from %s: %s", update.effective_user.id, text[:100])

    await update.message.reply_text("🤔 İsteğiniz işleniyor...")

    reply = await api_client.admin_chat(text)
    await update.message.reply_text(reply, parse_mode="Markdown")


@admin_required
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline keyboard callback handler."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "admin_stock":
        summary = await api_client.get_stock_summary()
        await query.edit_message_text(summary, parse_mode="Markdown", reply_markup=admin_main_menu())

    elif data == "admin_orders":
        summary = await api_client.get_orders_summary()
        await query.edit_message_text(summary, parse_mode="Markdown", reply_markup=admin_main_menu())

    elif data == "admin_summary":
        await query.edit_message_text("⏳ Günlük özet hazırlanıyor...", reply_markup=None)
        reply = await api_client.admin_chat("Bugünkü detaylı iş özetini hazırla.")
        await query.message.reply_text(reply, parse_mode="Markdown", reply_markup=admin_main_menu())

    elif data == "admin_cargo":
        reply = await api_client.admin_chat("Geciken kargoları listele.")
        await query.edit_message_text(reply, parse_mode="Markdown", reply_markup=admin_main_menu())

    elif data == "admin_help":
        await query.edit_message_text(
            "📖 **KoopPilot Admin Bot Komutları:**\n\n"
            "/start — Bot'u başlat, ana menü\n"
            "/stok — Kritik stok uyarıları\n"
            "/siparisler — Bekleyen siparişler\n"
            "/ozet — Günlük iş özeti\n"
            "/yardim — Yardım menüsü\n\n"
            "**Doğal dil komutlar da kullanabilirsiniz.**",
            parse_mode="Markdown",
            reply_markup=admin_main_menu(),
        )

    # Sipariş durumu güncelleme callback'leri
    elif data.startswith("order_confirm_"):
        order_id = data.split("_")[-1]
        reply = await api_client.admin_chat(f"Sipariş #{order_id}'yi onayla.")
        await query.edit_message_text(reply, parse_mode="Markdown")

    elif data.startswith("order_ship_"):
        order_id = data.split("_")[-1]
        reply = await api_client.admin_chat(f"Sipariş #{order_id}'yi kargola.")
        await query.edit_message_text(reply, parse_mode="Markdown")

    elif data.startswith("order_cancel_"):
        order_id = data.split("_")[-1]
        reply = await api_client.admin_chat(f"Sipariş #{order_id}'yi iptal et.")
        await query.edit_message_text(reply, parse_mode="Markdown")

    elif data.startswith("order_detail_"):
        order_id = data.split("_")[-1]
        reply = await api_client.admin_chat(f"Sipariş #{order_id}'nin detaylarını göster.")
        await query.edit_message_text(reply, parse_mode="Markdown")

    else:
        await query.edit_message_text("Bilinmeyen komut.", reply_markup=admin_main_menu())
