from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database.connection import get_session
from database.models import Order

router = APIRouter()


@router.get("/orders", response_model=List[Order])
async def list_orders(session: Session = Depends(get_session)) -> List[Order]:
    orders = session.exec(select(Order)).all()
    return list(orders)


@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int, session: Session = Depends(get_session)) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


if __name__ == "__main__":
    print("smoke ok")
