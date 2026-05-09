from database.connection import create_db_and_tables, get_session
from database.models import Product, Order, CargoEvent


def seed() -> None:
    create_db_and_tables()
    with next(get_session()) as session:
        # Sample products
        products = [
            Product(name="Ahşap Sandalye", sku="SKU-001", quantity=5, threshold=10),
            Product(name="Metal Masa", sku="SKU-002", quantity=20, threshold=5),
            Product(name="Kumaş Koltuk", sku="SKU-003", quantity=3, threshold=8),
        ]
        for p in products:
            session.add(p)

        # Sample orders
        orders = [
            Order(customer_name="Ali Yılmaz", product_sku="SKU-001", quantity=2, status="shipped"),
            Order(customer_name="Ayşe Kaya", product_sku="SKU-003", quantity=1, status="pending"),
        ]
        for o in orders:
            session.add(o)

        session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    seed()
    print("smoke ok")
