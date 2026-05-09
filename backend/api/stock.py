from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from database.connection import get_session_dep as get_session
from database.models import Product

router = APIRouter()


class StockUpdate(BaseModel):
    stock_amount: int


@router.get("/stock", response_model=List[Product])
async def list_stock(session: Session = Depends(get_session)) -> List[Product]:
    return list(session.exec(select(Product)).all())


@router.get("/stock/critical", response_model=List[Product])
async def critical_stock(session: Session = Depends(get_session)) -> List[Product]:
    products = session.exec(select(Product)).all()
    return [p for p in products if p.stock_amount <= p.critical_threshold]


@router.patch("/stock/{product_id}", response_model=Product)
async def update_stock(
    product_id: int,
    body: StockUpdate,
    session: Session = Depends(get_session),
) -> Product:
    if body.stock_amount < 0:
        raise HTTPException(status_code=422, detail="stock_amount cannot be negative")
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.stock_amount = body.stock_amount
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


if __name__ == "__main__":
    print("smoke ok")
