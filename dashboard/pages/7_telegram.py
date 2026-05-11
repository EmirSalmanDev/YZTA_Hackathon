"""
7_telegram.py — KoopPilot Telegram Bot Yönetimi.

Bot token'larını kaydetme, bağlantı durumunu gösterme,
ve Telegram bot kurulum rehberi.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_card_header, COLORS
from utils.auth import require_auth, update_user_settings

setup_page("Telegram")

if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

render_header("Telegram Bot Yönetimi", "Telegram botlarınızı yapılandırın ve yönetin.")

user = st.session_state.get("user", {})
user_id = user.get("id")

# --- Mevcut Token Durumları ---
admin_token = user.get("telegram_bot_token", "") or ""
customer_token = user.get("telegram_customer_bot_token", "") or ""

col_admin, col_customer = st.columns(2)

# --- Admin Bot Kartı ---
with col_admin:
    with st.container(border=True):
        render_card_header("Admin Bot", "🤖")

        has_admin = bool(admin_token)
        status_bg = "#F0FDF4" if has_admin else "#FEF2F2"
        status_border = "#BBF7D0" if has_admin else "#FECACA"
        status_color = "#166534" if has_admin else "#991B1B"
        status_dot = "#22C55E" if has_admin else "#EF4444"
        status_text = "Token Kayıtlı" if has_admin else "Token Girilmemiş"

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px;
                    background:{status_bg}; border:1px solid {status_border}; border-radius:8px;">
            <div style="width:8px; height:8px; background:{status_dot}; border-radius:50%;"></div>
            <span style="font-size:12px; color:{status_color}; font-weight:600;">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:13px; color:#6B7280; line-height:1.6; margin-bottom:12px;">
            İşletme yönetimi botu. Stok kontrolü, sipariş yönetimi,
            istatistik sorgulama ve doğal dil komutlarını destekler.
        </div>
        """, unsafe_allow_html=True)

        with st.form("admin_token_form", border=False):
            new_admin_token = st.text_input(
                "Admin Bot Token",
                value=admin_token,
                type="password",
                placeholder="1234567890:ABCDEfghIJKlmnOPQRstUVWxyz",
                help="BotFather'dan aldığınız admin bot token'ı",
            )
            submitted_admin = st.form_submit_button("💾 Admin Token Kaydet", use_container_width=True, type="primary")
            if submitted_admin and new_admin_token != admin_token:
                if user_id:
                    res = update_user_settings(user_id, telegram_bot_token=new_admin_token)
                    if res.get("success"):
                        st.session_state["user"]["telegram_bot_token"] = new_admin_token
                        st.success("✅ Admin bot token'ı kaydedildi!")
                        st.rerun()
                    else:
                        st.error(res.get("error", "Kayıt başarısız."))
                else:
                    st.error("Kullanıcı bilgisi bulunamadı.")

