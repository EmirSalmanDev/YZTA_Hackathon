"""
stock_tools.py — LangChain tools for inventory/stock management
Tools: check_inventory, low_stock_alert, update_stock
"""

from __future__ import annotations

import json
from typing import Optional

from langchain.tools import tool
from sqlmodel import select

from database.connection import get_session
from database.models import Product


@tool
def check_inventory(product_name: str) -> str:
    """
    Check current stock level of a product by name (partial match supported).
    Returns product details including current stock, critical threshold, unit and price.
    Use this when asked about availability of a specific product.
    """
    with get_session() as session:
        products = session.exec(select(Product)).all()
        # Case-insensitive partial match
        matches = [p for p in products if product_name.lower() in p.name.lower()]

        if not matches:
            return json.dumps({"error": f"No product found matching '{product_name}'."})

        result = []
        for p in matches:
            result.append({
                "product_id": p.id,
                "name": p.name,
                "stock_amount": p.stock_amount,
                "critical_threshold": p.critical_threshold,
                "unit": p.unit,
                "price": float(p.price),
                "is_low_stock": p.stock_amount <= p.critical_threshold,
                "status": "KRİTİK" if p.stock_amount <= p.critical_threshold else
                          ("DÜŞÜK" if p.stock_amount <= p.critical_threshold * 1.5 else "NORMAL"),
            })
        return json.dumps(result, ensure_ascii=False)


@tool
def low_stock_alert() -> str:
    """
    Get a list of ALL products that are at or below their critical stock threshold.
    Returns products that need urgent restocking.
    Use this for proactive stock monitoring, daily summaries, or when asked 'what needs restocking'.
    """
    with get_session() as session:
        all_products = session.exec(select(Product)).all()
        low = [p for p in all_products if p.stock_amount <= p.critical_threshold]
        warning = [p for p in all_products if
                   p.critical_threshold < p.stock_amount <= p.critical_threshold * 1.5]

    if not low and not warning:
        return json.dumps({"message": "All products are at healthy stock levels.", "critical": [], "warning": []})

    return json.dumps({
        "critical_count": len(low),
        "warning_count": len(warning),
        "critical": [
            {
                "product_id": p.id,
                "name": p.name,
                "stock_amount": p.stock_amount,
                "critical_threshold": p.critical_threshold,
                "unit": p.unit,
                "deficit": p.critical_threshold - p.stock_amount,
            }
            for p in low
        ],
        "warning": [
            {
                "product_id": p.id,
                "name": p.name,
                "stock_amount": p.stock_amount,
                "critical_threshold": p.critical_threshold,
                "unit": p.unit,
            }
            for p in warning
        ],
    }, ensure_ascii=False)


@tool
def update_stock(product_id: int, new_amount: int) -> str:
    """
    Update the stock amount for a product.
    Use this when the business owner reports receiving new inventory or wants to adjust stock.
    new_amount must be >= 0.
    """
    if new_amount < 0:
        return json.dumps({"error": "Stock amount cannot be negative."})

    with get_session() as session:
        product = session.get(Product, product_id)
        if not product:
            return json.dumps({"error": f"Product #{product_id} not found."})

        old_amount = product.stock_amount
        product.stock_amount = new_amount
        session.add(product)
        session.commit()

    return json.dumps({
        "success": True,
        "product_id": product_id,
        "name": product.name,
        "old_amount": old_amount,
        "new_amount": new_amount,
        "unit": product.unit,
        "is_now_critical": new_amount <= product.critical_threshold,
    }, ensure_ascii=False)


@tool
def list_all_products() -> str:
    """
    List all products in the inventory with their stock status.
    Use this for a full inventory overview.
    """
    with get_session() as session:
        products = session.exec(select(Product)).all()

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