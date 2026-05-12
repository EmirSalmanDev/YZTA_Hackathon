"""1_dashboard.py — Ana Dashboard"""
import streamlit as st
from utils.styles import (
    setup_page, render_header, render_card_header, render_kpi,
    render_progress_bar, render_empty, status_badge, render_login_prompt, COLORS
)
from utils.auth import require_auth
from utils.api_client import get_dashboard_stats, get_orders, get_critical_stock

setup_page("Dashboard")
if not require_auth():
    render_login_prompt(); st.stop()

stats    = get_dashboard_stats()
orders   = get_orders()
critical = get_critical_stock()

render_header("Dashboard", "Kooperatifinizin genel durumuna hızlı bir bakış.")

# ── KPI ───────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi("Bugünkü Siparişler", str(stats.get("today_orders", 0)),
               f"+{stats.get('today_orders',0)} sipariş", True, "📦", COLORS["primary"])
with c2:
    cc = stats.get("critical_stock_count", 0)
    render_kpi("Kritik Stok", str(cc), f"{cc} ürün aksiyon bekliyor", False, "⚠️", COLORS["warning"])
with c3:
    dc = stats.get("delay_count", 0)
    render_kpi("Kargoda", str(stats.get("shipped_count", 0)),
               f"{dc} gecikme riski" if dc else "Sorunsuz", dc == 0, "🚚", COLORS["info"])
with c4:
    rev = stats.get("today_revenue", 0)
    render_kpi("Bugünkü Gelir", f"₺{rev:,.0f}", "Günlük toplam", True, "💰", COLORS["success"])

st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

# ── AI Özet + Görevler ────────────────────────────────────────────────────────
col_ai, col_tasks = st.columns([3, 2])

with col_ai:
    with st.container(border=True):
        render_card_header("AI Günlük Özet", "✨", "Yapay zeka destekli analiz")
        delay_html = (
            f'<span style="color:#DC2626;font-weight:700;">⚠️ {stats.get("delay_count",0)} gecikmiş kargo tespit edildi.</span>'
            if stats.get('delay_count', 0) > 0
            else '<span style="color:#059669;font-weight:700;">✅ Kargo durumu normal.</span>'
        )
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#EEF5EA,#D8EFDF);border-radius:14px;padding:18px 20px;">'
            f'<div style="font-size:14px;color:#1B4332;line-height:1.9;font-weight:500;">'
            f'Bugün kooperatifinizde <strong>{stats.get("today_orders",0)}</strong> sipariş alındı, '
            f'toplam <strong>₺{stats.get("today_revenue",0):,.0f}</strong> gelir elde edildi. '
            f'<strong style="color:#D97706;">{stats.get("critical_stock_count",0)}</strong> ürün kritik stok seviyesinde.<br>'
            f'{delay_html}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        if st.button("💬 AI Asistana Sor", type="primary"):
            st.switch_page("pages/5_ai_assistant.py")

with col_tasks:
    with st.container(border=True):
        render_card_header("Hızlı Görevler", "📋", "Bugün yapılacaklar")
        tasks = []
        if stats.get("delay_count", 0) > 0:
            tasks.append(("⚠️", "#FEE2E2", "#991B1B", "Geciken kargolar", "Acil"))
        if stats.get("critical_stock_count", 0) > 0:
            tasks.append(("📦", "#FEF9C3", "#92400E", "Stok güncelleme", "Önemli"))
        if stats.get("pending_count", 0) > 0:
            tasks.append(("📋", "#DBEAFE", "#1E40AF", f"{stats['pending_count']} sipariş onayı", "Bekliyor"))
        if tasks:
            for icon, bg, fg, text, badge in tasks[:4]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;justify-content:space-between;'
                    f'padding:10px 12px;margin:4px 0;background:{bg};border-radius:10px;border:1px solid {fg}22;">'
                    f'<span style="font-size:13px;color:{fg};font-weight:600;">{icon} {text}</span>'
                    f'<span style="font-size:10px;font-weight:800;background:{fg}22;color:{fg};'
                    f'padding:3px 9px;border-radius:20px;">{badge}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            render_empty("Tüm görevler tamamlandı! 🎉", "🎉")

st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

# ── Son Siparişler + Kritik Stok ─────────────────────────────────────────────
col_orders, col_stock = st.columns(2)

with col_orders:
    with st.container(border=True):
        render_card_header("Son Siparişler", "📦", f"{len(orders)} sipariş")
        recent = sorted(orders, key=lambda o: o.get("created_at",""), reverse=True)[:6]
        if recent:
            for o in recent:
                bdg = status_badge(o.get('status', 'pending'))
                oid = o.get('id', '')
                date = o.get('created_at','')[:10]
                price = o.get('total_price', 0)
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'padding:10px 4px;border-bottom:1px solid #F0F4F1;">'
                    f'<div style="display:flex;align-items:center;gap:10px;">'
                    f'<div style="width:36px;height:36px;background:#EEF5EE;border-radius:10px;'
                    f'display:flex;align-items:center;justify-content:center;font-size:16px;">📋</div>'
                    f'<div>'
                    f'<div style="font-size:13px;font-weight:700;color:{COLORS["text"]};">Sipariş #{oid}</div>'
                    f'<div style="font-size:11px;color:{COLORS["text_light"]};">{date}</div>'
                    f'</div>'
                    f'</div>'
                    f'<div style="display:flex;align-items:center;gap:8px;">'
                    f'<span style="font-size:14px;font-weight:800;color:{COLORS["text"]};">₺{price:,.0f}</span>'
                    f'{bdg}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            if st.button("Tüm Siparişler →", key="goto_orders"):
                st.switch_page("pages/2_orders.py")
        else:
            render_empty("Henüz sipariş yok.", "📭")

with col_stock:
    with st.container(border=True):
        render_card_header("Kritik Stoklar", "🚨", f"{len(critical)} ürün aksiyon bekliyor")
        if critical:
            for p in critical[:6]:
                amt = p.get('stock_amount', 0)
                thr = p.get('critical_threshold', 1)
                pct = min(100, int((amt / max(thr, 1)) * 100))
                color = COLORS["danger"] if pct < 50 else COLORS["warning"]
                name = p.get('name', '')
                unit = p.get('unit', '')
                st.markdown(
                    f'<div style="padding:10px 4px;border-bottom:1px solid #F0F4F1;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px;">'
                    f'<span style="font-weight:700;color:{COLORS["text"]};">{name}</span>'
                    f'<span style="color:{color};font-weight:800;">{amt} {unit}'
                    f'<span style="color:{COLORS["text_light"]};font-weight:400;font-size:10px;"> / {thr}</span>'
                    f'</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                render_progress_bar(pct, color)
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            if st.button("Stok Yönetimine Git →", key="goto_stock"):
                st.switch_page("pages/3_stock.py")
        else:
            st.markdown(
                f'<div style="text-align:center;padding:32px;color:{COLORS["text_light"]};">'
                f'<div style="font-size:32px;margin-bottom:8px;">✅</div>'
                f'<div style="font-weight:600;">Tüm stoklar normal seviyede</div>'
                f'</div>',
                unsafe_allow_html=True,
            )