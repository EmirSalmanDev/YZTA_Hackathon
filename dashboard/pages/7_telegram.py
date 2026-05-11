"""
7_telegram.py — Telegram Bot Yönetimi.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_login_prompt
from utils.auth import require_auth

setup_page("Telegram")
if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

render_header("Telegram Bot Yönetimi", "Bot ayarlarınızı buradan yönetin.")
with st.container(border=True):
    st.text_input("Admin Bot Token", type="password")
    st.button("Kaydet", type="primary")
