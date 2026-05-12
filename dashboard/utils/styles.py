"""
utils/styles.py — KoopPilot Global Stil & Yardımcı Fonksiyonlar
"""
import streamlit as st

COLORS = {
    "primary":       "#2D6A4F",
    "primary_light": "#52B788",
    "primary_dark":  "#1B4332",
    "accent":        "#95D5B2",
    "accent2":       "#B7E4C7",
    "bg":            "#F5F7F2",
    "bg_card":       "#FFFFFF",
    "border":        "#E2EBE4",
    "text":          "#1A2E1F",
    "text_mid":      "#4A6741",
    "text_light":    "#8FAF8A",
    "danger":        "#DC2626",
    "warning":       "#D97706",
    "success":       "#059669",
    "info":          "#2563EB",
    "shipped":       "#2563EB",
    "pending":       "#D97706",
    "delivered":     "#059669",
    "cancelled":     "#DC2626",
}

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Nunito', sans-serif !important;
    background: #F5F7F2 !important;
    color: #1A2E1F !important;
}

/* Header tamamen şeffaf */
header[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
    pointer-events: none !important;
}

/* collapsedControl — görünmez tut ama tıklanabilir bırak */
[data-testid="collapsedControl"] {
    opacity: 0 !important;
    /* pointer-events: none KALDIRILDI — .click() çalışsın diye */
}

