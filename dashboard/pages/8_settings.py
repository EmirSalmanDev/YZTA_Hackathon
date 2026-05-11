"""
8_settings.py — KoopPilot Hesap Ayarları.

İşletme bilgileri güncelleme, şifre değiştirme,
backend sağlık kontrolü ve oturum kapatma.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_card_header, COLORS
from utils.auth import require_auth, update_user_settings, change_password
from utils.api_client import health_check

setup_page("Ayarlar")

if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

render_header("Ayarlar", "Hesap ve işletme ayarlarınızı yönetin.")

user = st.session_state.get("user", {})
user_id = user.get("id")

col_left, col_right = st.columns(2)

# --- İşletme Bilgileri ---
with col_left:
    with st.container(border=True):
        render_card_header("İşletme Bilgileri", "🏢")

        with st.form("business_form", border=False):
            business_name = st.text_input(
                "İşletme Adı",
                value=user.get("business_name", ""),
                placeholder="Örn: Yeşil Kooperatif",
            )
            phone = st.text_input(
                "Telefon",
                value=user.get("phone", ""),
                placeholder="05XX XXX XX XX",
            )
            st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("💾 Bilgileri Güncelle", use_container_width=True, type="primary")

            if submitted and user_id:
                res = update_user_settings(user_id, business_name=business_name, phone=phone)
                if res.get("success"):
                    st.session_state["user"]["business_name"] = business_name
                    st.session_state["user"]["phone"] = phone
                    st.success("✅ İşletme bilgileri güncellendi!")
                else:
                    st.error(res.get("error", "Güncelleme başarısız."))

# --- Şifre Değiştirme ---
with col_right:
    with st.container(border=True):
        render_card_header("Şifre Değiştir", "🔒")

        with st.form("password_form", border=False):
            current_pw = st.text_input("Mevcut Şifre", type="password")
            new_pw = st.text_input("Yeni Şifre", type="password")
            confirm_pw = st.text_input("Yeni Şifre (Tekrar)", type="password")
            st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
            pw_submitted = st.form_submit_button("🔐 Şifre Değiştir", use_container_width=True)

            if pw_submitted:
                if not current_pw or not new_pw:
                    st.error("Tüm alanları doldurunuz.")
                elif new_pw != confirm_pw:
                    st.error("Yeni şifreler eşleşmiyor.")
                elif len(new_pw) < 4:
                    st.error("Şifre en az 4 karakter olmalıdır.")
                else:
                    email = user.get("email", "")
                    res = change_password(email, current_pw, new_pw)
                    if res.get("success"):
                        st.success("✅ Şifreniz başarıyla değiştirildi!")
                    else:
                        st.error(res.get("error", "Şifre değiştirme başarısız."))

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

# --- Hesap Bilgileri & Sistem Durumu ---
col_account, col_system = st.columns(2)

with col_account:
    with st.container(border=True):
        render_card_header("Hesap Bilgileri", "👤")
        info_items = [
            ("E-posta", user.get("email", "—")),
            ("İşletme", user.get("business_name", "—")),
            ("Telefon", user.get("phone", "—") or "Belirtilmemiş"),
        ]
        for label, value in info_items:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #F9FAFB;">
                <span style="font-size:13px; color:{COLORS['text_light']}; font-weight:500;">{label}</span>
                <span style="font-size:13px; color:{COLORS['text']}; font-weight:600;">{value}</span>
            </div>
            """, unsafe_allow_html=True)

with col_system:
    with st.container(border=True):
        render_card_header("Sistem Durumu", "🖥️")

        health = health_check()
        is_online = health.get("status") == "ok"

        backend_dot = "#22C55E" if is_online else "#EF4444"
        backend_text = "Aktif" if is_online else "Çevrimdışı"

        st.markdown(f"""
        <div style="padding:8px 0; border-bottom:1px solid #F9FAFB;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:13px; color:{COLORS['text_light']};">Backend API</span>
                <div style="display:flex; align-items:center; gap:6px;">
                    <div style="width:8px; height:8px; background:{backend_dot}; border-radius:50%;"></div>
                    <span style="font-size:13px; font-weight:600;">{backend_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if is_online:
            db = health.get("db", {})
            items = [
                ("Ürünler", db.get("products", "?")),
                ("Siparişler", db.get("orders", "?")),
                ("Müşteriler", db.get("customers", "?")),
            ]
            for label, count in items:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #F9FAFB;">
                    <span style="font-size:13px; color:{COLORS['text_light']};">{label}</span>
                    <span style="font-size:13px; font-weight:700; color:{COLORS['primary']};">{count}</span>
                </div>
                """, unsafe_allow_html=True)

# --- Çıkış ---
st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
_, _, col_logout = st.columns([3, 3, 1.5])
with col_logout:
    if st.button("🚪 Oturumu Kapat", key="logout_btn", use_container_width=True, type="primary"):
        st.session_state.clear()
        st.rerun()
