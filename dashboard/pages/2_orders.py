"""2_orders.py — Sipariş Yönetimi"""
import streamlit as st
from utils.styles import (
    setup_page, render_header, render_card_header,
    render_empty, status_badge, render_login_prompt, COLORS
)
from utils.auth import require_auth
from utils.api_client import get_orders, update_order_status

setup_page("Siparişler")
if not require_auth():
    render_login_prompt(); st.stop()

orders = get_orders()
render_header("Sipariş Yönetimi", f"Toplam {len(orders)} sipariş listeleniyor.",
              back_page="pages/1_dashboard.py", back_label="← Dashboard'a Dön")

# ── Özet sayaçlar ─────────────────────────────────────────────────────────────
status_counts = {}
for o in orders:
    s = o.get("status", "pending")
    status_counts[s] = status_counts.get(s, 0) + 1

_pill = {
    "pending":   ("#FEF9C3", "#92400E", "⏳ Bekliyor"),
    "shipped":   ("#DBEAFE", "#1E40AF", "🚚 Kargoda"),
    "delivered": ("#DCFCE7", "#166534", "✅ Teslim"),
    "cancelled": ("#FEE2E2", "#991B1B", "❌ İptal"),
}
cols = st.columns(4)
for col, (key, (bg, fg, lbl)) in zip(cols, _pill.items()):
    with col:
        cnt = status_counts.get(key, 0)
        st.markdown(
            f'<div style="background:{bg};border-radius:16px;padding:14px 18px;'
            f'text-align:center;border:1px solid {fg}22;margin-bottom:4px;">'
            f'<div style="font-size:24px;font-weight:900;color:{fg};">{cnt}</div>'
            f'<div style="font-size:11px;font-weight:700;color:{fg};margin-top:2px;">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

# ── Filtre ────────────────────────────────────────────────────────────────────
with st.container(border=True):
    render_card_header("Filtrele", "🔍")
    c1, c2, c3 = st.columns([2, 2, 1])
    search        = c1.text_input("Sipariş Ara", placeholder="Sipariş numarası…", label_visibility="collapsed")
    status_filter = c2.selectbox("Durum", ["Hepsi", "Bekliyor", "Kargoda", "Teslim", "İptal"], label_visibility="collapsed")
    with c3:
        st.markdown(
            f'<div style="background:#EEF5EE;border-radius:10px;padding:8px 12px;'
            f'text-align:center;margin-top:4px;">'
            f'<span style="font-size:13px;font-weight:700;color:{COLORS["primary"]};">{len(orders)} toplam</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

# ── Filtrele & Listele ────────────────────────────────────────────────────────
_tr = {"Bekliyor":"pending","Kargoda":"shipped","Teslim":"delivered","İptal":"cancelled"}
filtered = orders if status_filter == "Hepsi" else [o for o in orders if o.get("status") == _tr.get(status_filter,"")]
if search:
    filtered = [o for o in filtered if search.lstrip("#") in str(o.get("id",""))]

if not filtered:
    render_empty("Filtreye uygun sipariş bulunamadı.", "📭")
else:
    for o in sorted(filtered, key=lambda x: x.get("created_at",""), reverse=True):
        status   = o.get("status", "pending")
        oid      = o.get("id", "?")
        price    = o.get("total_price", 0)
        date     = o.get("created_at","")[:16].replace("T"," ")
        cid      = o.get("customer_id","?")
        tracking = o.get("cargo_tracking_id")
        badge_html  = status_badge(status)
        tracking_html = f'&nbsp;·&nbsp; 📦 {tracking}' if tracking else ''

        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(
                    f'<div style="display:flex;align-items:flex-start;gap:14px;">'
                    f'<div style="width:44px;height:44px;background:linear-gradient(135deg,#D8EFDF,#B7E4C7);'
                    f'border-radius:14px;display:flex;align-items:center;justify-content:center;'
                    f'font-size:20px;flex-shrink:0;">📋</div>'
                    f'<div>'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
                    f'<span style="font-size:17px;font-weight:900;color:{COLORS["text"]};">Sipariş #{oid}</span>'
                    f'{badge_html}'
                    f'</div>'
                    f'<div style="font-size:12px;color:{COLORS["text_light"]};font-weight:500;">'
                    f'📅 {date} &nbsp;·&nbsp; 👤 Müşteri #{cid}{tracking_html}'
                    f'</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with right:
                st.markdown(
                    f'<div style="text-align:right;padding-top:4px;">'
                    f'<div style="font-size:22px;font-weight:900;color:{COLORS["primary"]};">₺{price:,.2f}</div>'
                    f'<div style="font-size:11px;color:{COLORS["text_light"]};margin-top:2px;">Toplam tutar</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            b1, b2, b3, _ = st.columns([1,1,1,3])
            with b1:
                if status == "pending" and st.button("✅ Onayla", key=f"a_{oid}", use_container_width=True, type="primary"):
                    update_order_status(oid, "shipped"); st.rerun()
            with b2:
                if status == "shipped" and st.button("📬 Teslim", key=f"d_{oid}", use_container_width=True):
                    update_order_status(oid, "delivered"); st.rerun()
            with b3:
                if status in ("pending","shipped") and st.button("❌ İptal", key=f"c_{oid}", use_container_width=True):
                    update_order_status(oid, "cancelled"); st.rerun()