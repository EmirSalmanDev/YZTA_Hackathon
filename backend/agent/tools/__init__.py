from agent.tools.order_tools import (
    get_order_status,
    list_customer_orders,
    update_order_status,
)
from agent.tools.stock_tools import (
    check_inventory,
    list_all_products,
    low_stock_alert,
    update_stock,
)
from agent.tools.cargo_tools import (
    track_by_order_id,
    track_shipment,
)
from agent.tools.notify_tools import (
    draft_customer_notification,
    draft_supplier_email,
    generate_daily_summary,
)

# Read-only tools available to customers: order lookups + cargo tracking.
CUSTOMER_TOOLS = [
    get_order_status,
    list_customer_orders,
    track_shipment,
    track_by_order_id,
]

# Write + management tools restricted to admin/owner.
ADMIN_TOOLS = [
    update_order_status,
    check_inventory,
    low_stock_alert,
    list_all_products,
    update_stock,
    draft_supplier_email,
    draft_customer_notification,
    generate_daily_summary,
]

# Union, deduplicated, preserving order.
ALL_TOOLS = CUSTOMER_TOOLS + [t for t in ADMIN_TOOLS if t not in CUSTOMER_TOOLS]


if __name__ == "__main__":
    print(f"CUSTOMER_TOOLS ({len(CUSTOMER_TOOLS)}): {[t.name for t in CUSTOMER_TOOLS]}")
    print(f"ADMIN_TOOLS    ({len(ADMIN_TOOLS)}): {[t.name for t in ADMIN_TOOLS]}")
    print(f"ALL_TOOLS      ({len(ALL_TOOLS)}): {[t.name for t in ALL_TOOLS]}")