# --- Müşteri Bot Kartı ---
with col_customer:
    with st.container(border=True):
        render_card_header("Müşteri Bot", "👤")

        has_customer = bool(customer_token)
        status_bg = "#F0FDF4" if has_customer else "#FEF2F2"
        status_border = "#BBF7D0" if has_customer else "#FECACA"
        status_color = "#166534" if has_customer else "#991B1B"
        status_dot = "#22C55E" if has_customer else "#EF4444"
        status_text = "Token Kayıtlı" if has_customer else "Token Girilmemiş"

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px;
                    background:{status_bg}; border:1px solid {status_border}; border-radius:8px;">
            <div style="width:8px; height:8px; background:{status_dot}; border-radius:50%;"></div>
            <span style="font-size:12px; color:{status_color}; font-weight:600;">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:13px; color:#6B7280; line-height:1.6; margin-bottom:12px;">
            Müşteri self-servis botu. Sipariş sorgulama, kargo takip
            ve ürün bilgisi gibi işlemleri destekler.
        </div>
        """, unsafe_allow_html=True)

        with st.form("customer_token_form", border=False):
            new_customer_token = st.text_input(
                "Müşteri Bot Token",
                value=customer_token,
                type="password",
                placeholder="9876543210:ZYXWvuTSRqpONMlkjIHGfedCBA",
                help="BotFather'dan aldığınız müşteri bot token'ı",
            )
            submitted_customer = st.form_submit_button("💾 Müşteri Token Kaydet", use_container_width=True, type="primary")
            if submitted_customer and new_customer_token != customer_token:
                if user_id:
                    res = update_user_settings(user_id, telegram_customer_bot_token=new_customer_token)
                    if res.get("success"):
                        st.session_state["user"]["telegram_customer_bot_token"] = new_customer_token
                        st.success("✅ Müşteri bot token'ı kaydedildi!")
                        st.rerun()
                    else:
                        st.error(res.get("error", "Kayıt başarısız."))
                else:
                    st.error("Kullanıcı bilgisi bulunamadı.")

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

# --- Kurulum Rehberi ---
with st.container(border=True):
    render_card_header("Telegram Bot Kurulum Rehberi", "📖")

    st.markdown("""
    <div style="font-size:14px; color:#374151; line-height:1.8;">
    
    <div style="margin-bottom:16px;">
        <div style="font-weight:700; color:#111827; margin-bottom:4px;">1️⃣ BotFather'ı Açın</div>
        Telegram'da <a href="https://t.me/BotFather" target="_blank" style="color:#2D6A2E; font-weight:600;">@BotFather</a>'ı 
        arayın ve bir konuşma başlatın.
    </div>
    
    <div style="margin-bottom:16px;">
        <div style="font-weight:700; color:#111827; margin-bottom:4px;">2️⃣ Yeni Bot Oluşturun</div>
        <code>/newbot</code> komutunu gönderin. BotFather size bot adı ve kullanıcı adı soracaktır.
        <br><b>İki bot oluşturun:</b> Biri admin (örn: KoopPilot_Admin_Bot), biri müşteri (örn: KoopPilot_Bot).
    </div>
    
    <div style="margin-bottom:16px;">
        <div style="font-weight:700; color:#111827; margin-bottom:4px;">3️⃣ Token'ları Kopyalayın</div>
        BotFather size <code>1234567890:ABCDEfghIJKlmnOPQRstUVWxyz</code> formatında bir token verecektir.
        Bu token'ları yukarıdaki ilgili alanlara yapıştırın.
    </div>
    
    <div style="margin-bottom:16px;">
        <div style="font-weight:700; color:#111827; margin-bottom:4px;">4️⃣ Admin User ID</div>
        Admin botuna kimlerin erişebileceğini belirlemek için Telegram User ID'nizi bulmanız gerekir.
        <a href="https://t.me/userinfobot" target="_blank" style="color:#2D6A2E; font-weight:600;">@userinfobot</a>'a mesaj atarak ID'nizi öğrenebilirsiniz.
    </div>
    
    <div>
        <div style="font-weight:700; color:#111827; margin-bottom:4px;">5️⃣ Bot'u Başlatın</div>
        Token'ları kaydettikten sonra <code>.env</code> dosyasına ekleyin ve bot servisini başlatın:
        <br><code>python bot.py --mode both</code>
    </div>
    
    </div>
    """, unsafe_allow_html=True)

# --- Bot Komutları ---
st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
col_admin_cmds, col_customer_cmds = st.columns(2)

with col_admin_cmds:
    with st.container(border=True):
        render_card_header("Admin Bot Komutları", "⚡")
        commands = [
            ("/start", "Bot'u başlat, ana menü"),
            ("/stok", "Kritik stok uyarıları"),
            ("/siparisler", "Bekleyen siparişler"),
            ("/ozet", "Günlük iş özeti"),
            ("/yardim", "Komut listesi"),
        ]
        for cmd, desc in commands:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #F9FAFB;">
                <code style="font-size:13px; font-weight:600; color:#2D6A2E;">{cmd}</code>
                <span style="font-size:12px; color:#6B7280;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

with col_customer_cmds:
    with st.container(border=True):
        render_card_header("Müşteri Bot Komutları", "⚡")
        commands = [
            ("/start", "Bot'u başlat"),
            ("/siparis <no>", "Sipariş sorgula"),
            ("/kargo <takip_no>", "Kargo takip"),
            ("/urunler", "Ürün listesi"),
            ("/stok <ürün>", "Stok durumu"),
        ]
        for cmd, desc in commands:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #F9FAFB;">
                <code style="font-size:13px; font-weight:600; color:#2D6A2E;">{cmd}</code>
                <span style="font-size:12px; color:#6B7280;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)
