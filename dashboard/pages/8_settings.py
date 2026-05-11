"""
8_settings.py — Ayarlar.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_login_prompt
from utils.auth import require_auth

setup_page("Ayarlar")
if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

render_header("Ayarlar", "Hesap ve işletme ayarları.")
with st.container(border=True):
    st.text_input("İşletme Adı")
    st.button("Güncelle", type="primary")
