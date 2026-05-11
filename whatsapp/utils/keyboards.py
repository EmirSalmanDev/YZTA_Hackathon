"""
keyboards.py — Telegram Inline Klavye Tanımları.

Admin ve müşteri botları için önceden hazırlanmış inline klavyeler.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ---------------------------------------------------------------------------
# Admin Bot Klavyeleri
# ---------------------------------------------------------------------------

def admin_main_menu() -> InlineKeyboardMarkup:
    """Admin ana menü klavyesi."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Stok Durumu", callback_data="admin_stock"),
            InlineKeyboardButton("🛒 Siparişler", callback_data="admin_orders"),
        ],
        [
            InlineKeyboardButton("📊 Günlük Özet", callback_data="admin_summary"),
            InlineKeyboardButton("🚚 Kargo Durumu", callback_data="admin_cargo"),
        ],
        [
            InlineKeyboardButton("❓ Yardım", callback_data="admin_help"),
        ],
    ])


def admin_order_actions(order_id: int) -> InlineKeyboardMarkup:
    """Sipariş işlem klavyesi."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Onayla", callback_data=f"order_confirm_{order_id}"),
            InlineKeyboardButton("🚚 Kargola", callback_data=f"order_ship_{order_id}"),
        ],
        [
            InlineKeyboardButton("📋 Detay", callback_data=f"order_detail_{order_id}"),
            InlineKeyboardButton("❌ İptal", callback_data=f"order_cancel_{order_id}"),
        ],
    ])


def admin_stock_actions(product_id: int) -> InlineKeyboardMarkup:
    """Stok işlem klavyesi."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Stok Güncelle", callback_data=f"stock_update_{product_id}"),
            InlineKeyboardButton("📊 Detay", callback_data=f"stock_detail_{product_id}"),
        ],
    ])


# ---------------------------------------------------------------------------
# Müşteri Bot Klavyeleri
# ---------------------------------------------------------------------------

def customer_main_menu() -> InlineKeyboardMarkup:
    """Müşteri ana menü klavyesi."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Sipariş Sorgula", callback_data="customer_order"),
            InlineKeyboardButton("🚚 Kargo Takip", callback_data="customer_cargo"),
        ],
        [
            InlineKeyboardButton("🛒 Ürünleri Gör", callback_data="customer_products"),
            InlineKeyboardButton("❓ Yardım", callback_data="customer_help"),
        ],
    ])


def customer_order_prompt() -> InlineKeyboardMarkup:
    """Sipariş no girişi için yönlendirme."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="customer_start")],
    ])
