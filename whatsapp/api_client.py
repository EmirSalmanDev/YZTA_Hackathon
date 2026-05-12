"""
api_client.py — KoopPilot Telegram Bot Backend API İstemcisi.

Telegram bot'ları bu modül üzerinden backend'e istek atar.
Dashboard'daki api_client.py ile aynı mantıkta çalışır.
"""

import logging
from typing import Any

import httpx

from config import BACKEND_URL, MAX_MESSAGE_LENGTH

logger = logging.getLogger(__name__)

_TIMEOUT = 60.0  # Chat endpoint'leri uzun sürebilir (LLM çağrısı)


def _url(path: str) -> str:
    return f"{BACKEND_URL}{path}"


# ---------------------------------------------------------------------------
# AI Sohbet
# ---------------------------------------------------------------------------

async def admin_chat(message: str, admin_id: int = 1) -> str:
    """Admin agent'a mesaj gönderir, yanıt metnini döner."""
    message = message[:MAX_MESSAGE_LENGTH]
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(_url("/api/chat/admin"), json={
                "message": message,
                "admin_id": admin_id,
                "channel": "telegram",
            })
            if r.status_code == 200:
                data = r.json()
                return data.get("response", "Yanıt alınamadı.")
            else:
                logger.error("Admin chat failed: HTTP %d — %s", r.status_code, r.text[:200])
                return "Üzgünüm, isteğinizi işlerken bir hata oluştu."
    except httpx.ConnectError:
        logger.error("Backend bağlantısı kurulamadı: %s", BACKEND_URL)
        return "⚠️ Backend bağlantısı kurulamadı. Lütfen sistem yöneticisine bildirin."
    except Exception as e:
        logger.exception("admin_chat exception")
        return f"Bir hata oluştu: {e}"


async def customer_chat(message: str, customer_id: int, channel: str = "telegram") -> str:
    """Müşteri agent'a mesaj gönderir, yanıt metnini döner."""
    message = message[:MAX_MESSAGE_LENGTH]
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(_url("/api/chat"), json={
                "message": message,
                "customer_id": customer_id,
                "channel": channel,
            })
            if r.status_code == 200:
                data = r.json()
                return data.get("response", "Yanıt alınamadı.")
            elif r.status_code == 404:
                return "Müşteri kaydınız bulunamadı. Lütfen sipariş numaranızı belirtin."
            else:
                logger.error("Customer chat failed: HTTP %d — %s", r.status_code, r.text[:200])
                return "Üzgünüm, isteğinizi işlerken bir hata oluştu."
    except httpx.ConnectError:
        logger.error("Backend bağlantısı kurulamadı: %s", BACKEND_URL)
        return "⚠️ Sistem şu an yanıt veremiyor. Lütfen daha sonra tekrar deneyin."
    except Exception as e:
        logger.exception("customer_chat exception")
        return f"Bir hata oluştu: {e}"


# ---------------------------------------------------------------------------
# Stok Sorgulama (Doğrudan API — hızlı yanıt için)
# ---------------------------------------------------------------------------

async def get_stock_summary() -> str:
    """Stok özeti metin olarak döner."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(_url("/stock/critical"))
            if r.status_code == 200:
                critical = r.json()
                if not critical:
                    return "✅ Tüm ürünler normal stok seviyesinde."

                lines = ["⚠️ **Kritik Stok Uyarıları:**\n"]
                for p in critical[:10]:
                    lines.append(
                        f"• {p['name']}: {p['stock_amount']} {p.get('unit', '')} "
                        f"(Eşik: {p['critical_threshold']})"
                    )
                return "\n".join(lines)
            return "Stok bilgisi alınamadı."
    except Exception as e:
        logger.exception("get_stock_summary failed")
        return f"Stok bilgisi alınırken hata: {e}"


async def get_orders_summary() -> str:
    """Bekleyen sipariş özeti döner."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(_url("/orders"), params={"status": "pending"})
            if r.status_code == 200:
                orders = r.json()
                if not orders:
                    return "✅ Bekleyen sipariş yok."

                total = sum(o.get("total_price", 0) for o in orders)
                lines = [f"📦 **{len(orders)} Bekleyen Sipariş** (Toplam: ₺{total:,.0f})\n"]
                for o in orders[:10]:
                    lines.append(
                        f"• #{o['id']} — ₺{o['total_price']:,.0f} "
                        f"({o.get('created_at', '')[:10]})"
                    )
                if len(orders) > 10:
                    lines.append(f"\n... ve {len(orders) - 10} sipariş daha.")
                return "\n".join(lines)
            return "Sipariş bilgisi alınamadı."
    except Exception as e:
        logger.exception("get_orders_summary failed")
        return f"Sipariş bilgisi alınırken hata: {e}"


async def get_product_list() -> str:
    """Ürün listesini metin olarak döner (müşteri botu için)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(_url("/stock"))
            if r.status_code == 200:
                products = r.json()
                if not products:
                    return "📭 Şu an satışta ürün bulunmuyor."

                lines = ["🛒 **Ürün Listesi:**\n"]
                for p in products:
                    status = "✅" if p.get("stock_amount", 0) > 0 else "❌ Tükendi"
                    lines.append(
                        f"• {p['name']} — ₺{p.get('price', 0):,.2f}/{p.get('unit', 'adet')} {status}"
                    )
                return "\n".join(lines)
            return "Ürün listesi alınamadı."
    except Exception as e:
        logger.exception("get_product_list failed")
        return f"Ürün listesi alınırken hata: {e}"


async def track_cargo_by_id(tracking_id: str) -> str:
    """Kargo takip sonucunu metin olarak döner."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(_url(f"/cargo/track/{tracking_id}"))
            if r.status_code == 200:
                data = r.json()
                return (
                    f"📦 **Kargo Takip: {tracking_id}**\n\n"
                    f"🚚 Firma: {data.get('carrier', '—')}\n"
                    f"📍 Durum: {data.get('status', '—')}\n"
                    f"📍 Konum: {data.get('location', '—')}\n"
                    f"📅 Tahmini Teslimat: {data.get('estimated_delivery', '—')}"
                )
            return f"❌ '{tracking_id}' takip numaralı kargo bulunamadı."
    except Exception as e:
        logger.exception("track_cargo_by_id failed")
        return f"Kargo takip sırasında hata: {e}"


async def health_check() -> bool:
    """Backend sağlık kontrolü."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(_url("/health"))
            return r.status_code == 200
    except Exception:
        return False
