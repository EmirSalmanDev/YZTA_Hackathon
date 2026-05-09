from typing import List

from sqlmodel import Session, select

from database.connection import engine
from database.models import Product


def get_stock() -> List[dict]:
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return [p.model_dump() for p in products]


def get_critical_stock() -> List[dict]:
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return [p.model_dump() for p in products if p.quantity <= p.threshold]


if __name__ == "__main__":
    print("smoke ok")
