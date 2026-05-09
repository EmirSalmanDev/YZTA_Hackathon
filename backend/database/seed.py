import random
from datetime import datetime, timedelta, date

from faker import Faker
from sqlmodel import Session, select

from database.connection import create_db_and_tables, engine
from database.models import CargoEvent, Channel, Conversation, Customer, Order, Product

fake = Faker("tr_TR")
random.seed(42)
Faker.seed(42)

# ---------------------------------------------------------------------------
# Static catalogues
# ---------------------------------------------------------------------------

_PRODUCT_CATALOG: list[tuple[str, str, float, float]] = [
    # (name, unit, min_price, max_price)
    ("Domates", "kg", 8.0, 25.0),
    ("Kırmızı Biber", "kg", 12.0, 35.0),
    ("Yeşil Biber", "kg", 10.0, 28.0),
    ("Sivri Biber", "kg", 8.0, 22.0),
    ("Çarliston Biber", "kg", 14.0, 40.0),
    ("Sarı Biber", "kg", 15.0, 42.0),
    ("Salatalık", "kg", 5.0, 15.0),
    ("Patlıcan", "kg", 6.0, 18.0),
    ("Kabak", "kg", 4.0, 12.0),
    ("Sarı Kabak", "kg", 5.0, 14.0),
    ("Patates", "kg", 5.0, 12.0),
    ("Soğan", "kg", 4.0, 10.0),
    ("Taze Soğan", "demet", 3.0, 8.0),
    ("Sarımsak", "kg", 40.0, 80.0),
    ("Havuç", "kg", 4.0, 10.0),
    ("Turp", "kg", 3.0, 8.0),
    ("Kırmızı Turp", "demet", 4.0, 10.0),
    ("Beyaz Lahana", "kg", 3.0, 8.0),
    ("Kırmızı Lahana", "kg", 4.0, 10.0),
    ("Kara Lahana", "demet", 5.0, 12.0),
    ("Brüksel Lahanası", "kg", 15.0, 35.0),
    ("Karnabahar", "adet", 10.0, 25.0),
    ("Brokoli", "adet", 12.0, 30.0),
    ("Ispanak", "demet", 5.0, 12.0),
    ("Pazı", "demet", 4.0, 10.0),
    ("Marul", "adet", 5.0, 12.0),
    ("Kıvırcık", "adet", 5.0, 12.0),
    ("Roka", "demet", 4.0, 10.0),
    ("Semizotu", "demet", 3.0, 8.0),
    ("Maydanoz", "demet", 2.0, 6.0),
    ("Dereotu", "demet", 2.0, 6.0),
    ("Nane", "demet", 3.0, 8.0),
    ("Fesleğen", "demet", 4.0, 10.0),
    ("Tarhun", "demet", 5.0, 12.0),
    ("Kişniş", "demet", 3.0, 8.0),
    ("Pırasa", "kg", 5.0, 12.0),
    ("Kereviz", "adet", 8.0, 20.0),
    ("Enginar", "adet", 8.0, 20.0),
    ("Bamya", "kg", 15.0, 40.0),
    ("Taze Fasulye", "kg", 10.0, 25.0),
    ("Barbunya", "kg", 15.0, 35.0),
    ("Bakla", "kg", 8.0, 20.0),
    ("Bezelye", "kg", 12.0, 30.0),
    ("Mısır", "adet", 3.0, 8.0),
    ("Tatlı Mısır", "adet", 4.0, 10.0),
    ("Kuşkonmaz", "demet", 20.0, 50.0),
    ("Rezene", "adet", 6.0, 15.0),
    ("Taze Nohut", "kg", 20.0, 45.0),
    ("Cherry Domates", "kg", 20.0, 45.0),
    ("Köy Domatesi", "kg", 15.0, 35.0),
]

_ORDER_STATUSES = ["pending", "shipped", "delivered", "cancelled"]
# Weighted distribution: delivered > shipped > pending > cancelled
_STATUS_WEIGHTS = [0.20, 0.25, 0.40, 0.15]

_CITIES = [
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya",
    "Adana", "Konya", "Gaziantep", "Kayseri", "Eskişehir",
]

# Ordered event sequences per status
_CARGO_EVENTS: dict[str, list[tuple[str, str]]] = {
    "pending": [
        ("Sipariş Alındı", "Depo"),
    ],
    "shipped": [
        ("Sipariş Alındı", "Depo"),
        ("Kargoya Verildi", "İstanbul"),
        ("Dağıtımda", "{city}"),
    ],
    "delivered": [
        ("Sipariş Alındı", "Depo"),
        ("Kargoya Verildi", "İstanbul"),
        ("Transfer Merkezinde", "{city}"),
        ("Teslim Edildi", "{city}"),
    ],
    "cancelled": [
        ("Sipariş Alındı", "Depo"),
        ("İptal Edildi", "Depo"),
    ],
}

