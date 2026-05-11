"""
4_cargo.py — Kargo Takibi.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_login_prompt
from utils.auth import require_auth
from utils.api_client import get_orders

setup_page("Kargo")

if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

orders = get_orders()
shipped = [o for o in orders if o.get("status") == "shipped"]
render_header("Kargo Yönetimi", f"{len(shipped)} aktif gönderi yolda.")

for o in shipped:
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between;">
            <div><b>Sipariş #{o['id']}</b><br><small>{o.get('cargo_tracking_id', 'TRK-123')}</small></div>
            <div style="color:#2563EB; font-weight:700;">Yolda</div>
        </div>
        """, unsafe_allow_html=True)
