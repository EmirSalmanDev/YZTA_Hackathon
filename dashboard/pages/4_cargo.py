"""4_cargo.py — Kargo Takibi"""
import streamlit as st
from utils.styles import (
    setup_page, render_header, render_card_header,
    render_empty, render_login_prompt, COLORS
)
from utils.auth import require_auth
from utils.api_client import get_orders

setup_page("Kargo")
if not require_auth():
    render_login_prompt(); st.stop()

orders   = get_orders()
shipped  = [o for o in orders if o.get("status") == "shipped"]
delivered = [o for o in orders if o.get("status") == "delivered"]
delayed  = [o for o in orders if o.get("status") == "delayed"]

render_header("Kargo Yönetimi", f"{len(shipped)} aktif gönderi takip ediliyor.",
              back_page="pages/1_dashboard.py", back_label="← Dashboard'a Dön")

# ── Özet ─────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
for col, val, lbl, bg, fg in [
    (c1, len(shipped),   "Yolda",         "#DBEAFE", COLORS["info"]),
    (c2, len(delayed),   "Gecikme Riski", "#FEE2E2", COLORS["danger"]),
    (c3, len(delivered), "Teslim Edildi", "#DCFCE7", COLORS["success"]),
]:
    with col:
        st.markdown(f"""
        <div style="background:{bg};border-radius:16px;padding:14px 18px;
                    text-align:center;border:1px solid {fg}22;">
            <div style="font-size:26px;font-weight:900;color:{fg};">{val}</div>
            <div style="font-size:11px;font-weight:700;color:{fg};margin-top:2px;
                        text-transform:uppercase;letter-spacing:0.4px;">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

if not shipped:
    render_empty("Aktif kargo bulunmuyor.", "🚚")
else:
    with st.container(border=True):
        render_card_header("Aktif Gönderiler", "🚚", f"{len(shipped)} kargo yolda")
        for o in shipped:
            oid      = o.get("id","?")
            tracking = o.get("cargo_tracking_id","—")
            date     = o.get("created_at","")[:10]
            delivery = o.get("delivery_date","—")
            price    = o.get("total_price", 0)
            is_late  = o.get("status") == "delayed"
            sbg  = "#FEE2E2" if is_late else "#DBEAFE"
            sfg  = COLORS["danger"] if is_late else COLORS["info"]
            slbl = "⚠️ Gecikme Riski" if is_late else "🚚 Yolda"

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;padding:14px 6px;
                        border-bottom:1px solid #F0F4F1;">
                <div style="width:44px;height:44px;background:{sbg};border-radius:14px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:22px;flex-shrink:0;">
                    {'⚠️' if is_late else '📦'}</div>
                <div style="flex:1;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
                        <span style="font-size:15px;font-weight:800;color:{COLORS['text']};">
                            Sipariş #{oid}</span>
                        <span style="font-size:10px;font-weight:800;background:{sbg};
                                     color:{sfg};padding:2px 9px;border-radius:20px;">{slbl}</span>
                    </div>
                    <div style="font-size:12px;color:{COLORS['text_light']};font-weight:500;">
                        📦 {tracking} &nbsp;·&nbsp; 📅 {date}
                        {f'&nbsp;·&nbsp; 🎯 Tahmini: {delivery}' if delivery and delivery != '—' else ''}
                    </div>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <div style="font-size:16px;font-weight:800;color:{COLORS['primary']};">
                        ₺{price:,.0f}</div>
                    <div style="font-size:11px;color:{COLORS['text_light']};">tutar</div>
                </div>
            </div>
            """, unsafe_allow_html=True)