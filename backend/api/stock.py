from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database.connection import get_session
from database.models import Product

router = APIRouter()


@router.get("/stock", response_model=List[Product])
async def list_stock(session: Session = Depends(get_session)) -> List[Product]:
    products = session.exec(select(Product)).all()
    return list(products)


@router.get("/stock/critical", response_model=List[Product])
async def critical_stock(session: Session = Depends(get_session)) -> List[Product]:
    products = session.exec(select(Product)).all()
    return [p for p in products if p.quantity <= p.threshold]


if __name__ == "__main__":
    print("smoke ok")
