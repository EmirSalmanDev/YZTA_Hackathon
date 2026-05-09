from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Channel(str, Enum):
    web = "web"
    whatsapp = "whatsapp"


class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    email: str
    whatsapp_number: str

    orders: List["Order"] = Relationship(back_populates="customer")
    conversations: List["Conversation"] = Relationship(back_populates="customer")


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    stock_amount: int
    critical_threshold: int
    unit: str
    price: float


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    status: str
    total_price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    delivery_date: Optional[date] = Field(default=None)
    cargo_tracking_id: Optional[str] = Field(default=None)

    customer: Optional["Customer"] = Relationship(back_populates="orders")
    cargo_events: List["CargoEvent"] = Relationship(back_populates="order")


class CargoEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    status: str
    location: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    order: Optional["Order"] = Relationship(back_populates="cargo_events")


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    channel: Channel
    last_message: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional["Customer"] = Relationship(back_populates="conversations")


if __name__ == "__main__":
    print("smoke ok")
