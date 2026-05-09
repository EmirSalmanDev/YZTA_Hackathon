"""
notify_tools.py — LangChain tools for notifications and email drafting
Tools: draft_supplier_email, draft_customer_notification, generate_daily_summary
"""

from __future__ import annotations

import json
from datetime import datetime, date

from langchain.tools import tool
from sqlmodel import select

from database.connection import get_session
from database.models import Product, Order, Customer, CargoEvent


@tool
def draft_supplier_email(product_name: str, quantity_needed: int, supplier_name: str = "Tedarikçi") -> str:
    """
    Draft a professional restock request email to a supplier for a product.
    Use this when stock is critically low and the business owner wants to order more.
    Returns a ready-to-send email draft in Turkish.
    """
    today = date.today().strftime("%d.%m.%Y")

    # Look up product details
    with get_session() as session:
        products = session.exec(select(Product)).all()
        product = next((p for p in products if product_name.lower() in p.name.lower()), None)

    stock_info = ""
    if product:
        stock_info = f"Mevcut stok: {product.stock_amount} {product.unit} (Kritik eşik: {product.critical_threshold} {product.unit})"

    email_draft = f"""Konu: Acil Stok Yenileme Talebi — {product_name}

Sayın {supplier_name} Yetkilileri,

İşletmemizde "{product_name}" ürününün stoğu kritik seviyeye düşmüştür.
{stock_info}

Bu doğrultuda, aşağıdaki miktarda sipariş vermek istiyoruz:

• Ürün: {product_name}
• Miktar: {quantity_needed} {product.unit if product else 'adet'}
• Tahmini Teslimat: En kısa sürede (tercihen 2-3 iş günü içinde)

Stok durumumuz acil olduğundan, talebimizin öncelikli olarak değerlendirilmesini rica ederiz.
Fiyat teklifi ve teslimat tarihi için lütfen en kısa sürede iletişime geçiniz.

Tarih: {today}

Saygılarımızla,
KOBİ Pilot Sistemi
"""

    return json.dumps({
        "subject": f"Acil Stok Yenileme Talebi — {product_name}",
        "to": supplier_name,
        "body": email_draft.strip(),
        "product_name": product_name,
        "quantity_needed": quantity_needed,
    }, ensure_ascii=False)


@tool
def draft_customer_notification(order_id: int, message_type: str) -> str:
    """
    Draft a notification message for a customer about their order.
    message_type options: 'shipped', 'delivered', 'delayed', 'confirmed', 'cancelled'
    Returns a ready-to-send SMS/WhatsApp message in Turkish.
    """
    valid_types = {"shipped", "delivered", "delayed", "confirmed", "cancelled"}
    if message_type not in valid_types:
        return json.dumps({"error": f"Invalid message_type. Choose from: {valid_types}"})

    with get_session() as session:
        order = session.get(Order, order_id)
        if not order:
            return json.dumps({"error": f"Order #{order_id} not found."})
        customer = session.get(Customer, order.customer_id)

    customer_name = customer.name.split()[0] if customer else "Müşteri"  # First name
    tracking = order.cargo_tracking_id or "—"
    delivery = str(order.delivery_date) if order.delivery_date else "belirtilmedi"

    templates = {
        "confirmed": f"Merhaba {customer_name}! 🎉 #{order_id} numaralı siparişiniz onaylandı. Toplam tutar: {order.total_price:.2f}₺. Hazırlanmaya başlandı, kısa sürede kargoya verilecektir.",
        "shipped": f"Merhaba {customer_name}! 📦 #{order_id} numaralı siparişiniz kargoya verildi! Takip numaranız: {tracking}. Tahmini teslimat: {delivery}.",
        "delivered": f"Merhaba {customer_name}! ✅ #{order_id} numaralı siparişiniz teslim edildi. Umarız memnun kalmışsınızdır! Herhangi bir sorun için bize ulaşabilirsiniz.",
        "delayed": f"Merhaba {customer_name}! ⚠️ #{order_id} numaralı siparişiniz lojistik nedenlerle gecikmiştir. Yeni tahmini teslimat: {delivery}. Anlayışınız için teşekkürler.",
        "cancelled": f"Merhaba {customer_name}. #{order_id} numaralı siparişiniz iptal edilmiştir. Ödeme iadesi 3-5 iş günü içinde gerçekleşecektir. Detay için iletişime geçebilirsiniz.",
    }

    return json.dumps({
        "order_id": order_id,
        "customer_name": customer.name if customer else "Unknown",
        "customer_phone": customer.phone if customer else None,
        "whatsapp_number": customer.whatsapp_number if customer else None,
        "message_type": message_type,
        "message": templates[message_type],
    }, ensure_ascii=False)


@tool
def generate_daily_summary() -> str:
    """
    Generate a comprehensive daily business summary including:
    - Today's orders and revenue
    - Low stock alerts
    - Pending shipments
    Use this for the daily automated report or when the owner asks for a business overview.
    """
    today = date.today()

    with get_session() as session:
        all_orders = session.exec(select(Order)).all()
        all_products = session.exec(select(Product)).all()
        all_customers = session.exec(select(Customer)).all()

        # Today's orders
        today_orders = [o for o in all_orders if o.created_at and o.created_at.date() == today]

        # Status counts
        status_counts: dict[str, int] = {}
        for o in all_orders:
            status_counts[o.status] = status_counts.get(o.status, 0) + 1

        # Revenue
        today_revenue = sum(o.total_price for o in today_orders)
        total_revenue = sum(o.total_price for o in all_orders)

        # Low stock
        critical_stock = [p for p in all_products if p.stock_amount <= p.critical_threshold]

        # Pending/in-transit orders
        active_orders = [o for o in all_orders if o.status in ("confirmed", "shipped", "pending")]

    summary = {
        "date": str(today),
        "orders": {
            "today_count": len(today_orders),
            "today_revenue": float(today_revenue),
            "total_all_time": len(all_orders),
            "total_revenue": float(total_revenue),
            "by_status": status_counts,
            "active_orders": len(active_orders),
        },
        "inventory": {
            "total_products": len(all_products),
            "critical_stock_count": len(critical_stock),
            "critical_products": [
                {"name": p.name, "stock": p.stock_amount, "threshold": p.critical_threshold, "unit": p.unit}
                for p in critical_stock
            ],
        },
        "customers": {
            "total": len(all_customers),
        },
    }

    return json.dumps(summary, ensure_ascii=False, indent=2)