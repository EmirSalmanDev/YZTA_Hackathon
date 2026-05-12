"""
6_reports.py — KoopPilot Performans Raporları.
"""
import streamlit as st
import plotly.graph_objects as go
from utils.styles import setup_page, render_header, render_card_header, render_progress_bar, COLORS
from utils.auth import require_auth
from utils.api_client import get_dashboard_stats, get_orders, get_stock, get_critical_stock

setup_page("Raporlar")

if not require_auth():
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

stats    = get_dashboard_stats()
orders   = get_orders()
stock    = get_stock()
critical = get_critical_stock()

render_header("Raporlar ve Analizler", "Operasyonel verilerinizi detaylı inceleyin.")

# ── KPI ───────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.container(border=True):
        st.metric("Toplam Sipariş", str(stats.get("total_orders", 0)))
with c2:
    with st.container(border=True):
        st.metric("Toplam Gelir", f"₺{stats.get('total_revenue', 0):,.0f}")
with c3:
    with st.container(border=True):
        st.metric("Toplam Ürün", str(stats.get("total_products", 0)))
with c4:
    with st.container(border=True):
        st.metric("Kritik Stok", str(stats.get("critical_stock_count", 0)), delta_color="inverse")

st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

# ── Grafikler ─────────────────────────────────────────────────────────────────
col_pie, col_bar = st.columns(2)

with col_pie:
    with st.container(border=True):
        render_card_header("Sipariş Durum Dağılımı", "🎯")
        dist = stats.get("status_distribution", {})
        if dist:
            lmap = {"pending": "Bekliyor", "shipped": "Kargoda", "delivered": "Teslim", "cancelled": "İptal"}
            cmap = {"pending": "#F59E0B", "shipped": "#3B82F6", "delivered": "#10B981", "cancelled": "#EF4444"}
            fig = go.Figure(data=[go.Pie(
                labels=[lmap.get(k, k) for k in dist],
                values=list(dist.values()),
                hole=0.45,
                marker_colors=[cmap.get(k, "#6B7280") for k in dist],
                textinfo="label+percent", textfont_size=12,
                hoverinfo="label+value+percent",
            )])
            fig.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10),
                              height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sipariş verisi bulunamadı.")

with col_bar:
    with st.container(border=True):
        render_card_header("Stok Seviyeleri (İlk 15 Ürün)", "📊")
        if stock:
            ss = sorted(stock, key=lambda x: x.get("stock_amount", 0))[:15]
            amounts = [p.get("stock_amount", 0) for p in ss]
            thresholds = [p.get("critical_threshold", 0) for p in ss]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=[p.get("name","?") for p in ss], x=amounts, orientation="h",
                marker_color=["#EF4444" if a<=t else "#10B981" for a,t in zip(amounts,thresholds)],
                text=[str(a) for a in amounts], textposition="auto", textfont_size=11,
            ))
            fig.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=280,
                              xaxis_title="Stok Miktarı", paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ürün verisi bulunamadı.")

st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

# ── Kritik Stok Tablosu ───────────────────────────────────────────────────────
with st.container(border=True):
    render_card_header("Kritik Stok Detayları", "🚨")
    if critical:
        for p in critical:
            amt = p.get("stock_amount", 0)
            thr = p.get("critical_threshold", 1)
            pct = min(100, int((amt / max(thr, 1)) * 100))
            deficit = thr - amt
            bar_color = "#DC2626" if pct < 50 else "#D97706"
            name = p.get('name', '')
            unit = p.get('unit', '')
            st.markdown(
                f'<div style="padding:10px 0;border-bottom:1px solid #F0F4F1;">'
                f'<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;">'
                f'<span style="font-weight:700;color:{COLORS["text"]};">{name}</span>'
                f'<span>'
                f'<span style="color:{bar_color};font-weight:700;">{amt} {unit}</span>'
                f'<span style="color:#9CA3AF;font-size:11px;"> / eşik: {thr}</span>'
                f'<span style="color:#DC2626;font-size:11px;font-weight:600;margin-left:8px;">({deficit} eksik)</span>'
                f'</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            render_progress_bar(pct, bar_color, height=5)
    else:
        st.success("✅ Tüm ürünler normal stok seviyesinde.")

st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

# ── Sipariş Gelir Özeti ───────────────────────────────────────────────────────
with st.container(border=True):
    render_card_header("Sipariş Gelir Özeti", "💰")
    if orders:
        status_revenue: dict[str, float] = {}
        status_count: dict[str, int] = {}
        for o in orders:
            s = o.get("status", "unknown")
            status_revenue[s] = status_revenue.get(s, 0) + o.get("total_price", 0)
            status_count[s] = status_count.get(s, 0) + 1

        lmap = {"pending": "Bekliyor", "shipped": "Kargoda", "delivered": "Teslim", "cancelled": "İptal"}
        cmap = {"pending": "#D97706", "shipped": "#2563EB", "delivered": "#059669", "cancelled": "#DC2626"}

        cols = st.columns(len(status_revenue))
        for i, (status, revenue) in enumerate(status_revenue.items()):
            with cols[i]:
                label = lmap.get(status, status)
                count = status_count.get(status, 0)
                accent = cmap.get(status, COLORS["primary"])
                st.markdown(
                    f'<div style="text-align:center;padding:16px 12px;background:#FAFCFA;'
                    f'border-radius:14px;border:1px solid #E2EBE4;">'
                    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_light"]};'
                    f'text-transform:uppercase;letter-spacing:0.5px;">{label}</div>'
                    f'<div style="font-size:24px;font-weight:900;color:{accent};margin:6px 0;">₺{revenue:,.0f}</div>'
                    f'<div style="font-size:12px;color:{COLORS["text_light"]};">{count} sipariş</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.info("Sipariş verisi bulunamadı.")