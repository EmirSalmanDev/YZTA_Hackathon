"""
app.py — KoopPilot Dashboard Ana Giriş Sayfası.
"""

import streamlit as st
from utils.styles import setup_page, inject_global_css, render_header, COLORS
from utils.auth import login_user, register_user, ensure_demo_user

# Sayfa Ayarları
st.set_page_config(
    page_title="KoopPilot | Yönetim",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Tasarım Hazırlığı
inject_global_css()
ensure_demo_user()

def main():
    # Zaten giriş yapılmışsa Dashboard'a yönlendir
    if st.session_state.get("authenticated"):
        st.switch_page("pages/1_dashboard.py")
        st.stop()

    # --- UI ---
    _, col, _ = st.columns([1, 2.5, 1])
    
    with col:
        st.markdown("<div style='margin-top:60px;'></div>", unsafe_allow_html=True)
        
        # Ana Logo ve Başlık (Kutu dışında, ferah)
        st.markdown("""
        <div style="text-align:center; margin-bottom:40px;">
            <div style="font-size:60px; margin-bottom:10px;">🌿</div>
            <h1 style="font-size:32px; font-weight:800; color:#111827; margin:0;">KoopPilot</h1>
            <p style="color:#6B7280; font-size:15px; margin-top:8px;">Kooperatif Yönetiminde Akıllı Asistanınız</p>
        </div>
        """, unsafe_allow_html=True)

        # Giriş/Kayıt Kartı (Tek ve Net)
        with st.container(border=True):
            tab_login, tab_reg = st.tabs(["Giriş Yap", "Kayıt Ol"])
            
            with tab_login:
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
                with st.form("login_form", border=False):
                    email = st.text_input("E-posta", placeholder="deneme@gmail.com")
                    password = st.text_input("Şifre", type="password", placeholder="••••••••")
                    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                    submit = st.form_submit_button("Giriş Yap", type="primary", use_container_width=True)
                    
                    if submit:
                        res = login_user(email, password)
                        if res.get("success"):
                            # KRİTİK: Session State Güncelleme
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = res["user"]
                            st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                            st.rerun()
                        else:
                            st.error(res.get("error", "E-posta veya şifre hatalı."))
            
            with tab_reg:
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
                with st.form("register_form", border=False):
                    b_name = st.text_input("İşletme Adı", placeholder="Örn: Yeşil Kooperatif")
                    reg_email = st.text_input("E-posta Adresi")
                    reg_pw = st.text_input("Şifre Belirleyin", type="password")
                    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                    reg_submit = st.form_submit_button("Hesabımı Oluştur", use_container_width=True)
                    
                    if reg_submit:
                        res = register_user(b_name, reg_email, reg_pw)
                        if res.get("success"):
                            st.success("Hesabınız oluşturuldu! Şimdi giriş yapabilirsiniz.")
                        else:
                            st.error(res.get("error", "Kayıt sırasında bir hata oluştu."))

        # Alt Bilgi
        st.markdown("""
        <div style="text-align:center; margin-top:30px; color:#9CA3AF; font-size:12px;">
            &copy; 2026 KoopPilot AI. Tüm hakları saklıdır.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
