"""
api_client.py — Backend API istemcisi + offline mock data.

Backend çalışmadığında gerçekçi demo veriler döndürür.
Backend çalışıyorsa gerçek verileri kullanır.
"""

import os
import random
from datetime import date, datetime, timedelta
from typing import Any, Optional

import requests

# ---------------------------------------------------------------------------
# Yapılandırma
# ---------------------------------------------------------------------------
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
_TIMEOUT = 5


def _url(path: str) -> str:
    return f"{BACKEND_URL}{path}"


def _is_backend_alive() -> bool:
    try:
        r = requests.get(_url("/health"), timeout=2)
        return r.ok
    except Exception:
        return False


def _safe_get(path: str, params: dict | None = None) -> Any:
    try:
        r = requests.get(_url(path), params=params, timeout=_TIMEOUT)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return None


def _safe_post(path: str, json_data: dict) -> dict:
    try:
        r = requests.post(_url(path), json=json_data, timeout=30)
        if r.ok:
            return r.json()
        return {"error": f"HTTP {r.status_code}"}
    except Exception:
        return {"error": "Backend bağlantısı kurulamadı."}


def _safe_patch(path: str, json_data: dict) -> dict:
    try:
        r = requests.patch(_url(path), json=json_data, timeout=_TIMEOUT)
        if r.ok:
            return r.json()
        return {"error": f"HTTP {r.status_code}"}
    except Exception:
        return {"error": "Backend bağlantısı kurulamadı."}


# ===========================================================================
# MOCK DATA (Backend offline iken kullanılır)
# ===========================================================================

_MOCK_PRODUCTS = [
    {"id": 1, "name": "Domates", "stock_amount": 245, "critical_threshold": 50, "unit": "kg", "price": 18.50},
    {"id": 2, "name": "Kırmızı Biber", "stock_amount": 32, "critical_threshold": 40, "unit": "kg", "price": 28.00},
    {"id": 3, "name": "Salatalık", "stock_amount": 180, "critical_threshold": 30, "unit": "kg", "price": 12.75},
    {"id": 4, "name": "Patlıcan", "stock_amount": 15, "critical_threshold": 25, "unit": "kg", "price": 14.00},
    {"id": 5, "name": "Patates", "stock_amount": 420, "critical_threshold": 60, "unit": "kg", "price": 9.50},
    {"id": 6, "name": "Soğan", "stock_amount": 310, "critical_threshold": 50, "unit": "kg", "price": 7.25},
    {"id": 7, "name": "Havuç", "stock_amount": 8, "critical_threshold": 20, "unit": "kg", "price": 8.00},
    {"id": 8, "name": "Ispanak", "stock_amount": 90, "critical_threshold": 15, "unit": "demet", "price": 10.00},
    {"id": 9, "name": "Maydanoz", "stock_amount": 65, "critical_threshold": 10, "unit": "demet", "price": 4.50},
    {"id": 10, "name": "Kabak", "stock_amount": 125, "critical_threshold": 20, "unit": "kg", "price": 11.00},
    {"id": 11, "name": "Cherry Domates", "stock_amount": 5, "critical_threshold": 15, "unit": "kg", "price": 35.00},
    {"id": 12, "name": "Sarımsak", "stock_amount": 48, "critical_threshold": 10, "unit": "kg", "price": 65.00},
]

_MOCK_ORDERS = [
    {"id": 1001, "customer_id": 1, "status": "delivered", "total_price": 1250.00, "created_at": (datetime.now() - timedelta(days=5)).isoformat(), "cargo_tracking_id": "TRK-445521", "delivery_date": (date.today() - timedelta(days=2)).isoformat()},
    {"id": 1002, "customer_id": 2, "status": "shipped", "total_price": 780.50, "created_at": (datetime.now() - timedelta(days=2)).isoformat(), "cargo_tracking_id": "TRK-445522", "delivery_date": (date.today() + timedelta(days=1)).isoformat()},
    {"id": 1003, "customer_id": 3, "status": "pending", "total_price": 2340.00, "created_at": (datetime.now() - timedelta(hours=6)).isoformat(), "cargo_tracking_id": None, "delivery_date": None},
    {"id": 1004, "customer_id": 1, "status": "shipped", "total_price": 560.25, "created_at": (datetime.now() - timedelta(days=1)).isoformat(), "cargo_tracking_id": "TRK-445524", "delivery_date": (date.today() + timedelta(days=2)).isoformat()},
    {"id": 1005, "customer_id": 4, "status": "pending", "total_price": 1890.00, "created_at": datetime.now().isoformat(), "cargo_tracking_id": None, "delivery_date": None},
    {"id": 1006, "customer_id": 5, "status": "delivered", "total_price": 445.75, "created_at": (datetime.now() - timedelta(days=7)).isoformat(), "cargo_tracking_id": "TRK-445526", "delivery_date": (date.today() - timedelta(days=4)).isoformat()},
    {"id": 1007, "customer_id": 2, "status": "cancelled", "total_price": 320.00, "created_at": (datetime.now() - timedelta(days=3)).isoformat(), "cargo_tracking_id": None, "delivery_date": None},
    {"id": 1008, "customer_id": 6, "status": "shipped", "total_price": 1675.50, "created_at": (datetime.now() - timedelta(hours=18)).isoformat(), "cargo_tracking_id": "TRK-445528", "delivery_date": (date.today() + timedelta(days=1)).isoformat()},
    {"id": 1009, "customer_id": 3, "status": "pending", "total_price": 950.00, "created_at": datetime.now().isoformat(), "cargo_tracking_id": None, "delivery_date": None},
    {"id": 1010, "customer_id": 7, "status": "delivered", "total_price": 2100.00, "created_at": (datetime.now() - timedelta(days=4)).isoformat(), "cargo_tracking_id": "TRK-445530", "delivery_date": (date.today() - timedelta(days=1)).isoformat()},
]