_LAST_MESSAGES = [
    "Siparişim ne zaman gelecek?",
    "Stok durumunu öğrenebilir miyim?",
    "İptal etmek istiyorum.",
    "Ürün geldi, teşekkürler.",
    "Fatura bilgilerimi güncelleyebilir misiniz?",
    "Kargo takip numaram nerede?",
    "Bir sonraki teslimat ne zaman?",
    "Hasarlı ürün geldi, ne yapmalıyım?",
    "Toplu sipariş indirimi var mı?",
    "Merhaba, fiyat listesini alabilir miyim?",
]


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def _whatsapp_number() -> str:
    # +90 5XX XXX XXXX — valid Turkish mobile format
    operator = random.choice(["30", "31", "32", "35", "38", "42", "45", "50", "53", "55"])
    return f"+905{operator}{random.randint(1000000, 9999999)}"


def _make_customers(n: int) -> list[Customer]:
    return [
        Customer(
            name=fake.name(),
            phone=f"05{random.randint(30, 59)}{random.randint(1000000, 9999999)}",
            email=fake.email(),
            whatsapp_number=_whatsapp_number(),
        )
        for _ in range(n)
    ]


def _make_products() -> list[Product]:
    products = []
    for name, unit, lo, hi in _PRODUCT_CATALOG:
        price = round(random.uniform(lo, hi), 2)
        stock = random.randint(0, 500)
        threshold = random.randint(20, 80)
        products.append(Product(
            name=name,
            stock_amount=stock,
            critical_threshold=threshold,
            unit=unit,
            price=price,
        ))
    return products


def _make_orders(customer_ids: list[int], n: int) -> list[Order]:
    orders = []
    for _ in range(n):
        status = random.choices(_ORDER_STATUSES, weights=_STATUS_WEIGHTS, k=1)[0]
        created_at = fake.date_time_between(start_date="-6M", end_date="now")

        delivery_date: date | None = None
        tracking_id: str | None = None

        if status in ("shipped", "delivered"):
            tracking_id = f"TRK-{random.randint(100000, 999999)}"
        if status == "delivered":
            delivery_date = (created_at + timedelta(days=random.randint(1, 7))).date()
        elif status == "shipped":
            delivery_date = (created_at + timedelta(days=random.randint(1, 5))).date()

        orders.append(Order(
            customer_id=random.choice(customer_ids),
            status=status,
            total_price=round(random.uniform(50.0, 3000.0), 2),
            created_at=created_at,
            delivery_date=delivery_date,
            cargo_tracking_id=tracking_id,
        ))
    return orders


def _make_cargo_events(order: Order) -> list[CargoEvent]:
    city = random.choice(_CITIES)
    sequence = _CARGO_EVENTS.get(order.status, _CARGO_EVENTS["pending"])
    events = []
    # Space events 3-12 hours apart starting from order creation
    ts: datetime = order.created_at  # type: ignore[assignment]
    for status_label, location_tmpl in sequence:
        location = location_tmpl.replace("{city}", city)
        events.append(CargoEvent(
            order_id=order.id,  # type: ignore[arg-type]
            status=status_label,
            location=location,
            timestamp=ts,
        ))
        ts = ts + timedelta(hours=random.randint(3, 12))
    return events


def _make_conversations(customer_ids: list[int]) -> list[Conversation]:
    convs = []
    channels = [Channel.web] * 5 + [Channel.whatsapp] * 5
    random.shuffle(channels)
    sampled_customers = random.sample(customer_ids, k=10)
    for customer_id, channel in zip(sampled_customers, channels):
        convs.append(Conversation(
            customer_id=customer_id,
            channel=channel,
            last_message=random.choice(_LAST_MESSAGES),
            updated_at=fake.date_time_between(start_date="-30d", end_date="now"),
        ))
    return convs


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def seed() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        # Idempotency: bail out if customers already exist
        if session.exec(select(Customer)).first() is not None:
            print("Database already seeded — skipping.")
            return

        # Customers
        customers = _make_customers(30)
        session.add_all(customers)
        session.flush()  # populate .id fields
        customer_ids = [c.id for c in customers]  # type: ignore[misc]

        # Products
        session.add_all(_make_products())

        # Orders
        orders = _make_orders(customer_ids, 200)
        session.add_all(orders)
        session.flush()  # populate order .id fields

        # CargoEvents (one sequence per order)
        for order in orders:
            session.add_all(_make_cargo_events(order))

        # Conversations (5 web + 5 whatsapp)
        session.add_all(_make_conversations(customer_ids))

        session.commit()

    print(
        f"Seeded: 30 customers, {len(_PRODUCT_CATALOG)} products, "
        "200 orders, cargo events, 10 conversations."
    )


if __name__ == "__main__":
    seed()
    print("smoke ok")
