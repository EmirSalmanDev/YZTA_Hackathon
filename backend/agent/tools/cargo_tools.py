"""
cargo_tools.py — LangChain tools for cargo/shipment tracking
"""

from __future__ import annotations
import json
import re
import logging
from langchain.tools import tool
from sqlmodel import select
from database.connection import get_session_ctx
from database.models import Order, CargoEvent, Customer

logger = logging.getLogger(__name__)


def _parse_int(val, name="değer"):
    match = re.search(r'\d+', str(val))
    if not match:
        raise ValueError(f"Geçerli bir {name} girin.")
    return int(match.group())


@tool
def track_shipment(cargo_tracking_id: str) -> str:
    """
    Track a shipment by its cargo tracking ID.
    Use this when a customer provides a tracking number or asks 'where is my package'.
    """
    try:
        with get_session_ctx() as session:
            order = session.exec(
                select(Order).where(Order.cargo_tracking_id == cargo_tracking_id)
            ).first()

            if not order:
                return json.dumps({"error": f"'{cargo_tracking_id}' takip numaralı kargo bulunamadı."})

            events = session.exec(
                select(CargoEvent)
                .where(CargoEvent.order_id == order.id)
                .order_by(CargoEvent.timestamp.desc())
            ).all()

            customer = session.get(Customer, order.customer_id)

        return json.dumps({
            "tracking_id": cargo_tracking_id,
            "order_id": order.id,
            "order_status": order.status,
            "customer_name": customer.name if customer else "Bilinmiyor",
            "delivery_date": str(order.delivery_date) if order.delivery_date else None,
            "latest_status": events[0].status if events else "Henüz güncelleme yok",
            "latest_location": events[0].location if events else None,
            "total_events": len(events),
            "events": [
                {"status": e.status, "location": e.location, "timestamp": str(e.timestamp)}
                for e in events
            ],
        }, ensure_ascii=False)
    except Exception:
        logger.exception("track_shipment failed for tracking_id=%s", cargo_tracking_id)
        return json.dumps({"error": "Kargo takibi sırasında bir hata oluştu."})


@tool
def track_by_order_id(order_id: str) -> str:
    """
    Track a shipment by order ID instead of tracking number.
    Use this when a customer mentions their order number and wants shipping info.
    """
    try:
        oid = _parse_int(order_id, "sipariş numarası")
        with get_session_ctx() as session:
            order = session.get(Order, oid)
            if not order:
                return json.dumps({"error": f"Sipariş #{oid} bulunamadı."})

            if not order.cargo_tracking_id:
                return json.dumps({
                    "order_id": oid,
                    "order_status": order.status,
                    "message": "Bu siparişe ait kargo takip numarası henüz atanmamış.",
                })

            events = session.exec(
                select(CargoEvent)
                .where(CargoEvent.order_id == oid)
                .order_by(CargoEvent.timestamp.desc())
            ).all()

        return json.dumps({
            "order_id": oid,
            "tracking_id": order.cargo_tracking_id,
            "order_status": order.status,
            "delivery_date": str(order.delivery_date) if order.delivery_date else None,
            "latest_status": events[0].status if events else "Henüz güncelleme yok",
            "latest_location": events[0].location if events else None,
            "events": [
                {"status": e.status, "location": e.location, "timestamp": str(e.timestamp)}
                for e in events
            ],
        }, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception:
        logger.exception("track_by_order_id failed for order_id=%s", order_id)
        return json.dumps({"error": "Kargo takibi sırasında bir hata oluştu."})