# ===========================================================================
# Public API — Backend varsa oradan, yoksa mock'tan
# ===========================================================================

def get_orders(status: str | None = None, filter_date: str | None = None) -> list:
    params = {}
    if status: params["status"] = status
    if filter_date: params["filter_date"] = filter_date
    result = _safe_get("/orders", params=params)
    if result is not None:
        return result
    orders = _MOCK_ORDERS
    if status:
        orders = [o for o in orders if o["status"] == status]
    return orders


def get_order(order_id: int) -> dict:
    result = _safe_get(f"/orders/{order_id}")
    if result is not None and isinstance(result, dict):
        return result
    for o in _MOCK_ORDERS:
        if o["id"] == order_id:
            return o
    return {}


def update_order_status(order_id: int, new_status: str) -> dict:
    return _safe_patch(f"/orders/{order_id}/status", {"status": new_status})


def get_today_orders() -> list:
    today = date.today().isoformat()
    result = get_orders(filter_date=today)
    if result:
        return result
    return [o for o in _MOCK_ORDERS if o["created_at"][:10] == today]


def get_stock() -> list:
    result = _safe_get("/stock")
    if result is not None:
        return result
    return _MOCK_PRODUCTS


def get_critical_stock() -> list:
    result = _safe_get("/stock/critical")
    if result is not None:
        return result
    return [p for p in _MOCK_PRODUCTS if p["stock_amount"] <= p["critical_threshold"]]


def update_stock(product_id: int, new_amount: int) -> dict:
    return _safe_patch(f"/stock/{product_id}", {"stock_amount": new_amount})


def track_cargo(tracking_id: str) -> dict:
    result = _safe_get(f"/cargo/track/{tracking_id}")
    if result is not None and isinstance(result, dict):
        return result
    return {"status": "Dağıtımda", "carrier": "Yurtiçi Kargo", "location": "İstanbul"}


def get_cargo_delays() -> list:
    result = _safe_get("/cargo/delays")
    if result is not None:
        return result
    return [{"order_id": 1004, "expected": (date.today() - timedelta(days=1)).isoformat(), "status": "delayed"}]


def admin_chat(message: str, admin_id: int = 1) -> str:
    result = _safe_post("/api/chat/admin", {"message": message, "admin_id": admin_id, "channel": "dashboard"})
    if isinstance(result, dict) and "error" not in result:
        return result.get("response", result.get("message", str(result)))
    return f"🤖 Backend şu an çevrimdışı. Mesajınız: '{message}' — Backend başlatılınca bu özellik aktif olacak."


def health_check() -> dict:
    result = _safe_get("/health")
    if result is not None and isinstance(result, dict):
        return result
    return {"status": "offline"}


def get_dashboard_stats() -> dict:
    orders = get_orders()
    stock = get_stock()
    critical = get_critical_stock()
    today_orders = get_today_orders()
    delays = get_cargo_delays()

    today_revenue = sum(o.get("total_price", 0) for o in today_orders)
    shipped = [o for o in orders if o.get("status") == "shipped"]
    pending = [o for o in orders if o.get("status") == "pending"]

    status_dist: dict[str, int] = {}
    for o in orders:
        s = o.get("status", "unknown")
        status_dist[s] = status_dist.get(s, 0) + 1

    return {
        "today_orders": len(today_orders),
        "today_revenue": today_revenue,
        "total_orders": len(orders),
        "critical_stock_count": len(critical),
        "shipped_count": len(shipped),
        "pending_count": len(pending),
        "delay_count": len(delays),
        "total_products": len(stock),
        "status_distribution": status_dist,
        "total_revenue": sum(o.get("total_price", 0) for o in orders),
    }
