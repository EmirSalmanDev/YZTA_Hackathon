"""
order_tools.py — LangChain tools for order management
"""

from __future__ import annotations
import json
import re
import logging
from langchain.tools import tool
from sqlmodel import select
from database.connection import get_session
from database.models import Order, Customer, CargoEvent

logger = logging.getLogger(__name__)


def _parse_int(val, name="değer"):
    match = re.search(r'\d+', str(val))
    if not match:
        raise ValueError(f"Geçerli bir {name} girin.")
    return int(match.group())


@tool
def get_order_status(order_id: str) -> str:
    """
    Get the current status and details of a specific order by its ID.
    Returns order status, total price, delivery date, and latest cargo event.
    Use this when a customer asks about a specific order number.
    """
    try:
        oid = _parse_int(order_id, "sipariş numarası")
        with get_session() as session:
            order = session.get(Order, oid)
            if not order:
                return json.dumps({"error": f"Sipariş #{oid} bulunamadı."})

            customer = session.get(Customer, order.customer_id)
            cargo_events = session.exec(
                select(CargoEvent)
                .where(CargoEvent.order_id == oid)
                .order_by(CargoEvent.timestamp.desc())
            ).all()

            result = {
                "order_id": order.id,
                "customer_name": customer.name if customer else "Bilinmiyor",
                "status": order.status,
                "total_price": float(order.total_price),
                "created_at": str(order.created_at),
                "delivery_date": str(order.delivery_date) if order.delivery_date else None,
                "cargo_tracking_id": order.cargo_tracking_id,
                "latest_cargo_event": {
                    "status": cargo_events[0].status,
                    "location": cargo_events[0].location,
                    "timestamp": str(cargo_events[0].timestamp),
                } if cargo_events else None,
            }

        return json.dumps(result, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception:
        logger.exception("get_order_status failed for order_id=%s", order_id)
        return json.dumps({"error": "Sipariş bilgisi alınırken bir hata oluştu."})


@tool
def list_customer_orders(customer_id: str) -> str:
    """
    List all orders belonging to a specific customer.
    Use this when a customer asks 'what are my orders' or 'show my order history'.
    """
    try:
        cid = _parse_int(customer_id, "müşteri numarası")
        with get_session() as session:
            orders = session.exec(
                select(Order)
                .where(Order.customer_id == cid)
                .order_by(Order.created_at.desc())
            ).all()

            orders_data = [
                {
                    "order_id": o.id,
                    "status": o.status,
                    "total_price": float(o.total_price),
                    "created_at": str(o.created_at),
                    "delivery_date": str(o.delivery_date) if o.delivery_date else None,
                }
                for o in orders
            ]

        if not orders_data:
            return json.dumps({"message": "Bu müşteriye ait sipariş bulunamadı.", "orders": []})

        return json.dumps({
            "customer_id": cid,
            "total_orders": len(orders_data),
            "orders": orders_data,
        }, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception:
        logger.exception("list_customer_orders failed for customer_id=%s", customer_id)
        return json.dumps({"error": "Sipariş listesi alınırken bir hata oluştu."})


@tool
def update_order_status(order_id: str, new_status: str) -> str:
    """
    Update the status of an order.
    Valid statuses: pending, confirmed, shipped, delivered, cancelled.
    Use this when the business owner wants to change an order's status.
    """
    valid_statuses = {"pending", "confirmed", "shipped", "delivered", "cancelled"}
    if new_status not in valid_statuses:
        return json.dumps({"error": f"Geçersiz durum '{new_status}'. Geçerli değerler: {valid_statuses}"})

    try:
        oid = _parse_int(order_id, "sipariş numarası")
        with get_session() as session:
            order = session.get(Order, oid)
            if not order:
                return json.dumps({"error": f"Sipariş #{oid} bulunamadı."})
            old_status = order.status
            order.status = new_status
            session.add(order)
            session.commit()

        return json.dumps({
            "success": True,
            "order_id": oid,
            "old_status": old_status,
            "new_status": new_status,
        }, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception:
        logger.exception("update_order_status failed for order_id=%s", order_id)
        return json.dumps({"error": "Sipariş güncellenirken bir hata oluştu."})