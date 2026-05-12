"""5_ai_assistant.py — KoopPilot AI İşletme Asistanı"""
import streamlit as st
from utils.styles import (
    setup_page, render_header, render_card_header,
    render_status_pill, render_login_prompt, COLORS
)
from utils.auth import require_auth
from utils.api_client import admin_chat, health_check

setup_page("AI Asistan")
if not require_auth():
    render_login_prompt(); st.stop()

render_header("AI İşletme Asistanı", "Doğal dil ile işletmenizi yönetin.",
              back_page="pages/1_dashboard.py", back_label="← Dashboard'a Dön")

# ── Backend durumu ────────────────────────────────────────────────────────────
health    = health_check()
is_online = health.get("status") == "ok"
db_info   = health.get("db", {})
extra     = f"{db_info.get('products','?')} ürün · {db_info.get('orders','?')} sipariş" if is_online else ""
render_status_pill(is_online, extra=extra)

# ── Hızlı sorular ─────────────────────────────────────────────────────────────
quick_questions = [
    ("📦", "Bugünkü sipariş özeti",   "#DBEAFE", "#1E40AF"),
    ("🚨", "Kritik stokları göster",  "#FEE2E2", "#991B1B"),
    ("🚚", "Geciken kargolar var mı?","#FEF9C3", "#92400E"),
    ("📊", "Günlük iş raporu hazırla","#DCFCE7", "#166534"),
]
quick_cols = st.columns(4)
for i, (icon, question, bg, fg) in enumerate(quick_questions):
    with quick_cols[i]:
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {fg}22;border-radius:14px;
                    padding:12px 14px;margin-bottom:4px;">
            <div style="font-size:20px;margin-bottom:5px;">{icon}</div>
            <div style="font-size:12px;font-weight:700;color:{fg};line-height:1.4;">{question}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sor →", key=f"quick_{i}", use_container_width=True):
            if "pending_quick" not in st.session_state:
                st.session_state.pending_quick = question

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

# ── Chat geçmişi ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not st.session_state.chat_history:
    st.markdown(f"""
    <div style="text-align:center;padding:56px 20px;
                background:linear-gradient(135deg,#EEF5EA,#D8EFDF);
                border-radius:20px;margin:16px 0;border:1px solid #B7E4C7;">
        <div style="font-size:56px;margin-bottom:16px;">🌿</div>
        <h3 style="font-size:20px;font-weight:900;color:{COLORS['text']};margin:0 0 8px;">
            Merhaba! Ben KoopPilot AI Asistanınız.</h3>
        <p style="font-size:14px;color:{COLORS['text_mid']};max-width:480px;
                  margin:0 auto;line-height:1.8;font-weight:500;">
            İşletmenizle ilgili her türlü soruyu yanıtlayabilirim.<br>
            Yukarıdaki hızlı sorulardan birini seçin veya aşağıya yazın.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.chat_history:
        role = "assistant" if msg["role"] == "assistant" else "user"
        with st.chat_message(role, avatar="🌿" if role == "assistant" else None):
            st.markdown(msg["content"])

# ── Mesaj gönderme ────────────────────────────────────────────────────────────
def _send_message(message: str) -> None:
    st.session_state.chat_history.append({"role": "user", "content": message})
    with st.chat_message("user"):
        st.markdown(message)
    with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("🤔 Yanıt hazırlanıyor…"):
            response = admin_chat(message)
        st.markdown(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})

if "pending_quick" in st.session_state:
    quick_msg = st.session_state.pop("pending_quick")
    _send_message(quick_msg)
    st.rerun()

if prompt := st.chat_input("Sorunuzu yazın… Örn: 'Kaç kilo domates stoğum var?'"):
    _send_message(prompt)
    st.rerun()

if st.session_state.chat_history:
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    _, _, col_clear = st.columns([4, 4, 1])
    with col_clear:
        if st.button("🗑️ Temizle", key="clear_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()