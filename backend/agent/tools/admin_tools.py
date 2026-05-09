"""
admin_tools.py — LangChain tools for business owner / admin operations
Tools: get_business_stats, search_customer, get_pending_orders
"""

from __future__ import annotations

import json
from datetime import date, timedelta

from langchain.tools import tool
from sqlmodel import select

from database.connection import get_session
from database.models import Order, Product, Customer, CargoEvent


@tool
def get_business_stats(period: str = "today") -> str:
    """
    Get business statistics for a given period.
    period options: 'today', 'week', 'month', 'all'
    Returns order counts, revenue, and top metrics.
    Use this when the business owner asks for stats or a performance overview.
    """
    today = date.today()
    period_map = {
        "today": today,
        "week": today - timedelta(days=7),
        "month": today - timedelta(days=30),
        "all": None,
    }

    if period not in period_map:
        period = "today"

    cutoff = period_map[period]

    with get_session() as session:
        all_orders = session.exec(select(Order)).all()
        all_products = session.exec(select(Product)).all()

    filtered = [
        o for o in all_orders
        if cutoff is None or (o.created_at and o.created_at.date() >= cutoff)
    ]

    revenue = sum(o.total_price for o in filtered)
    status_dist: dict[str, int] = {}
    for o in filtered:
        status_dist[o.status] = status_dist.get(o.status, 0) + 1

    low_stock = [p for p in all_products if p.stock_amount <= p.critical_threshold]

    return json.dumps({
        "period": period,
        "order_count": len(filtered),
        "total_revenue": float(revenue),
        "avg_order_value": float(revenue / len(filtered)) if filtered else 0,
        "status_distribution": status_dist,
        "low_stock_alerts": len(low_stock),
        "low_stock_products": [p.name for p in low_stock],
    }, ensure_ascii=False)


@tool
def search_customer(query: str) -> str:
    """
    Search for a customer by name, phone number, or email.
    Returns matching customer profiles and their order count.
    Use this when the owner wants to look up a specific customer.
    """
    with get_session() as session:
        all_customers = session.exec(select(Customer)).all()
        all_orders = session.exec(select(Order)).all()

    q = query.lower()
    matches = [
        c for c in all_customers
        if q in c.name.lower()
        or q in (c.phone or "").lower()
        or q in (c.email or "").lower()
        or q in (c.whatsapp_number or "").lower()
    ]

    if not matches:
        return json.dumps({"message": f"No customer found matching '{query}'.", "results": []})

    # Count orders per customer
    order_counts = {}
    for o in all_orders:
        order_counts[o.customer_id] = order_counts.get(o.customer_id, 0) + 1

    return json.dumps({
        "match_count": len(matches),
        "results": [
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "email": c.email,
                "whatsapp_number": c.whatsapp_number,
                "order_count": order_counts.get(c.id, 0),
            }
            for c in matches
        ],
    }, ensure_ascii=False)


@tool
def get_pending_orders() -> str:
    """
    Get all orders that require attention: pending confirmation or shipped but not delivered.
    Use this for a quick action list for the business owner.
    """
    with get_session() as session:
        orders = session.exec(
            select(Order).where(Order.status.in_(["pending", "confirmed", "shipped"]))
        ).all()

        result = []
        for o in orders:
            customer = session.get(Customer, o.customer_id)
            result.append({
                "order_id": o.id,
                "customer_name": customer.name if customer else "Unknown",
                "customer_phone": customer.phone if customer else None,
                "status": o.status,
                "total_price": float(o.total_price),
                "created_at": str(o.created_at),
                "delivery_date": str(o.delivery_date) if o.delivery_date else None,
                "cargo_tracking_id": o.cargo_tracking_id,
            })

    return json.dumps({
        "pending_count": len(result),
        "orders": result,
    }, ensure_ascii=False)