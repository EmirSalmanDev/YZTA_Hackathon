"""
2_orders.py — Sipariş Yönetimi.
"""

import streamlit as st
from utils.styles import setup_page, render_header, status_badge, render_login_prompt
from utils.auth import require_auth
from utils.api_client import get_orders, update_order_status

setup_page("Siparişler")

if not require_auth():
    render_login_prompt()

# Data
orders = get_orders()
render_header("Sipariş Yönetimi", f"Toplam {len(orders)} sipariş bulundu.")

# Filters
with st.container(border=True):
    c1, c2 = st.columns(2)
    search = c1.text_input("Sipariş veya Müşteri Ara", placeholder="Örn: #25")
    status_filter = c2.selectbox("Durum Filtresi", ["Hepsi", "Bekliyor", "Kargoda", "Teslim", "İptal"])

st.markdown("---")
filtered = [o for o in orders if status_filter == "Hepsi" or status_filter.lower() in status_badge(o['status']).lower()]

if not filtered:
    st.info("Filtreye uygun sipariş bulunamadı.")
else:
    for o in sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True):
        status = o.get("status", "pending")
        oid = o.get("id", "?")
        
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:18px; font-weight:800; color:#1A1A1A;">#{oid}</span>
                        {status_badge(status)}
                    </div>
                    <div style="font-size:13px; color:#6B7280; margin-top:6px;">
                        📅 {o.get('created_at', '')[:16].replace('T', ' ')} · Müşteri #{o.get('customer_id', '?')}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:20px; font-weight:800; color:#2D6A2E;">₺{o.get('total_price', 0):,.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
            b1, b2, b3, _ = st.columns([1, 1, 1, 3])
            with b1:
                if status == "pending" and st.button("✅ Onayla", key=f"a_{oid}", use_container_width=True):
                    update_order_status(oid, "shipped"); st.rerun()
            with b2:
                if status == "shipped" and st.button("📬 Teslim", key=f"d_{oid}", use_container_width=True):
                    update_order_status(oid, "delivered"); st.rerun()
            with b3:
                if status in ("pending", "shipped") and st.button("❌ İptal", key=f"c_{oid}", use_container_width=True):
                    update_order_status(oid, "cancelled"); st.rerun()
