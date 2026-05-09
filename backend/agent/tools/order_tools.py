"""
order_tools.py — LangChain tools for order management
Tools: get_order_status, list_customer_orders
"""

from __future__ import annotations

import json
from typing import Optional

from langchain.tools import tool
from sqlmodel import select

from database.connection import get_session
from database.models import Order, Customer, CargoEvent


@tool
def get_order_status(order_id: int) -> str:
    """
    Get the current status and details of a specific order by its ID.
    Returns order status, total price, delivery date, and latest cargo event.
    Use this when a customer asks about a specific order number.
    """
    with get_session() as session:
        order = session.get(Order, order_id)
        if not order:
            return json.dumps({"error": f"Order #{order_id} not found."})

        customer = session.get(Customer, order.customer_id)

        # Latest cargo event
        cargo_events = session.exec(
            select(CargoEvent)
            .where(CargoEvent.order_id == order_id)
            .order_by(CargoEvent.timestamp.desc())
        ).all()

        latest_event = None
        if cargo_events:
            ev = cargo_events[0]
            latest_event = {
                "status": ev.status,
                "location": ev.location,
                "timestamp": str(ev.timestamp),
            }

        return json.dumps({
            "order_id": order.id,
            "customer_name": customer.name if customer else "Unknown",
            "status": order.status,
            "total_price": float(order.total_price),
            "created_at": str(order.created_at),
            "delivery_date": str(order.delivery_date) if order.delivery_date else None,
            "cargo_tracking_id": order.cargo_tracking_id,
            "latest_cargo_event": latest_event,
        }, ensure_ascii=False)


@tool
def list_customer_orders(customer_id: int) -> str:
    """
    List all orders belonging to a specific customer.
    Returns a summary list of their orders with status and totals.
    Use this when a customer asks 'what are my orders' or 'show my order history'.
    """
    with get_session() as session:
        orders = session.exec(
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
        ).all()

        if not orders:
            return json.dumps({"message": "No orders found for this customer.", "orders": []})

        order_list = [
            {
                "order_id": o.id,
                "status": o.status,
                "total_price": float(o.total_price),
                "created_at": str(o.created_at),
                "delivery_date": str(o.delivery_date) if o.delivery_date else None,
            }
            for o in orders
        ]
        return json.dumps({"customer_id": customer_id, "total_orders": len(orders), "orders": order_list}, ensure_ascii=False)


@tool
def update_order_status(order_id: int, new_status: str) -> str:
    """
    Update the status of an order. Valid statuses: pending, confirmed, shipped, delivered, cancelled.
    Use this when the business owner wants to change an order's status.
    """
    valid_statuses = {"pending", "confirmed", "shipped", "delivered", "cancelled"}
    if new_status not in valid_statuses:
        return json.dumps({"error": f"Invalid status '{new_status}'. Valid: {valid_statuses}"})

    with get_session() as session:
        order = session.get(Order, order_id)
        if not order:
            return json.dumps({"error": f"Order #{order_id} not found."})

        old_status = order.status
        order.status = new_status
        session.add(order)
        session.commit()

    return json.dumps({
        "success": True,
        "order_id": order_id,
        "old_status": old_status,
        "new_status": new_status,
    }, ensure_ascii=False)
