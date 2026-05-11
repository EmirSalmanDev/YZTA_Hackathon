"""
6_reports.py — KoopPilot Performans Raporları.

Backend'den çekilen gerçek verilerle sipariş, stok ve gelir analizleri.
Plotly ile interaktif grafikler.
"""

import streamlit as st
import plotly.graph_objects as go
from utils.styles import setup_page, render_header, render_card_header, COLORS
from utils.auth import require_auth
from utils.api_client import get_dashboard_stats, get_orders, get_stock, get_critical_stock

setup_page("Raporlar")

if not require_auth():
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.")
        st.page_link("app.py", label="🚪 Giriş Sayfasına Git", use_container_width=True)
    st.stop()

stats = get_dashboard_stats()
orders = get_orders()
stock = get_stock()
critical = get_critical_stock()

render_header("Raporlar ve Analizler", "Operasyonel verilerinizi detaylı inceleyin.")

# --- KPI Satırı ---
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

# --- Grafik Satırı ---
col_pie, col_bar = st.columns(2)

# Sipariş Durum Dağılımı (Donut Chart)
with col_pie:
    with st.container(border=True):
        render_card_header("Sipariş Durum Dağılımı", "🎯")

        dist = stats.get("status_distribution", {})
        if dist:
            labels_map = {
                "pending": "Bekliyor",
                "shipped": "Kargoda",
                "delivered": "Teslim",
                "cancelled": "İptal",
            }
            colors_map = {
                "pending": "#F59E0B",
                "shipped": "#3B82F6",
                "delivered": "#10B981",
                "cancelled": "#EF4444",
            }

            labels = [labels_map.get(k, k) for k in dist.keys()]
            values = list(dist.values())
            colors = [colors_map.get(k, "#6B7280") for k in dist.keys()]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                marker_colors=colors,
                textinfo="label+percent",
                textfont_size=12,
                hoverinfo="label+value+percent",
            )])
            fig.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sipariş verisi bulunamadı.")

# Stok Durumu (Bar Chart)
with col_bar:
    with st.container(border=True):
        render_card_header("Stok Seviyeleri (İlk 15 Ürün)", "📊")

        if stock:
            sorted_stock = sorted(stock, key=lambda x: x.get("stock_amount", 0))[:15]
            names = [p.get("name", "?") for p in sorted_stock]
            amounts = [p.get("stock_amount", 0) for p in sorted_stock]
            thresholds = [p.get("critical_threshold", 0) for p in sorted_stock]

            bar_colors = [
                "#EF4444" if a <= t else "#10B981"
                for a, t in zip(amounts, thresholds)
            ]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=names,
                x=amounts,
                orientation="h",
                marker_color=bar_colors,
                text=[str(a) for a in amounts],
                textposition="auto",
                textfont_size=11,
            ))
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                xaxis_title="Stok Miktarı",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ürün verisi bulunamadı.")

st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

# --- Kritik Stok Tablosu ---
with st.container(border=True):
    render_card_header("Kritik Stok Detayları", "🚨")

    if critical:
        for p in critical:
            amt = p.get("stock_amount", 0)
            thr = p.get("critical_threshold", 1)
            pct = min(100, int((amt / max(thr, 1)) * 100))
            deficit = thr - amt
            bar_color = "#DC2626" if pct < 50 else "#D97706"

            st.markdown(f"""
            <div style="padding:10px 0; border-bottom:1px solid #F9FAFB;">
                <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;">
                    <span style="font-weight:600;">{p.get('name')}</span>
                    <span>
                        <span style="color:{bar_color}; font-weight:700;">{amt} {p.get('unit', '')}</span>
                        <span style="color:#9CA3AF; font-size:11px;"> / eşik: {thr}</span>
                        <span style="color:#DC2626; font-size:11px; font-weight:600; margin-left:8px;">
                            ({deficit} eksik)
                        </span>
                    </span>
                </div>
                <div style="width:100%; height:4px; background:#F3F4F6; border-radius:2px;">
                    <div style="width:{pct}%; height:100%; background:{bar_color}; border-radius:2px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Tüm ürünler normal stok seviyesinde.")

# --- Sipariş Gelir Dağılımı ---
st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
with st.container(border=True):
    render_card_header("Sipariş Gelir Özeti", "💰")

    if orders:
        status_revenue: dict[str, float] = {}
        status_count: dict[str, int] = {}
        for o in orders:
            s = o.get("status", "unknown")
            status_revenue[s] = status_revenue.get(s, 0) + o.get("total_price", 0)
            status_count[s] = status_count.get(s, 0) + 1

        labels_map = {
            "pending": "Bekliyor",
            "shipped": "Kargoda",
            "delivered": "Teslim",
            "cancelled": "İptal",
        }

        cols = st.columns(len(status_revenue))
        for i, (status, revenue) in enumerate(status_revenue.items()):
            with cols[i]:
                label = labels_map.get(status, status)
                count = status_count.get(status, 0)
                st.markdown(f"""
                <div style="text-align:center; padding:12px;">
                    <div style="font-size:11px; font-weight:700; color:{COLORS['text_light']}; text-transform:uppercase; letter-spacing:0.5px;">
                        {label}
                    </div>
                    <div style="font-size:22px; font-weight:800; color:{COLORS['text']}; margin:4px 0;">
                        ₺{revenue:,.0f}
                    </div>
                    <div style="font-size:12px; color:{COLORS['text_light']};">
                        {count} sipariş
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Sipariş verisi bulunamadı.")
