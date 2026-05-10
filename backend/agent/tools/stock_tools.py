"""
stock_tools.py — LangChain tools for inventory/stock management
"""

from __future__ import annotations
import json
import re
import logging
from langchain.tools import tool
from sqlmodel import select
from database.connection import get_session_ctx
from database.models import Product

logger = logging.getLogger(__name__)


def _parse_int(val, name="değer"):
    match = re.search(r'\d+', str(val))
    if not match:
        raise ValueError(f"Geçerli bir {name} girin.")
    return int(match.group())


def _product_to_dict(p) -> dict:
    return {
        "product_id": p.id,
        "name": p.name,
        "stock_amount": p.stock_amount,
        "critical_threshold": p.critical_threshold,
        "unit": p.unit,
        "price": float(p.price),
    }


@tool
def check_inventory(product_name: str) -> str:
    """
    Check current stock level of a product by name (partial match supported).
    Use this when asked about availability of a specific product.
    """
    try:
        with get_session_ctx() as session:
            all_products = session.exec(select(Product)).all()
            products_data = [_product_to_dict(p) for p in all_products]

        matches = [p for p in products_data if product_name.lower() in p["name"].lower()]
        if not matches:
            return json.dumps({"error": f"'{product_name}' ile eşleşen ürün bulunamadı."})

        for p in matches:
            p["is_low_stock"] = p["stock_amount"] <= p["critical_threshold"]
            p["status"] = (
                "KRİTİK" if p["stock_amount"] <= p["critical_threshold"]
                else ("DÜŞÜK" if p["stock_amount"] <= p["critical_threshold"] * 1.5 else "NORMAL")
            )

        return json.dumps(matches, ensure_ascii=False)
    except Exception:
        logger.exception("check_inventory failed for product_name=%s", product_name)
        return json.dumps({"error": "Stok bilgisi alınırken bir hata oluştu."})


@tool
def low_stock_alert(dummy: str = "") -> str:
    """
    Get all products at or below their critical stock threshold.
    Use this for proactive stock monitoring or when asked what needs restocking.
    Action Input olarak bos string gir.
    """
    try:
        with get_session_ctx() as session:
            all_products = session.exec(select(Product)).all()
            products_data = [_product_to_dict(p) for p in all_products]

        critical = [p for p in products_data if p["stock_amount"] <= p["critical_threshold"]]
        warning = [p for p in products_data
                   if p["critical_threshold"] < p["stock_amount"] <= p["critical_threshold"] * 1.5]

        if not critical and not warning:
            return json.dumps({"message": "Tüm ürünler normal stok seviyesinde.", "critical": [], "warning": []})

        return json.dumps({
            "critical_count": len(critical),
            "warning_count": len(warning),
            "critical": [
                {**p, "deficit": p["critical_threshold"] - p["stock_amount"]}
                for p in critical
            ],
            "warning": warning,
        }, ensure_ascii=False)
    except Exception:
        logger.exception("low_stock_alert failed")
        return json.dumps({"error": "Stok uyarıları alınırken bir hata oluştu."})


@tool
def update_stock(product_id: str, new_amount: str) -> str:
    """
    Update the stock amount for a product. new_amount must be >= 0.
    Use this when the business owner reports receiving new inventory.
    """
    try:
        pid = _parse_int(product_id, "ürün numarası")
        amount = _parse_int(new_amount, "stok miktarı")
        if amount < 0:
            return json.dumps({"error": "Stok miktarı negatif olamaz."})

        with get_session_ctx() as session:
            product = session.get(Product, pid)
            if not product:
                return json.dumps({"error": f"Ürün #{pid} bulunamadı."})
            old_amount = product.stock_amount
            is_critical = amount <= product.critical_threshold
            name = product.name
            unit = product.unit
            product.stock_amount = amount
            session.add(product)

        return json.dumps({
            "success": True,
            "product_id": pid,
            "name": name,
            "old_amount": old_amount,
            "new_amount": amount,
            "unit": unit,
            "is_now_critical": is_critical,
        }, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception:
        logger.exception("update_stock failed for product_id=%s", product_id)
        return json.dumps({"error": "Stok güncellenirken bir hata oluştu."})


@tool
def list_all_products(dummy: str = "") -> str:
    """
    List all products in the inventory with their stock status.
    Use this for a full inventory overview.
    Action Input olarak bos string gir.
    """
    try:
        with get_session_ctx() as session:
            all_products = session.exec(select(Product)).all()
            products_data = [_product_to_dict(p) for p in all_products]

    if not products:
        return json.dumps({"message": "No products in database.", "products": []})

    return json.dumps({
        "total_products": len(products),
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "stock_amount": p.stock_amount,
                "critical_threshold": p.critical_threshold,
                "unit": p.unit,
                "price": float(p.price),
                "status": "KRİTİK" if p.stock_amount <= p.critical_threshold else "NORMAL",
            }
            for p in products
        ],
    }, ensure_ascii=False)