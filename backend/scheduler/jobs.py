from apscheduler.schedulers.background import BackgroundScheduler

from agent.tools.stock_tools import get_critical_stock
from agent.tools.notify_tools import send_alert

scheduler = BackgroundScheduler()


def check_stock_levels() -> None:
    critical = get_critical_stock()
    for product in critical:
        send_alert(
            message=f"Kritik stok: {product['name']} — {product['quantity']} {product['unit']} kaldı",
            level="warning",
        )


def start_scheduler() -> None:
    scheduler.add_job(check_stock_levels, "interval", minutes=15, id="stock_check")
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()


if __name__ == "__main__":
    print("smoke ok")
