"""
cargo_tools.py — LangChain tools for cargo/shipment tracking
Tools: track_shipment, get_order_cargo_history
"""

from __future__ import annotations

import json

from langchain.tools import tool
from sqlmodel import select

from database.connection import get_session
from database.models import Order, CargoEvent, Customer


@tool
def track_shipment(cargo_tracking_id: str) -> str:
    """
    Track a shipment by its cargo tracking ID.
    Returns the full event history of the shipment (location, status, timestamps).
    Use this when a customer provides a tracking number or asks 'where is my package'.
    """
    with get_session() as session:
        # Find order with this tracking ID
        order = session.exec(
            select(Order).where(Order.cargo_tracking_id == cargo_tracking_id)
        ).first()

        if not order:
            return json.dumps({"error": f"No shipment found with tracking ID '{cargo_tracking_id}'."})

        events = session.exec(
            select(CargoEvent)
            .where(CargoEvent.order_id == order.id)
            .order_by(CargoEvent.timestamp.desc())
        ).all()

        customer = session.get(Customer, order.customer_id)

    if not events:
        return json.dumps({
            "tracking_id": cargo_tracking_id,
            "order_id": order.id,
            "order_status": order.status,
            "message": "No cargo events recorded yet.",
            "events": [],
        })

    return json.dumps({
        "tracking_id": cargo_tracking_id,
        "order_id": order.id,
        "order_status": order.status,
        "customer_name": customer.name if customer else "Unknown",
        "delivery_date": str(order.delivery_date) if order.delivery_date else None,
        "latest_status": events[0].status,
        "latest_location": events[0].location,
        "total_events": len(events),
        "events": [
            {
                "status": e.status,
                "location": e.location,
                "timestamp": str(e.timestamp),
            }
            for e in events
        ],
    }, ensure_ascii=False)


@tool
def track_by_order_id(order_id: int) -> str:
    """
    Track a shipment by order ID instead of tracking number.
    Use this when a customer mentions their order number and wants shipping info.
    """
    with get_session() as session:
        order = session.get(Order, order_id)
        if not order:
            return json.dumps({"error": f"Order #{order_id} not found."})

        if not order.cargo_tracking_id:
            return json.dumps({
                "order_id": order_id,
                "order_status": order.status,
                "message": "This order does not have a cargo tracking ID yet. It may not have shipped.",
            })

        events = session.exec(
            select(CargoEvent)
            .where(CargoEvent.order_id == order_id)
            .order_by(CargoEvent.timestamp.desc())
        ).all()

    return json.dumps({
        "order_id": order_id,
        "tracking_id": order.cargo_tracking_id,
        "order_status": order.status,
        "delivery_date": str(order.delivery_date) if order.delivery_date else None,
        "latest_status": events[0].status if events else "No events",
        "latest_location": events[0].location if events else None,
        "events": [
            {
                "status": e.status,
                "location": e.location,
                "timestamp": str(e.timestamp),
            }
            for e in events
        ],
    }, ensure_ascii=False)