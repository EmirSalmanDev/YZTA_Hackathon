"""
notify_tools.py — LangChain tools for notifications and email drafting
"""

from __future__ import annotations
import json
import re
import logging
from datetime import date
from langchain.tools import tool
from sqlmodel import select
from database.connection import get_session
from database.models import Product, Order, Customer

logger = logging.getLogger(__name__)


def _parse_int(val, name="değer"):
    match = re.search(r'\d+', str(val))
    if not match:
        raise ValueError(f"Geçerli bir {name} girin.")
    return int(match.group())


@tool
def draft_supplier_email(product_name: str, quantity_needed: str, supplier_name: str = "Tedarikçi") -> str:
    """
    Draft a professional restock request email to a supplier.
    Use this when stock is critically low and the owner wants to order more inventory.
    Returns a ready-to-send email draft in Turkish.
    """
    try:
        qty = _parse_int(quantity_needed, "miktar")
    except ValueError:
        qty = 0

    try:
        with get_session() as session:
            all_products = session.exec(select(Product)).all()
            products_data = [
                {"name": p.name, "stock_amount": p.stock_amount, "critical_threshold": p.critical_threshold, "unit": p.unit}
                for p in all_products
            ]
        product = next((p for p in products_data if product_name.lower() in p["name"].lower()), None)
    except Exception:
        logger.exception("draft_supplier_email DB lookup failed")
        product = None

    today = date.today().strftime("%d.%m.%Y")
    unit = product["unit"] if product else "adet"
    stock_info = (
        f"Mevcut stok: {product['stock_amount']} {product['unit']} "
        f"(Kritik eşik: {product['critical_threshold']} {product['unit']})"
    ) if product else ""

    body = f"""Konu: Acil Stok Yenileme Talebi — {product_name}

Sayın {supplier_name} Yetkilileri,

İşletmemizde "{product_name}" ürününün stoğu kritik seviyeye düşmüştür.
{stock_info}

Sipariş detayları:
- Ürün: {product_name}
- Miktar: {qty} {unit}
- Tahmini Teslimat: En kısa sürede (tercihen 2-3 iş günü)

Talebimizin öncelikli değerlendirilmesini rica ederiz.

Tarih: {today}
Saygılarımızla,
KOBİ Pilot"""

    return json.dumps({
        "subject": f"Acil Stok Yenileme Talebi — {product_name}",
        "to": supplier_name,
        "body": body.strip(),
    }, ensure_ascii=False)


@tool
def draft_customer_notification(order_id: str, message_type: str) -> str:
    """
    Draft a WhatsApp/SMS notification for a customer about their order.
    message_type: 'shipped' | 'delivered' | 'delayed' | 'confirmed' | 'cancelled'
    """
    valid_types = {"shipped", "delivered", "delayed", "confirmed", "cancelled"}
    if message_type not in valid_types:
        return json.dumps({"error": f"Geçersiz message_type. Seçenekler: {valid_types}"})

    try:
        oid = _parse_int(order_id, "sipariş numarası")
        with get_session() as session:
            order = session.get(Order, oid)
            if not order:
                return json.dumps({"error": f"Sipariş #{oid} bulunamadı."})
            customer = session.get(Customer, order.customer_id)

            result = {
                "order_id": oid,
                "customer_name": customer.name if customer else "Bilinmiyor",
                "customer_phone": customer.phone if customer else None,
                "whatsapp_number": customer.whatsapp_number if customer else None,
                "total_price": float(order.total_price),
                "cargo_tracking_id": order.cargo_tracking_id,
                "delivery_date": str(order.delivery_date) if order.delivery_date else "belirtilmedi",
                "first_name": customer.name.split()[0] if customer else "Müşteri",
            }

        templates = {
            "confirmed": f"Merhaba {result['first_name']}! #{oid} siparişiniz onaylandı. Toplam: {result['total_price']:.2f}TL.",
            "shipped":   f"Merhaba {result['first_name']}! #{oid} siparişiniz kargoya verildi. Takip: {result['cargo_tracking_id'] or '-'}. Tahmini teslimat: {result['delivery_date']}.",
            "delivered": f"Merhaba {result['first_name']}! #{oid} siparişiniz teslim edildi.",
            "delayed":   f"Merhaba {result['first_name']}. #{oid} siparişiniz gecikti. Yeni tahmini teslimat: {result['delivery_date']}.",
            "cancelled": f"Merhaba {result['first_name']}. #{oid} siparişiniz iptal edildi. İade 3-5 is günü içinde yapılacaktır.",
        }

        result["message_type"] = message_type
        result["message"] = templates[message_type]
        result.pop("first_name")
        return json.dumps(result, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception:
        logger.exception("draft_customer_notification failed")
        return json.dumps({"error": "Bildirim hazırlanırken bir hata oluştu."})


@tool
def generate_daily_summary(dummy: str = "") -> str:
    """
    Generate a comprehensive daily business summary.
    Use this for the automated daily report or when the owner asks for an overview.
    Action Input olarak bos string gir.
    """
    today = date.today()
    try:
        with get_session() as session:
            all_orders = session.exec(select(Order)).all()
            all_products = session.exec(select(Product)).all()
            all_customers = session.exec(select(Customer)).all()

            orders_data = [
                {"status": o.status, "total_price": float(o.total_price), "created_at": o.created_at}
                for o in all_orders
            ]
            products_data = [
                {"name": p.name, "stock_amount": p.stock_amount, "critical_threshold": p.critical_threshold, "unit": p.unit}
                for p in all_products
            ]
            customer_count = len(all_customers)

        today_orders = [o for o in orders_data if o["created_at"] and o["created_at"].date() == today]
        status_counts: dict[str, int] = {}
        for o in orders_data:
            status_counts[o["status"]] = status_counts.get(o["status"], 0) + 1

        critical_stock = [p for p in products_data if p["stock_amount"] <= p["critical_threshold"]]
        active_orders = [o for o in orders_data if o["status"] in ("confirmed", "shipped", "pending")]

        return json.dumps({
            "date": str(today),
            "orders": {
                "today_count": len(today_orders),
                "today_revenue": float(sum(o["total_price"] for o in today_orders)),
                "total_all_time": len(orders_data),
                "total_revenue": float(sum(o["total_price"] for o in orders_data)),
                "by_status": status_counts,
                "active_orders": len(active_orders),
            },
            "inventory": {
                "total_products": len(products_data),
                "critical_stock_count": len(critical_stock),
                "critical_products": critical_stock,
            },
            "customers": {"total": customer_count},
        }, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("generate_daily_summary DB query failed")
        return json.dumps({"error": "Günlük özet oluşturulurken bir hata oluştu."})