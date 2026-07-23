"""Static configuration, CSS themes, and reference lists for the Streamlit app."""


PAGE_CONFIG = {
    "page_title": "Heliopolis-AI | Solar Intel",
    "page_icon": "◆",
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
}


def get_css(is_dark: bool) -> str:
    """Return the full custom CSS block for the selected theme."""
    bg_color = "#09090b" if is_dark else "#ffffff"
    bg_subtle = "#0c0c0f" if is_dark else "#f9fafb"
    card_color = "#0c0c0f" if is_dark else "#ffffff"
    border_color = "#1e1e24" if is_dark else "#e4e4e7"
    border_subtle = "#16161a" if is_dark else "#f0f0f2"
    text_color = "#fafafa" if is_dark else "#09090b"
    text_muted = "#71717a"
    text_dim = "#52525b" if is_dark else "#a1a1aa"
    shadow_style = "none" if is_dark else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"
    green_color = "#22c55e" if is_dark else "#16a34a"
    green_muted = "rgba(34,197,94,0.12)" if is_dark else "rgba(22,163,74,0.08)"
    red_color = "#ef4444" if is_dark else "#dc2626"
    red_muted = "rgba(239,68,68,0.12)" if is_dark else "rgba(220,38,38,0.08)"
    amber_color = "#f59e0b" if is_dark else "#d97706"
    amber_muted = "rgba(245,158,11,0.12)" if is_dark else "rgba(217,119,6,0.08)"

    return f"""
<style>
:root {{
    --bg: {bg_color};
    --bg-subtle: {bg_subtle};
    --card: {card_color};
    --border: {border_color};
    --border-subtle: {border_subtle};
    --text: {text_color};
    --text-muted: {text_muted};
    --text-dim: {text_dim};
    --accent: #2563eb;
    --accent-muted: #1d4ed8;
    --green: {green_color};
    --green-muted: {green_muted};
    --red: {red_color};
    --red-muted: {red_muted};
    --amber: {amber_color};
    --amber-muted: {amber_muted};
    --shadow: {shadow_style};
    --radius: 10px;
}}

/* Hide Streamlit chrome */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}

.block-container {{
    padding: 1.5rem 2.5rem 3rem !important;
    max-width: 1400px !important;
}}

[data-testid="stHorizontalBlock"] {{
    gap: 1.25rem !important;
}}

/* Brand Styling */
.brand {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}}
.brand-icon {{
    color: var(--accent);
    font-size: 1.6rem;
    font-weight: 700;
}}
.brand-name {{
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text);
}}
.brand-badge {{
    background: rgba(37,99,235,0.12);
    color: var(--accent);
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    margin-left: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Tabs Customization */
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.825rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.1rem !important;
    border: 1px solid transparent !important;
    border-radius: 7px !important;
    transition: all 0.2s ease;
}}
button[data-baseweb="tab"]:hover {{
    color: var(--text) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--text) !important;
    background: var(--card) !important;
    border-color: var(--border) !important;
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
    display: none !important;
}}
[data-baseweb="tab-list"] {{
    gap: 4px !important;
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 3px !important;
    margin-bottom: 1.5rem !important;
}}

/* Custom Cards */
.card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.25rem;
}}
.card-title {{
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
.card-subtitle {{
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
}}

/* KPI Metric Cards */
.metric-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow);
}}
.metric-label {{
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}}
.metric-value {{
    font-size: 1.85rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.03em;
    margin: 0.2rem 0;
}}
.metric-delta {{
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
}}
.delta-up {{ color: var(--green); background: var(--green-muted); }}
.delta-down {{ color: var(--red); background: var(--red-muted); }}
.delta-warn {{ color: var(--amber); background: var(--amber-muted); }}

/* Data Tables */
.data-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.8rem;
    margin-top: 0.5rem;
}}
.data-table th {{
    text-align: left;
    padding: 0.65rem 0.8rem;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border);
}}
.data-table td {{
    padding: 0.7rem 0.8rem;
    color: var(--text);
    border-bottom: 1px solid var(--border-subtle);
}}
.data-table tr:last-child td {{
    border-bottom: none;
}}

/* Status Badges */
.badge {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
}}
.badge-green {{ color: var(--green); background: var(--green-muted); }}
.badge-red {{ color: var(--red); background: var(--red-muted); }}
.badge-amber {{ color: var(--amber); background: var(--amber-muted); }}
.badge-blue {{ color: var(--accent); background: rgba(37,99,235,0.1); }}

/* SEDA Checklist Styles */
.checklist-item {{
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 0.8rem;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.checklist-item:last-child {{
    border-bottom: none;
}}
.checklist-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
}}
</style>
"""


STATE_LIST = ["Perak", "Kedah", "Kelantan", "Selangor", "Johor"]
ZONING_LIST = ["Pertanian", "Bangunan", "Perindustrian"]
SLOPE_PROFILES = [
    "Optimal Flat Plain (2.1° mean)",
    "Rolling Hills (8.5° mean)",
    "Severe Ridge (37.7° mean)",
]

SAMPLE_OWNERS = [
    {"name": "Ahmad Bin Ismail", "id": "650212-08-5431", "share": "11/120"},
    {"name": "Wan Fatimah Binti Wan Ali", "id": "701103-08-5222", "share": "15/120"},
    {"name": "Siti Aminah Binti Ahmad", "id": "930415-08-6112", "share": "14/120"},
    {"name": "Solarvest Development Sdn Bhd", "id": "1234567-U", "share": "40/120"},
    {"name": "Lee Chong Wei", "id": "821021-10-5431", "share": "40/120"},
]