/* Toolbar & menü gizle */
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1280px !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2EBE4 !important;
}
[data-testid="stSidebar"] .block-container { padding: 0 !important; }
[data-testid="stSidebarNav"] a {
    font-family: 'Nunito', sans-serif !important;
    font-size: 13.5px !important; font-weight: 600 !important;
    color: #4A6741 !important; border-radius: 10px !important;
    margin: 1px 10px !important; padding: 9px 14px !important;
    transition: all 0.15s ease !important;
    text-transform: capitalize !important;
}
[data-testid="stSidebarNav"] a:hover { background: #EEF5EE !important; color: #2D6A4F !important; }
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(135deg,#D8EFDF,#C7E8D0) !important;
    color: #1B4332 !important; font-weight: 800 !important;
}

/* Metric */
[data-testid="metric-container"] {
    background: #FFFFFF !important; border: 1px solid #E2EBE4 !important;
    border-radius: 18px !important; padding: 20px 22px 18px !important;
    box-shadow: 0 2px 8px rgba(45,106,79,0.07) !important;
    transition: transform 0.18s, box-shadow 0.18s !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(45,106,79,0.13) !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 11px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.7px !important; color: #8FAF8A !important;
}
[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: 900 !important; color: #1A2E1F !important; }

/* Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px !important; border: 1px solid #E2EBE4 !important;
    background: #FFFFFF !important; box-shadow: 0 2px 10px rgba(45,106,79,0.06) !important;
    transition: box-shadow 0.2s !important; overflow: hidden !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 24px rgba(45,106,79,0.11) !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
    font-size: 13px !important; border-radius: 50px !important;
    padding: 8px 22px !important; border: none !important; transition: all 0.18s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#2D6A4F,#40916C) !important;
    color: white !important; box-shadow: 0 3px 10px rgba(45,106,79,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg,#1B4332,#2D6A4F) !important;
    box-shadow: 0 5px 16px rgba(45,106,79,0.45) !important; transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: #F0F7F2 !important; color: #2D6A4F !important; border: 1.5px solid #B7E4C7 !important;
}
.stButton > button[kind="secondary"]:hover { background: #D8EFDF !important; }

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
    font-family: 'Nunito', sans-serif !important; border-radius: 12px !important;
    border: 1.5px solid #E2EBE4 !important; font-size: 14px !important;
    background: #FAFCFA !important; transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #52B788 !important; box-shadow: 0 0 0 3px rgba(82,183,136,0.18) !important;
}
.stSelectbox > div > div {
    border-radius: 12px !important; border: 1.5px solid #E2EBE4 !important;
    font-family: 'Nunito', sans-serif !important; background: #FAFCFA !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #F0F7F2 !important; border-radius: 50px !important;
    padding: 4px !important; gap: 4px !important; border: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 50px !important; font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important; font-size: 13px !important;
    color: #4A6741 !important; padding: 8px 20px !important;
    border: none !important; background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important; color: #1B4332 !important;
    box-shadow: 0 2px 8px rgba(45,106,79,0.15) !important;
}

/* Chat */
[data-testid="stChatMessage"] {
    border-radius: 16px !important; border: 1px solid #EEF5EE !important;
    background: #FAFCFA !important; padding: 14px 18px !important; margin: 6px 0 !important;
}
[data-testid="stChatInputTextArea"] {
    border-radius: 50px !important; border: 2px solid #E2EBE4 !important;
    background: white !important; font-family: 'Nunito', sans-serif !important;
}

/* Misc */
hr { border: none !important; border-top: 1px solid #E2EBE4 !important; margin: 16px 0 !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F5F7F2; }
::-webkit-scrollbar-thumb { background: #B7E4C7; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #52B788; }
.main .block-container { animation: fadeUp 0.3s ease both; }
@keyframes fadeUp { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
.stSpinner > div { border-top-color: #2D6A4F !important; }
[data-testid="stForm"] { border: none !important; background: transparent !important; }
.js-plotly-plot .plotly .modebar { display: none !important; }
</style>
"""

# ── Status badge ──────────────────────────────────────────────────────────────
_STATUS_CFG = {
    "pending":   ("#FEF9C3", "#92400E", "⏳ Bekliyor"),
    "shipped":   ("#DBEAFE", "#1E40AF", "🚚 Kargoda"),
    "delivered": ("#DCFCE7", "#166534", "✅ Teslim"),
    "cancelled": ("#FEE2E2", "#991B1B", "❌ İptal"),
}

def status_badge(status: str) -> str:
    bg, fg, label = _STATUS_CFG.get(status, ("#F3F4F6", "#374151", status.title()))
    return (
        f'<span style="background:{bg}; color:{fg}; padding:3px 11px; '
        f'border-radius:20px; font-size:11px; font-weight:800;">{label}</span>'
    )

# ── Setup ─────────────────────────────────────────────────────────────────────
def setup_page(title: str) -> None:
    st.set_page_config(
        page_title=f"{title} — KoopPilot",
        page_icon="🌿", layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    _render_sidebar_brand()
    _inject_sidebar_toggle()

def inject_global_css() -> None:
    """Geriye dönük uyumluluk — app.py için."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Floating sidebar toggle ───────────────────────────────────────────────────
def _inject_sidebar_toggle() -> None:
    """
    Parent document'a yeşil floating bir buton ekler.
    Sidebar açıkken buton kaybolur, kapalıyken belirir.
    Birden fazla selector deneyerek Streamlit'in toggle butonunu bulur.
    """
    st.components.v1.html("""
    <!DOCTYPE html>
    <html>
    <head><style>
        body { margin: 0; padding: 0; overflow: hidden; }
    </style></head>
    <body>
    <script>
    (function() {
        var BTN_ID = 'koop-sidebar-toggle-btn';

        function isSidebarOpen() {
            try {
                var sidebar = parent.document.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) return false;
                return sidebar.getBoundingClientRect().width > 100;
            } catch(e) {
                return false;
            }
        }

        function updateVisibility() {
            var btn = parent.document.getElementById(BTN_ID);
            if (!btn) return;
            if (isSidebarOpen()) {
                btn.style.opacity = '0';
                btn.style.transform = 'scale(0.8)';
                btn.style.pointerEvents = 'none';
            } else {
                btn.style.opacity = '1';
                btn.style.transform = 'scale(1)';
                btn.style.pointerEvents = 'auto';
            }
        }

        function clickSidebarToggle() {
            /*
             * Streamlit farklı sürümlerde farklı selector kullanıyor.
             * Sırayla hepsini dene, ilk bulduğuna tıkla.
             */
            var selectors = [
                '[data-testid="collapsedControl"]',
                '[data-testid="stSidebarCollapsedControl"]',
                'button[aria-label="Open sidebar"]',
                'button[aria-label="Kenar çubuğunu aç"]',
                'button[kind="header"][aria-expanded="false"]',
                'section[data-testid="stSidebar"] ~ div button',
                'div[data-testid="stDecoration"] ~ div button',
            ];

            var found = null;
            for (var i = 0; i < selectors.length; i++) {
                var el = parent.document.querySelector(selectors[i]);
                if (el) { found = el; break; }
            }

            if (found) {
                /*
                 * CSS pointer-events:none engel çıkarabilir.
                 * Geçici olarak kaldır, tıkla, geri koy.
                 */
                var prev = found.style.pointerEvents;
                found.style.pointerEvents = 'auto';
                found.click();
                found.style.pointerEvents = prev;
            } else {
                /*
                 * Fallback: Streamlit'in sidebar'ını doğrudan manipüle et.
                 * sidebar wrapper'ındaki aria-expanded attribute'unu değiştir.
                 */
                var sidebar = parent.document.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    var isOpen = sidebar.getBoundingClientRect().width > 100;
                    if (isOpen) {
                        sidebar.style.marginLeft = '-' + sidebar.getBoundingClientRect().width + 'px';
                        sidebar.style.transition = 'margin-left 0.3s ease';
                    } else {
                        sidebar.style.marginLeft = '0';
                        sidebar.style.transition = 'margin-left 0.3s ease';
                    }
                }
            }

            setTimeout(updateVisibility, 350);
        }

        function createButton() {
            if (parent.document.getElementById(BTN_ID)) {
                updateVisibility();
                return;
            }

            var btn = parent.document.createElement('button');
            btn.id = BTN_ID;
            btn.title = 'Menüyü Aç / Kapat';
            btn.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';

            btn.style.cssText = [
                'position:fixed',
                'top:14px',
                'left:14px',
                'z-index:9999999',
                'width:48px',
                'height:48px',
                'border-radius:16px',
                'border:2px solid rgba(255,255,255,0.3)',
                'cursor:pointer',
                'background:linear-gradient(135deg,#2D6A4F 0%,#52B788 100%)',
                'color:white',
                'display:flex',
                'align-items:center',
                'justify-content:center',
                'box-shadow:0 6px 24px rgba(45,106,79,0.5),0 2px 8px rgba(0,0,0,0.15)',
                'transition:opacity 0.25s ease,transform 0.25s ease,box-shadow 0.2s ease',
                'outline:none',
            ].join(';');

            btn.onmouseenter = function() {
                btn.style.boxShadow = '0 10px 32px rgba(45,106,79,0.65),0 4px 12px rgba(0,0,0,0.2)';
                btn.style.background = 'linear-gradient(135deg,#1B4332 0%,#2D6A4F 100%)';
            };
            btn.onmouseleave = function() {
                btn.style.boxShadow = '0 6px 24px rgba(45,106,79,0.5),0 2px 8px rgba(0,0,0,0.15)';
                btn.style.background = 'linear-gradient(135deg,#2D6A4F 0%,#52B788 100%)';
            };
            btn.onmousedown = function() {
                btn.style.transform = 'scale(0.93)';
            };
            btn.onmouseup = function() {
                btn.style.transform = 'scale(1)';
            };

            btn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                clickSidebarToggle();
            };

            parent.document.body.appendChild(btn);
            updateVisibility();
        }

        // İlk oluşturma
        createButton();

        // Sidebar boyutunu izle (ResizeObserver)
        try {
            var sidebar = parent.document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                var ro = new parent.ResizeObserver(function() { updateVisibility(); });
                ro.observe(sidebar);
            }
        } catch(e) {}

        // DOM değişikliklerini izle (sayfa geçişleri)
        try {
            var mo = new MutationObserver(function() {
                createButton();
                updateVisibility();
            });
            mo.observe(parent.document.body, {
                childList: true,
                subtree: true
            });
        } catch(e) {}

        // Periyodik fallback
        setInterval(function() {
            createButton();
            updateVisibility();
        }, 1500);

    })();
    </script>
    </body>
    </html>
    """, height=0, scrolling=False)

# ── Sidebar brand ──────────────────────────────────────────────────────────────
def _render_sidebar_brand() -> None:
    st.sidebar.markdown("""
    <div style="padding:20px 16px 16px; border-bottom:1px solid #E2EBE4; margin-bottom:8px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:40px; height:40px;
                        background:linear-gradient(135deg,#2D6A4F,#52B788);
                        border-radius:14px; display:flex; align-items:center;
                        justify-content:center; font-size:22px;
                        box-shadow:0 3px 10px rgba(45,106,79,0.3);">🌿</div>
            <div>
                <div style="font-size:18px; font-weight:900; color:#1A2E1F;">KoopPilot</div>
                <div style="font-size:10px; color:#8FAF8A; font-weight:600; letter-spacing:0.3px;">
                    Kadın Kooperatifleri İçin Akıllı Asistan</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div style="margin:8px 10px; padding:14px 16px;
                background:linear-gradient(135deg,#EEF5EA,#D8EFDF);
                border-radius:16px; border:1px solid #C7E8D0;">
        <div style="font-size:13px; font-weight:800; color:#1B4332; margin-bottom:4px;">
            🌸 Birlikte üretin,</div>
        <div style="font-size:13px; font-weight:800; color:#1B4332;">
            birlikte güçlenin.</div>
        <div style="font-size:11px; color:#4A6741; margin-top:6px; font-weight:500;">
            Kooperatif destek hattı aktif</div>
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
def render_header(title: str, subtitle: str = "",
                  back_page: str = "", back_label: str = "← Geri Dön") -> None:
    sub_html = (
        f'<p style="font-size:13px; color:{COLORS["text_light"]}; margin:3px 0 0; font-weight:500;">'
        f'{subtitle}</p>'
    ) if subtitle else ""

    st.markdown(f"""
    <div style="margin-bottom:24px; padding-bottom:16px; border-bottom:2px solid #E2EBE4;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
            <div style="width:52px; height:52px;
                        background:linear-gradient(135deg,#2D6A4F,#52B788);
                        border-radius:18px; display:flex; align-items:center;
                        justify-content:center; font-size:28px;
                        box-shadow:0 4px 12px rgba(45,106,79,0.35);">🌿</div>
            <div>
                <div style="font-size:26px; font-weight:900; color:#1A2E1F; line-height:1.1;">
                    KoopPilot</div>
                <div style="font-size:12px; color:#8FAF8A; font-weight:600; letter-spacing:0.3px;">
                    Kadın Kooperatifleri İçin Akıllı Asistan</div>
            </div>
        </div>
        <h1 style="font-size:28px; font-weight:900; color:#1A2E1F;
                   margin:0; line-height:1.2;">{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

    if back_page:
        col_back, _ = st.columns([1, 5])
        with col_back:
            st.page_link(back_page, label=back_label, use_container_width=True)
        st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# ── Card header ───────────────────────────────────────────────────────────────
def render_card_header(title: str, icon: str = "", subtitle: str = "") -> None:
    prefix = f"{icon} " if icon else ""
    if subtitle:
        st.markdown(f"**{prefix}{title}**")
        st.caption(subtitle)
    else:
        st.markdown(f"**{prefix}{title}**")
    st.divider()

# ── KPI card ──────────────────────────────────────────────────────────────────
def render_kpi(label: str, value: str, delta: str = "",
               delta_up: bool = True, icon: str = "", accent: str = "") -> None:
    accent = accent or COLORS["primary"]
    dc = COLORS["success"] if delta_up else COLORS["warning"]
    da = "↑" if delta_up else "↓"
    delta_html = (
        f'<div style="font-size:11px; font-weight:700; color:{dc}; margin-top:5px;">{da} {delta}</div>'
    ) if delta else ""
    icon_html = (
        f'<div style="position:absolute; top:16px; right:16px; width:46px; height:46px; '
        f'background:linear-gradient(135deg,{accent}18,{accent}30); '
        f'border-radius:14px; display:flex; align-items:center; justify-content:center; '
        f'font-size:22px;">{icon}</div>'
    ) if icon else ""
    st.markdown(f"""
    <div style="background:#FFFFFF; border-radius:18px; padding:20px 22px 18px;
                border:1px solid #E2EBE4; position:relative; overflow:hidden;
                box-shadow:0 2px 10px rgba(45,106,79,0.07); border-top:3px solid {accent};">
        {icon_html}
        <div style="font-size:10px; font-weight:800; text-transform:uppercase;
                    letter-spacing:0.8px; color:{COLORS['text_light']}; margin-bottom:8px;">{label}</div>
        <div style="font-size:30px; font-weight:900; color:{COLORS['text']}; line-height:1;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# ── Progress bar ──────────────────────────────────────────────────────────────
def render_progress_bar(pct: int, color: str = "", height: int = 6) -> None:
    color = color or COLORS["primary_light"]
    st.markdown(f"""
    <div style="width:100%; height:{height}px; background:#EEF5EE;
                border-radius:{height}px; overflow:hidden; margin:5px 0 2px;">
        <div style="width:{min(pct,100)}%; height:100%; background:{color};
                    border-radius:{height}px;"></div>
    </div>
    """, unsafe_allow_html=True)

# ── Login prompt ──────────────────────────────────────────────────────────────
def render_login_prompt() -> None:
    st.markdown("<div style='margin-top:60px;'></div>", unsafe_allow_html=True)
    col = st.columns([1, 2, 1])[1]
    with col:
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align:center; padding:36px 16px 16px;">
                <div style="font-size:54px; margin-bottom:14px;">🌿</div>
                <h2 style="font-size:20px; font-weight:900; color:{COLORS['text']}; margin:0 0 6px;">
                    KoopPilot'a Hoş Geldiniz</h2>
                <p style="font-size:13px; color:{COLORS['text_light']}; margin:0 0 22px;">
                    Bu sayfayı görüntülemek için giriş yapmanız gerekiyor.</p>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("app.py", label="🚪 Giriş Yap", use_container_width=True)

# ── Status pill ───────────────────────────────────────────────────────────────
def render_status_pill(online: bool, label_on: str = "Backend Aktif",
                       label_off: str = "Backend Çevrimdışı", extra: str = "") -> None:
    if online:
        bg, border, color, dot = "#F0FDF4", "#BBF7D0", "#166534", "#22C55E"
        label = label_on
    else:
        bg, border, color, dot = "#FEF2F2", "#FECACA", "#991B1B", "#EF4444"
        label = label_off
    extra_html = (
        f'<span style="font-size:12px; color:{color}; margin-left:auto; opacity:0.85;">{extra}</span>'
    ) if extra else ""
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:20px;
                padding:10px 16px; background:{bg}; border:1px solid {border}; border-radius:12px;">
        <div style="width:8px; height:8px; background:{dot}; border-radius:50%;
                    box-shadow:0 0 0 3px {dot}40; flex-shrink:0;"></div>
        <span style="font-size:13px; color:{color}; font-weight:700;">{label}</span>
        {extra_html}
    </div>
    """, unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────────────────────
def render_empty(message: str = "Veri bulunamadı.", icon: str = "🌱") -> None:
    st.markdown(f"""
    <div style="text-align:center; padding:48px 20px; color:{COLORS['text_light']};">
        <div style="font-size:40px; margin-bottom:12px; opacity:0.6;">{icon}</div>
        <div style="font-size:14px; font-weight:600;">{message}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Section divider ───────────────────────────────────────────────────────────
def render_section(title: str, icon: str = "") -> None:
    icon_html = f'<span style="margin-right:6px;">{icon}</span>' if icon else ""
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin:22px 0 12px;">
        <div style="font-size:11px; font-weight:800; color:{COLORS['text_mid']};
                    text-transform:uppercase; letter-spacing:0.7px; white-space:nowrap;">
            {icon_html}{title}</div>
        <div style="flex:1; height:1px; background:#E2EBE4;"></div>
    </div>
    """, unsafe_allow_html=True)

# ── Info banner ───────────────────────────────────────────────────────────────
def render_info_banner(title: str, body: str, icon: str = "ℹ️",
                       bg: str = "#EFF6FF", border: str = "#BFDBFE",
                       text_color: str = "#1D4ED8") -> None:
    st.markdown(f"""
    <div style="background:{bg}; border:1px solid {border}; border-radius:14px;
                padding:14px 18px; margin-bottom:16px; display:flex; gap:12px; align-items:flex-start;">
        <span style="font-size:20px; flex-shrink:0;">{icon}</span>
        <div>
            <div style="font-size:13px; font-weight:800; color:{text_color};">{title}</div>
            <div style="font-size:12px; color:{text_color}; opacity:0.8; margin-top:3px; line-height:1.6;">
                {body}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)