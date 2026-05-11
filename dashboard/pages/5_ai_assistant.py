"""
5_ai_assistant.py — KoopPilot AI İşletme Asistanı.

Backend'deki admin agent'a bağlanarak doğal dil sorguları işler.
Stok, sipariş, kargo, istatistik gibi tüm işletme verilerine
AI üzerinden erişim sağlar.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_card_header, COLORS
from utils.auth import require_auth
from utils.api_client import admin_chat, health_check

setup_page("AI Asistan")

if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

# --- Başlık & Backend Durum ---
render_header("AI İşletme Asistanı", "İşletmenizle ilgili sorular sorun, analizler isteyin.")

# Backend bağlantı durumu
health = health_check()
is_online = health.get("status") == "ok"

if is_online:
    db_info = health.get("db", {})
    product_count = db_info.get("products", "?")
    order_count = db_info.get("orders", "?")
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:20px; padding:10px 16px; 
                background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px;">
        <div style="width:8px; height:8px; background:#22C55E; border-radius:50%;"></div>
        <span style="font-size:13px; color:#166534; font-weight:600;">Backend Aktif</span>
        <span style="font-size:12px; color:#166534; margin-left:auto;">
            {product_count} ürün · {order_count} sipariş
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:20px; padding:10px 16px; 
                background:#FEF2F2; border:1px solid #FECACA; border-radius:10px;">
        <div style="width:8px; height:8px; background:#EF4444; border-radius:50%;"></div>
        <span style="font-size:13px; color:#991B1B; font-weight:600;">Backend Çevrimdışı</span>
        <span style="font-size:12px; color:#991B1B; margin-left:auto;">
            AI asistan yanıt veremez
        </span>
    </div>
    """, unsafe_allow_html=True)

# --- Hızlı Sorular ---
st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
quick_cols = st.columns(4)

quick_questions = [
    ("📦", "Bugünkü sipariş özeti"),
    ("🚨", "Kritik stokları göster"),
    ("🚚", "Geciken kargolar var mı?"),
    ("📊", "Günlük iş raporu hazırla"),
]

for i, (icon, question) in enumerate(quick_questions):
    with quick_cols[i]:
        if st.button(f"{icon} {question}", key=f"quick_{i}", use_container_width=True):
            if "pending_quick" not in st.session_state:
                st.session_state.pending_quick = question

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

# --- Chat Geçmişi ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat mesajlarını göster
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        # Boş state — hoşgeldin mesajı
        st.markdown(f"""
        <div style="text-align:center; padding:60px 20px; color:{COLORS['text_light']};">
            <div style="font-size:48px; margin-bottom:16px;">🌿</div>
            <h3 style="color:{COLORS['text']}; font-size:18px; margin:0 0 8px;">Merhaba! Ben KoopPilot AI Asistanınız.</h3>
            <p style="font-size:14px; max-width:500px; margin:0 auto; line-height:1.6;">
                İşletmenizle ilgili her türlü soruyu yanıtlayabilirim.<br>
                Stok durumu, sipariş takibi, kargo bilgisi ve daha fazlası için soru sorun.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            role = "assistant" if msg["role"] == "assistant" else "user"
            with st.chat_message(role, avatar="🌿" if role == "assistant" else None):
                st.markdown(msg["content"])

# --- Mesaj Gönderme ---
def _send_message(message: str) -> None:
    """Mesajı backend'e gönder ve yanıtı al."""
    # Kullanıcı mesajını ekle
    st.session_state.chat_history.append({"role": "user", "content": message})

    # Backend'e gönder
    with st.chat_message("user"):
        st.markdown(message)

    with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("🤔 AI yanıtınızı hazırlıyor..."):
            response = admin_chat(message)
        st.markdown(response)

    # Yanıtı kaydet
    st.session_state.chat_history.append({"role": "assistant", "content": response})


# Hızlı soru varsa işle
if "pending_quick" in st.session_state:
    quick_msg = st.session_state.pop("pending_quick")
    _send_message(quick_msg)
    st.rerun()

# Chat input
if prompt := st.chat_input("Sorunuzu yazın... Örn: 'Kaç kilo domates stoğum var?'"):
    _send_message(prompt)
    st.rerun()

# --- Alt Bilgi: Sohbet Temizleme ---
if st.session_state.chat_history:
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    _, _, col_clear = st.columns([4, 4, 1])
    with col_clear:
        if st.button("🗑️ Temizle", key="clear_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
