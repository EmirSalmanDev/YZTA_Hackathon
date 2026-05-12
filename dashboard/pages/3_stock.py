"""3_stock.py — Stok Yönetimi"""
import streamlit as st
from utils.styles import (
    setup_page, render_header, render_card_header,
    render_progress_bar, render_empty, render_login_prompt, COLORS
)
from utils.auth import require_auth
from utils.api_client import get_stock, update_stock

setup_page("Stok")
if not require_auth():
    render_login_prompt(); st.stop()

stock = get_stock()
render_header("Stok Yönetimi", f"Toplam {len(stock)} çeşit ürün takip ediliyor.",
              back_page="pages/1_dashboard.py", back_label="← Dashboard'a Dön")

# ── Özet ─────────────────────────────────────────────────────────────────────
critical_count = sum(1 for p in stock if p.get("stock_amount",0) <= p.get("critical_threshold",0))
normal_count   = len(stock) - critical_count

s1, s2, s3 = st.columns(3)
for col, val, lbl, bg, fg in [
    (s1, len(stock),     "Toplam Ürün",  "#EEF5EE", COLORS["primary"]),
    (s2, critical_count, "Kritik Stok",  "#FEF9C3", COLORS["warning"]),
    (s3, normal_count,   "Normal Stok",  "#DCFCE7", COLORS["success"]),
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

st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

# ── Filtre ────────────────────────────────────────────────────────────────────
with st.container(border=True):
    c1, c2 = st.columns([3, 1])
    search    = c1.text_input("Ürün Ara", placeholder="Ürün adı yazın…", label_visibility="collapsed")
    show_only = c2.selectbox("Göster", ["Tümü","Sadece Kritik"], label_visibility="collapsed")

filtered_stock = stock
if search:
    filtered_stock = [p for p in filtered_stock if search.lower() in p.get("name","").lower()]
if show_only == "Sadece Kritik":
    filtered_stock = [p for p in filtered_stock if p.get("stock_amount",0) <= p.get("critical_threshold",0)]

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

if not filtered_stock:
    render_empty("Ürün bulunamadı.")
else:
    for p in filtered_stock:
        amt = p.get("stock_amount", 0)
        thr = p.get("critical_threshold", 5)
        pct = min(100, int((amt / max(thr, 1)) * 100))
        is_crit   = amt <= thr
        bar_color = COLORS["danger"] if is_crit else COLORS["success"]
        badge_bg  = "#FEE2E2" if is_crit else "#DCFCE7"
        badge_fg  = COLORS["danger"] if is_crit else COLORS["success"]
        badge_lbl = "KRİTİK" if is_crit else "NORMAL"

        with st.container(border=True):
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:10px;">
                    <div style="width:44px;height:44px;background:{badge_bg};
                                border-radius:14px;display:flex;align-items:center;
                                justify-content:center;font-size:22px;flex-shrink:0;">
                        {'⚠️' if is_crit else '🌿'}</div>
                    <div style="flex:1;">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
                            <span style="font-size:15px;font-weight:800;color:{COLORS['text']};">
                                {p.get('name')}</span>
                            <span style="font-size:10px;font-weight:800;background:{badge_bg};
                                         color:{badge_fg};padding:2px 8px;border-radius:20px;">
                                {badge_lbl}</span>
                        </div>
                        <div style="font-size:12px;color:{COLORS['text_light']};font-weight:500;">
                            ID #{p.get('id')} &nbsp;·&nbsp; ₺{p.get('price',0):,.2f}/{p.get('unit','adet')}
                            &nbsp;·&nbsp; Eşik:
                            <strong style="color:{badge_fg};">{thr} {p.get('unit','')}</strong>
                        </div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;">
                        <div style="font-size:22px;font-weight:900;color:{bar_color};">{amt}</div>
                        <div style="font-size:11px;color:{COLORS['text_light']};">{p.get('unit','adet')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                render_progress_bar(pct, bar_color, height=8)

            with col_btn:
                st.markdown("<div style='padding-top:8px;'></div>", unsafe_allow_html=True)
                if st.button("✏️ Güncelle", key=f"e_{p['id']}", use_container_width=True):
                    st.session_state[f"edit_{p['id']}"] = not st.session_state.get(f"edit_{p['id']}", False)

            if st.session_state.get(f"edit_{p['id']}"):
                st.markdown("<div style='padding-top:10px;border-top:1px solid #EEF5EE;margin-top:8px;'></div>",
                            unsafe_allow_html=True)
                with st.form(f"f_{p['id']}"):
                    fc1, fc2 = st.columns([3, 1])
                    new_amt = fc1.number_input(
                        f"Yeni miktar ({p.get('unit','adet')})",
                        value=float(amt), min_value=0.0, step=1.0
                    )
                    fc2.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
                    if fc2.form_submit_button("💾 Kaydet", use_container_width=True, type="primary"):
                        update_stock(p["id"], int(new_amt))
                        st.session_state.pop(f"edit_{p['id']}", None)
                        st.rerun()