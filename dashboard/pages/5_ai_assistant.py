"""
5_ai_assistant.py — AI İşletme Asistanı.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_login_prompt
from utils.auth import require_auth

setup_page("AI Asistan")

if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

render_header("AI İşletme Asistanı", "İşletmenizle ilgili sorular sorun, analizler isteyin.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat container
chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_history:
        role = "assistant" if msg["role"] == "assistant" else "user"
        with st.chat_message(role):
            st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Nasıl yardımcı olabilirim?"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response = f"Analiz ediliyor... (Demo modunda: '{prompt}' sorusu için backend bağlantısı bekleniyor.)"
        st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
