from typing import List, Optional

from sqlmodel import Session, select

from database.connection import engine
from database.models import Order


def get_orders() -> List[dict]:
    with Session(engine) as session:
        orders = session.exec(select(Order)).all()
        return [o.model_dump() for o in orders]


def get_order_by_id(order_id: int) -> Optional[dict]:
    with Session(engine) as session:
        order = session.get(Order, order_id)
        return order.model_dump() if order else None


if __name__ == "__main__":
    print("smoke ok")
