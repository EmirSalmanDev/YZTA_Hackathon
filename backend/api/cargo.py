from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from database.connection import get_session_dep as get_session
from database.models import Order
from mock.cargo_mock import track_shipment

router = APIRouter()

_DELAYED_STATUS = "Gecikmiş"


class ShipmentStatus(BaseModel):
    tracking_id: str
    carrier: str
    status: str
    location: str
    estimated_delivery: str


class DelayedShipment(BaseModel):
    order_id: int
    tracking_id: str
    carrier: str
    status: str
    location: str
    estimated_delivery: str


@router.get("/cargo/track/{tracking_id}", response_model=ShipmentStatus)
async def track_cargo(tracking_id: str) -> ShipmentStatus:
    return ShipmentStatus(**track_shipment(tracking_id))


@router.get("/cargo/delays", response_model=List[DelayedShipment])
async def cargo_delays(session: Session = Depends(get_session)) -> List[DelayedShipment]:
    orders = session.exec(
        select(Order).where(Order.cargo_tracking_id.is_not(None))
    ).all()
    delayed: list[DelayedShipment] = []
    for order in orders:
        if order.cargo_tracking_id is None:
            continue
        result = track_shipment(order.cargo_tracking_id)
        if result["status"] == _DELAYED_STATUS:
            delayed.append(DelayedShipment(order_id=order.id, **result))  # type: ignore[arg-type]
    return delayed


if __name__ == "__main__":
    print("smoke ok")
