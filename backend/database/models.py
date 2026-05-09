from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    sku: str
    quantity: int
    threshold: int
    unit: str = "adet"
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    product_sku: str
    quantity: int
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CargoEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    carrier: str
    tracking_code: str
    status: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)


if __name__ == "__main__":
    print("smoke ok")
