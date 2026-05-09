from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from database.connection import get_session
from database.models import Order

router = APIRouter()

_VALID_STATUSES = {"pending", "shipped", "delivered", "cancelled"}


class StatusUpdate(BaseModel):
    status: str


@router.get("/orders", response_model=List[Order])
async def list_orders(
    status: Optional[str] = Query(default=None, description="Filter by order status"),
    filter_date: Optional[date] = Query(default=None, description="Filter by creation date (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
) -> List[Order]:
    if status is not None and status not in _VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Allowed values: {', '.join(sorted(_VALID_STATUSES))}",
        )
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    if filter_date:
        query = query.where(func.date(Order.created_at) == filter_date)
    orders = session.exec(query).all()
    return list(orders)


@router.get("/orders/{order_id}", response_model=Order)
async def get_order(
    order_id: int,
    session: Session = Depends(get_session),
) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/orders/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: int,
    body: StatusUpdate,
    session: Session = Depends(get_session),
) -> Order:
    if body.status not in _VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Allowed values: {', '.join(sorted(_VALID_STATUSES))}",
        )
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = body.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


if __name__ == "__main__":
    print("smoke ok")
