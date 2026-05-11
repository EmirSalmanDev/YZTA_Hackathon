"""
styles.py — KoopPilot Premium Design System.
"""

import streamlit as st

COLORS = {
    "primary":       "#2D6A2E",
    "primary_light": "#F0FDF4",
    "bg":            "#FAFBFC",
    "border":        "#E5E7EB",
    "text":          "#111827",
    "text_light":    "#6B7280",
}

def inject_global_css() -> None:
    """CSS bloklarındaki süslü parantezleri f-string için kaçış karakterleriyle düzeltir."""
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        * {{ font-family: 'Inter', sans-serif !important; }}
        
        .stApp {{ background-color: {COLORS["bg"]}; }}

        /* Sidebar Modernizasyonu */
        section[data-testid="stSidebar"] {{
            background-color: white !important;
            border-right: 1px solid {COLORS["border"]} !important;
        }}

        /* === PREMIUM CARD SİSTEMİ === */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: white !important;
            border: 1px solid {COLORS["border"]} !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        }}

        div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlockBorderWrapper"] {{
            box-shadow: none !important;
            border: 1px solid #F3F4F6 !important;
        }}

        /* Butonlar */
        .stButton > button {{
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }}

        .stButton > button[kind="primary"] {{
            background-color: {COLORS["primary"]} !important;
            border: none !important;
        }}

        /* Tipografi */
        p, span, div, label {{
            color: #374151;
        }}

        /* Metrikler */
        [data-testid="stMetric"] {{
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            font-size: 11px !important;
            font-weight: 700 !important;
            color: {COLORS["text_light"]} !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }}

        [data-testid="stMetricValue"] {{
            font-size: 24px !important;
            font-weight: 800 !important;
            color: {COLORS["text"]} !important;
        }}

        /* Kart Başlığı */
        .card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid #F3F4F6;
        }}
        .card-header h3 {{
            font-size: 15px !important;
            font-weight: 700 !important;
            margin: 0 !important;
            color: {COLORS["text"]} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def setup_page(title: str) -> None:
    inject_global_css()
    _render_sidebar()

def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 10px 0 20px; text-align: center;">
            <span style="font-size: 32px;">🌿</span>
            <h2 style="margin: 0; font-size: 20px; color: {COLORS["text"]};">KoopPilot</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("authenticated"):
            user = st.session_state.get("user", {})
            st.markdown(f"""
            <div style="background:{COLORS["primary_light"]}; padding:12px; border-radius:10px; margin-bottom:20px;">
                <div style="font-size:10px; font-weight:700; color:{COLORS["primary"]}; text-transform:uppercase;">Aktif İşletme</div>
                <div style="font-size:14px; font-weight:700; color:{COLORS["text"]};">{user.get('business_name', 'Deneme')}</div>
            </div>
            """, unsafe_allow_html=True)

def render_header(title: str, subtitle: str = "") -> None:
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h1 style="font-size: 28px; margin: 0;">{title}</h1>
        <p style="color: {COLORS["text_light"]}; margin: 4px 0 0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_card_header(title: str, icon: str = "") -> None:
    st.markdown(f"""
    <div class="card-header">
        <span>{icon}</span>
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_login_prompt() -> None:
    """Oturum açmamış kullanıcılar için profesyonel yönlendirme kartı."""
    st.markdown("<div style='margin-top:60px;'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align:center; padding:10px 0 20px;">
                <div style="font-size:40px; margin-bottom:10px;">🔐</div>
                <h3 style="margin:0; font-size:18px;">Oturum Açmanız Gerekiyor</h3>
                <p style="color:#6B7280; font-size:14px; margin:8px 0 20px;">Bu sayfayı görüntülemek için lütfen hesabınıza giriş yapın.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("app.py", label="🚪 Giriş Ekranına Dön", use_container_width=True)
    st.stop()

def status_badge(status: str) -> str:
    badges = {
        "pending":   ("#D97706", "#FFFBEB", "Bekliyor"),
        "shipped":   ("#2563EB", "#EFF6FF", "Kargoda"),
        "delivered": ("#059669", "#F0FDF4", "Teslim"),
        "cancelled": ("#DC2626", "#FEF2F2", "İptal"),
    }
    fg, bg, label = badges.get(status, ("#6B7280", "#F3F4F6", status))
    return f'<span style="background:{bg}; color:{fg}; padding:2px 10px; border-radius:100px; font-size:11px; font-weight:700;">{label}</span>'
