"""
6_reports.py — Performans Raporları.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_login_prompt
from utils.auth import require_auth
from utils.api_client import get_dashboard_stats

setup_page("Raporlar")
if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

stats = get_dashboard_stats()
render_header("Raporlar ve Analizler", "Operasyonel verilerinizi inceleyin.")

with st.container(border=True):
    st.markdown("### Satış Trendi")
    st.bar_chart({"Gün": ["Pzt", "Sal", "Çar", "Per", "Cum"], "Satış": [10, 20, 15, 25, 30]})
