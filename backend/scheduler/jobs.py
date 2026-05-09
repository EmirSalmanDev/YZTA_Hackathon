import json
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select

from database.connection import engine
from database.models import Order, Product

_DATA_DIR = Path("data")
_ALERTS_FILE = _DATA_DIR / "alerts.json"
_SUMMARY_FILE = _DATA_DIR / "daily_summary.json"

scheduler = BackgroundScheduler(timezone="Europe/Istanbul")


def check_critical_stock() -> None:
    """Write every product below its critical_threshold to data/alerts.json."""
    with Session(engine) as session:
        products = session.exec(select(Product)).all()

    critical = [
        {
            "id": p.id,
            "name": p.name,
            "stock_amount": p.stock_amount,
            "critical_threshold": p.critical_threshold,
            "unit": p.unit,
        }
        for p in products
        if p.stock_amount <= p.critical_threshold
    ]

    _DATA_DIR.mkdir(exist_ok=True)
    _tmp = _ALERTS_FILE.with_suffix(".tmp")
    _tmp.write_text(
        json.dumps(
            {
                "last_check": datetime.now(timezone.utc).isoformat(),
                "critical_count": len(critical),
                "products": critical,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _tmp.replace(_ALERTS_FILE)


def daily_summary() -> None:
    """Write an orders + critical-stock summary to data/daily_summary.json."""
    with Session(engine) as session:
        orders = session.exec(select(Order)).all()
        products = session.exec(select(Product)).all()

    status_counts: dict[str, int] = {}
    for order in orders:
        status_counts[order.status] = status_counts.get(order.status, 0) + 1

    critical = [
        {
            "id": p.id,
            "name": p.name,
            "stock_amount": p.stock_amount,
            "critical_threshold": p.critical_threshold,
            "unit": p.unit,
        }
        for p in products
        if p.stock_amount <= p.critical_threshold
    ]

    _DATA_DIR.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc)
    _tmp = _SUMMARY_FILE.with_suffix(".tmp")
    _tmp.write_text(
        json.dumps(
            {
                "date": now.date().isoformat(),
                "generated_at": now.isoformat(),
                "orders": {"total": len(orders), **status_counts},
                "critical_stock_count": len(critical),
                "critical_stock": critical,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _tmp.replace(_SUMMARY_FILE)


def start_scheduler() -> None:
    scheduler.add_job(
        check_critical_stock,
        trigger="interval",
        minutes=15,
        id="stock_check",
        replace_existing=True,
    )
    scheduler.add_job(
        daily_summary,
        trigger="cron",
        hour=8,
        minute=0,
        id="daily_summary",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()


if __name__ == "__main__":
    check_critical_stock()
    daily_summary()
    print("smoke ok")
