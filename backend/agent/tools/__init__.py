from .order_tools import get_order_status, list_customer_orders, update_order_status
from .stock_tools import check_inventory, low_stock_alert, update_stock, list_all_products
from .cargo_tools import track_shipment, track_by_order_id
from .notify_tools import draft_supplier_email, draft_customer_notification, generate_daily_summary
from .admin_tools import get_business_stats, search_customer, get_pending_orders

ALL_TOOLS = [
    get_order_status,
    list_customer_orders,
    update_order_status,
    check_inventory,
    low_stock_alert,
    update_stock,
    list_all_products,
    track_shipment,
    track_by_order_id,
    draft_supplier_email,
    draft_customer_notification,
    generate_daily_summary,
    get_business_stats,
    search_customer,
    get_pending_orders,
]

CUSTOMER_TOOLS = [
    get_order_status,
    list_customer_orders,
    track_shipment,
    track_by_order_id,
    check_inventory,
]

ADMIN_TOOLS = ALL_TOOLS