"""
admin_tools.py — LangChain tools for business owner operations
"""

from __future__ import annotations
import json
import re
import logging
from datetime import date, timedelta
from langchain.tools import tool
from sqlmodel import select
from database.connection import get_session_ctx
from database.models import Order, Product, Customer

logger = logging.getLogger(__name__)


@tool
def get_business_stats(period: str = "today") -> str:
    """
    Get business statistics for a given period.
    period: 'today' | 'week' | 'month' | 'all'
    Use this when the owner asks for performance stats or revenue overview.
    """
    today = date.today()
    cutoffs = {"today": today, "week": today - timedelta(days=7), "month": today - timedelta(days=30), "all": None}
    cutoff = cutoffs.get(period, today)

    try:
        with get_session_ctx() as session:
            all_orders = session.exec(select(Order)).all()
            all_products = session.exec(select(Product)).all()

            orders_data = [
                {"status": o.status, "total_price": float(o.total_price), "created_at": o.created_at}
                for o in all_orders
            ]
            products_data = [
                {"name": p.name, "stock_amount": p.stock_amount, "critical_threshold": p.critical_threshold}
                for p in all_products
            ]

        filtered = [o for o in orders_data if cutoff is None or (o["created_at"] and o["created_at"].date() >= cutoff)]
        revenue = sum(o["total_price"] for o in filtered)
        status_dist: dict[str, int] = {}
        for o in filtered:
            status_dist[o["status"]] = status_dist.get(o["status"], 0) + 1

        low_stock = [p for p in products_data if p["stock_amount"] <= p["critical_threshold"]]

        return json.dumps({
            "period": period,
            "order_count": len(filtered),
            "total_revenue": float(revenue),
            "avg_order_value": float(revenue / len(filtered)) if filtered else 0,
            "status_distribution": status_dist,
            "low_stock_alerts": len(low_stock),
            "low_stock_products": [p["name"] for p in low_stock],
        }, ensure_ascii=False)
    except Exception:
        logger.exception("get_business_stats DB query failed")
        return json.dumps({"error": "İstatistikler alınırken bir hata oluştu."})


@tool
def search_customer(query: str) -> str:
    """
    Search for a customer by name, phone, or email.
    Use this when the owner wants to look up a specific customer.
    """
    try:
        with get_session_ctx() as session:
            all_customers = session.exec(select(Customer)).all()
            all_orders = session.exec(select(Order)).all()

            customers_data = [
                {
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone,
                    "email": c.email,
                    "whatsapp_number": c.whatsapp_number,
                }
                for c in all_customers
            ]
            order_counts = {}
            for o in all_orders:
                order_counts[o.customer_id] = order_counts.get(o.customer_id, 0) + 1

        q = query.lower()
        matches = [
            c for c in customers_data
            if q in c["name"].lower()
            or q in (c["phone"] or "").lower()
            or q in (c["email"] or "").lower()
            or q in (c["whatsapp_number"] or "").lower()
        ]

        if not matches:
            return json.dumps({"message": f"'{query}' ile eşleşen müşteri bulunamadı.", "results": []})

        for c in matches:
            c["order_count"] = order_counts.get(c["id"], 0)

        return json.dumps({"match_count": len(matches), "results": matches}, ensure_ascii=False)
    except Exception:
        logger.exception("search_customer DB query failed")
        return json.dumps({"error": "Müşteri aranırken bir hata oluştu."})


@tool
def get_pending_orders(dummy: str = "") -> str:
    """
    Get all orders requiring attention: pending, confirmed, or shipped.
    Use this for a quick action list for the business owner.
    Action Input olarak bos string gir.
    """
    try:
        with get_session_ctx() as session:
            orders = session.exec(
                select(Order).where(Order.status.in_(["pending", "confirmed", "shipped"]))
            ).all()

            result = []
            for o in orders:
                customer = session.get(Customer, o.customer_id)
                result.append({
                    "order_id": o.id,
                    "customer_name": customer.name if customer else "Bilinmiyor",
                    "customer_phone": customer.phone if customer else None,
                    "status": o.status,
                    "total_price": float(o.total_price),
                    "created_at": str(o.created_at),
                    "delivery_date": str(o.delivery_date) if o.delivery_date else None,
                    "cargo_tracking_id": o.cargo_tracking_id,
                })

        return json.dumps({"pending_count": len(result), "orders": result}, ensure_ascii=False)
    except Exception:
        logger.exception("get_pending_orders DB query failed")
        return json.dumps({"error": "Bekleyen siparişler alınırken bir hata oluştu."})