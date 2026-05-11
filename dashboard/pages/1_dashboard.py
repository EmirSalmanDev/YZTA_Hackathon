"""
1_dashboard.py — Ana Dashboard sayfası.
"""

import streamlit as st
from utils.styles import setup_page, render_header, render_card_header, status_badge, render_login_prompt, COLORS
from utils.auth import require_auth
from utils.api_client import get_dashboard_stats, get_orders, get_critical_stock, get_cargo_delays

setup_page("Dashboard")

if not require_auth():
    render_login_prompt()

# Data
stats = get_dashboard_stats()
orders = get_orders()
critical = get_critical_stock()

render_header("Dashboard", "Kooperatifinizin genel durumuna hızlı bir bakış.")

# --- KPIs ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.container(border=True):
        st.metric("Bugünkü Siparişler", str(stats.get("today_orders", 0)), f"+{stats.get('today_orders', 0)}")
with c2:
    with st.container(border=True):
        cc = stats.get("critical_stock_count", 0)
        st.metric("Kritik Stok", str(cc), f"{cc} ürün", delta_color="inverse")
with c3:
    with st.container(border=True):
        st.metric("Kargoda", str(stats.get("shipped_count", 0)), f"{stats.get('delay_count', 0)} gecikme", delta_color="inverse")
with c4:
    with st.container(border=True):
        rev = stats.get("today_revenue", 0)
        st.metric("Bugünkü Gelir", f"₺{rev:,.0f}", "Günlük")

st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

# --- AI & Tasks ---
col_ai, col_tasks = st.columns([3, 2])

with col_ai:
    with st.container(border=True):
        render_card_header("AI Günlük Özet", "✨")
        st.markdown(f"""
        <div style="font-size:15px; color:#374151; line-height:1.7; padding:4px 0;">
            Bugün kooperatifinizde <b>{stats.get('today_orders', 0)}</b> sipariş alındı, 
            toplam <b>₺{stats.get('today_revenue', 0):,.0f}</b> gelir elde edildi. 
            Stok tarafında <b>{stats.get('critical_stock_count', 0)}</b> ürün kritik seviyede.
            {f"<br><span style='color:#DC2626; font-weight:600;'>⚠️ {stats.get('delay_count', 0)} gecikmiş kargo var.</span>" if stats.get('delay_count', 0) > 0 else ""}
        </div>
        """, unsafe_allow_html=True)

with col_tasks:
    with st.container(border=True):
        render_card_header("Hızlı Görevler", "📋")
        tasks = []
        if stats.get("delay_count", 0) > 0: tasks.append(("🔴", "Geciken kargolar", "Acil"))
        if stats.get("critical_stock_count", 0) > 0: tasks.append(("🟡", "Stok güncelleme", "Önemli"))
        if stats.get("pending_count", 0) > 0: tasks.append(("⚪", f"{stats['pending_count']} onay bekliyor", "Bekliyor"))
        
        for icon, text, badge in tasks[:3]:
            st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid #F9FAFB;">
                <span style="font-size:13px; color:#374151;">{icon} {text}</span>
                <span style="font-size:10px; font-weight:700; background:#F3F4F6; padding:2px 8px; border-radius:10px;">{badge}</span>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

# --- Lists ---
col_orders, col_stock = st.columns(2)

with col_orders:
    with st.container(border=True):
        render_card_header("Son Siparişler", "📦")
        recent = sorted(orders, key=lambda o: o.get("created_at", ""), reverse=True)[:5]
        for o in recent:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #F9FAFB;">
                <div>
                    <div style="font-size:14px; font-weight:700;">#{o.get('id')}</div>
                    <div style="font-size:12px; color:#6B7280;">₺{o.get('total_price', 0):,.2f}</div>
                </div>
                {status_badge(o.get('status', 'pending'))}
            </div>
            """, unsafe_allow_html=True)

with col_stock:
    with st.container(border=True):
        render_card_header("Kritik Stoklar", "🚨")
        if critical:
            for p in critical[:5]:
                amt, thr = p.get('stock_amount', 0), p.get('critical_threshold', 1)
                pct = min(100, int((amt / max(thr, 1)) * 100))
                color = "#DC2626" if pct < 50 else "#D97706"
                st.markdown(f"""
                <div style="padding:10px 0; border-bottom:1px solid #F9FAFB;">
                    <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;">
                        <span style="font-weight:600;">{p.get('name')}</span>
                        <span style="color:{color}; font-weight:700;">{amt} {p.get('unit')}</span>
                    </div>
                    <div style="width:100%; height:4px; background:#F3F4F6; border-radius:2px;">
                        <div style="width:{pct}%; height:100%; background:{color}; border-radius:2px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Stoklar normal.")
