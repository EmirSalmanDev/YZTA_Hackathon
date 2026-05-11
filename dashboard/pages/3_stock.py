"""
3_stock.py — Stok Yönetimi.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_login_prompt
from utils.auth import require_auth
from utils.api_client import get_stock, update_stock

setup_page("Stok")

if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

stock = get_stock()
render_header("Stok Yönetimi", f"Toplam {len(stock)} çeşit ürün listeleniyor.")

# ... (Stock list logic remains same as updated previously)
for p in stock:
    amt = p.get("stock_amount", 0)
    thr = p.get("critical_threshold", 5)
    pct = min(100, int((amt / max(thr, 1)) * 100))
    bar_color = "#DC2626" if amt < thr else "#059669"
    
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"**{p.get('name')}** (#{p.get('id')})")
        with c2:
            st.markdown(f"₺{p.get('price', 0):,.2f}")
        
        st.markdown(f"""
        <div style="width:100%; height:6px; background:#F3F4F6; border-radius:3px; margin:10px 0;">
            <div style="width:{pct}%; height:100%; background:{bar_color}; border-radius:3px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Stok Güncelle", key=f"e_{p['id']}"):
            st.session_state[f"edit_{p['id']}"] = True
        
        if st.session_state.get(f"edit_{p['id']}"):
            with st.form(f"f_{p['id']}"):
                new_amt = st.number_input("Yeni Miktar", value=amt)
                if st.form_submit_button("Kaydet"):
                    update_stock(p["id"], new_amt)
                    st.session_state.pop(f"edit_{p['id']}", None)
                    st.rerun()
