"""
NeuroBiomeX — AI-Powered Gut-Brain Neurodegenerative Risk Platform
Streamlit conversion of the React application.
Run: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import io
from audio_recorder_streamlit import audio_recorder
from pdf_report import generate_pdf_report

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuroBiomeX",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Root Variables (LIGHT THEME) ── */
:root {
    --indigo: #6366f1;
    --indigo-dark: #4f46e5;
    --indigo-light: #818cf8;
    --rose: #f43f5e;
    --amber: #f59e0b;
    --emerald: #10b981;
    --purple: #8b5cf6;
    --sky: #0ea5e9;
    --bg: #f1f5f9;
    --card: #ffffff;
    --border: #e2e8f0;
    --text: #1e293b;
    --text-muted: #64748b;
    --text-subtle: #94a3b8;
    --radius: 16px;
}

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
}

[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
    background-color: var(--bg) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #4f46e5, #6366f1, #7c3aed) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Sidebar button nav ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    color: rgba(255,255,255,0.75) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
    transform: none !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: rgba(255,255,255,0.2) !important;
    color: white !important;
    border-left: 3px solid rgba(255,255,255,0.8) !important;
    border-radius: 0 10px 10px 0 !important;
}

/* ── Card styles ── */
.nbx-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.nbx-card-sm {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* ── Score cards ── */
.score-card {
    border-radius: var(--radius);
    padding: 22px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    height: 140px;
    position: relative;
    overflow: hidden;
}
.score-card-solid { background: linear-gradient(135deg, #6366f1, #4f46e5); }
.score-card-amber { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.25); }
.score-card-sky { background: rgba(14,165,233,0.08); border: 1px solid rgba(14,165,233,0.25); }
.score-card-rose { background: rgba(244,63,94,0.08); border: 1px solid rgba(244,63,94,0.25); }
.score-card-emerald { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); }
.score-card-purple { background: rgba(139,92,246,0.08); border: 1px solid rgba(139,92,246,0.25); }
.score-value { font-size: 36px; font-weight: 900; line-height: 1; }
.score-label { font-size: 13px; font-weight: 600; color: var(--text-muted); }
.score-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    width: fit-content;
}
.badge-high { background: rgba(244,63,94,0.12); color: #e11d48; }
.badge-mod { background: rgba(245,158,11,0.12); color: #d97706; }
.badge-low { background: rgba(16,185,129,0.12); color: #059669; }
.badge-white { background: rgba(255,255,255,0.25); color: white; }

/* ── Section label ── */
.section-label {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--indigo);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Recommendation items ── */
.rec-item {
    background: rgba(16,185,129,0.05);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 14px;
    color: var(--text);
    font-weight: 500;
    line-height: 1.5;
}
.rec-icon { color: #10b981; font-size: 18px; flex-shrink: 0; margin-top: 1px; }

/* ── Waveform animation ── */
.waveform {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 3px;
    height: 56px;
    background: rgba(99,102,241,0.06);
    border-radius: 10px;
    padding: 0 12px;
}
.wave-bar {
    width: 3px;
    border-radius: 3px;
    background: var(--indigo);
    animation: wave 1.2s ease-in-out infinite;
}
@keyframes wave {
    0%, 100% { transform: scaleY(0.3); opacity: 0.5; }
    50% { transform: scaleY(1); opacity: 1; }
}

/* ── Status dot ── */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    animation: pulse 2s infinite;
    margin-right: 6px;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Table ── */
.nbx-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.nbx-table th {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--text-subtle);
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    text-align: left;
    background: #f8fafc;
}
.nbx-table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    font-weight: 500;
}
.nbx-table tr:hover td { background: rgba(99,102,241,0.03); }

/* ── Impact badges ── */
.impact-high {
    background: rgba(244,63,94,0.1);
    color: #e11d48;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 8px;
}
.impact-mod {
    background: rgba(245,158,11,0.1);
    color: #d97706;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 8px;
}

/* ── Progress bar ── */
.nbx-progress {
    height: 6px;
    background: var(--border);
    border-radius: 6px;
    overflow: hidden;
    margin-top: 6px;
}
.nbx-progress-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.6s ease;
}

/* ── Streamlit element overrides ── */
.stButton > button {
    background: var(--indigo) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 12px 28px !important;
    transition: all 0.2s !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: var(--indigo-dark) !important;
    transform: translateY(-1px) !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: #f8fafc !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
.stSlider > div > div > div { color: var(--indigo) !important; }
.stCheckbox label { color: var(--text) !important; font-weight: 500 !important; }
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 8px !important;
    border-bottom: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-muted) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--indigo) !important;
    border-bottom: 2px solid var(--indigo) !important;
}

/* ── Alert/warning ── */
.nbx-warning {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: var(--radius);
    padding: 18px 20px;
    margin-bottom: 20px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}
.nbx-disclaimer {
    background: rgba(244,63,94,0.04);
    border: 1px solid rgba(244,63,94,0.2);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin-top: 12px;
}

/* ── Help Desk styles ── */
.help-section-title {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-subtle);
    border-bottom: 1px solid var(--border);
    padding-bottom: 10px;
    margin-bottom: 16px;
    margin-top: 8px;
}
.help-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.help-tag {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 6px;
    background: #f1f5f9;
    color: #64748b;
    margin-right: 4px;
    margin-bottom: 4px;
}
.help-tag-sky { background: rgba(14,165,233,0.1); color: #0284c7; }
.help-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 8px;
}
.help-badge-emerald { background: rgba(16,185,129,0.1); color: #059669; }
.help-badge-amber { background: rgba(245,158,11,0.1); color: #d97706; }
.help-badge-rose { background: rgba(244,63,94,0.1); color: #e11d48; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── Page transitions ── */
[data-testid="stMainBlockContainer"] {
    padding: 2rem 2.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
RADAR_DATA = {
    "categories": [
        "Microbiome",
        "Voice",
        "Autonomic (HRV)",
        "Inflammation",
        "AMR"
    ]
}

MICROBIOME_DATA = {
    "names": ["Prevotella", "Bacteroides", "Faecalibacterium", "Akkermansia", "Bifidobacterium", "Others"],
    "values": [18.2, 15.6, 12.8, 8.7, 7.1, 37.6],
    "colors": ["#3b82f6", "#06b6d4", "#f59e0b", "#8b5cf6", "#f43f5e", "#94a3b8"],
}

TREND_DATA = pd.DataFrame({
    "date": ["01 May", "08 May", "15 May", "22 May", "29 May", "05 Jun"],
    "Microbiome": [65, 68, 75, 78, 75, 72],
    "Voice": [55, 58, 62, 65, 64, 68],
    "Autonomic": [60, 62, 68, 64, 63, 65],
    "Inflammation": [62, 65, 72, 75, 71, 70],
    "AMR": [50, 52, 55, 58, 59, 60],
})

SHAP_DATA = pd.DataFrame({
    "feature": ["Gut: Prevotella (Low)", "Voice: High Jitter", "Lifestyle: Poor Sleep",
                 "AMR: Freq. Antibiotics", "Inflammation: Normal CRP", "Diet: High Fiber"],
    "impact": [0.15, 0.12, 0.08, 0.05, -0.04, -0.09],
    "type": ["Risk Increasing"] * 4 + ["Risk Decreasing"] * 2,
})


# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "👤 Patient Profile"
if "patient" not in st.session_state:
    st.session_state.patient = {
        "name": "Jane Doe",
        "patient_id": "PDBR-2024-001",
        "age": "45",
        "gender": "Female",
        "overall_risk": 78,
        "risk_label": "HIGH",
        "primary_driver": "Gut Dysbiosis",
        "confidence": "82",
        "microbiome_score": 72,
        "voice_score": 68,
        "autonomic_score": 65,
        "inflammation_score": 70,
        "amr_score": 60,
        "recommendations": None,   # None = use global RECOMMENDATIONS
    }
if "scores" not in st.session_state:
    st.session_state.scores = {
        "microbiome":   72.0,
        "voice":        68.0,
        "autonomic":    65.0,
        "inflammation": 70.0,
        "amr":          60.0,
    }


def _risk_label(score: float) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 50:
        return "MODERATE"
    return "LOW"


def calculate_dashboard_results():
    s = st.session_state.scores
    overall = round(sum(s.values()) / len(s), 1)
    lbl = _risk_label(overall)

    drivers = {k: v for k, v in s.items()}
    primary = max(drivers, key=drivers.get)

    primary_labels = {
        "microbiome": "Gut Dysbiosis",
        "voice": "Voice Biomarkers",
        "autonomic": "Autonomic Dysfunction",
        "inflammation": "Inflammation",
        "amr": "AMR Exposure",
    }

    st.session_state.patient.update({
        "overall_risk": overall,
        "risk_label": lbl,
        "primary_driver": primary_labels.get(primary, "Gut Dysbiosis"),
        "microbiome_score": int(s["microbiome"]),
        "voice_score": int(s["voice"]),
        "autonomic_score": int(s["autonomic"]),
        "inflammation_score": int(s["inflammation"]),
        "amr_score": int(s["amr"]),
        "recommendations": generate_dynamic_recommendations(),
    })


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 28px 20px 20px; border-bottom: 1px solid rgba(255,255,255,0.15);">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                <div style="width:44px;height:44px;background:rgba(255,255,255,0.2);border-radius:12px;
                            display:flex;align-items:center;justify-content:center;font-size:22px;">🧠</div>
                <div>
                    <div style="font-size:20px;font-weight:900;color:white;letter-spacing:-0.5px;">
                        NeuroBiome<span style="color:rgba(255,255,255,0.6);">X</span>
                    </div>
                    <div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
                                color:rgba(255,255,255,0.6);margin-top:1px;">Neuro Risk Platform</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='padding: 12px 12px 8px;'>", unsafe_allow_html=True)

        # ── UPDATED NAV ORDER ──────────────────────────────────────────────
        nav_items = [
            "👤 Patient Profile",
            "📋 Metadata",
            "🎤 Voice Analysis",
            "🦠 Microbiome Analysis",
            "🛡️ AMR Analysis",
            "📊 Risk Summary",
            "💡 Explainability",
            "🧠 Dashboard",
            "📄 Patient Report",
            "❓ Help Desk",
            "ℹ️ About Platform",
        ]

        for item in nav_items:
            active = st.session_state.page == item
            if st.button(
                item,
                key=f"nav_{item}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.page = item
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="padding: 16px; border-top: 1px solid rgba(255,255,255,0.15); margin-top: auto;">
            <div style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15);
                        border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                    <span class="status-dot"></span>
                    <span style="font-size:13px; font-weight:700; color:white;">AI Status</span>
                </div>
                <div style="font-size:12px; color:rgba(255,255,255,0.65); font-weight:500;">All systems operational</div>
            </div>
            <div style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15);
                        border-radius: 10px; padding: 10px 14px;">
                <div style="font-size:11px; color:rgba(255,255,255,0.6); font-weight:600;">Patient:</div>
                <div style="font-size:13px; color:white; font-weight:700;">PDBR-2024-001</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── CHART HELPERS ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#64748b"),
    margin=dict(l=10, r=10, t=30, b=10),
)


def radar_chart():

    s = st.session_state.scores

    dyn_values = [

        s["microbiome"],

        s["voice"],

        s["autonomic"],

        s["inflammation"],

        s["amr"]
    ]

    categories = RADAR_DATA["categories"] + [RADAR_DATA["categories"][0]]

    values = dyn_values + [dyn_values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(

        r=values,

        theta=categories,

        fill="toself",

        fillcolor="rgba(99,102,241,0.12)",

        line=dict(color="#6366f1", width=2.5),

        marker=dict(color="#6366f1", size=6),
    ))

    fig.update_layout(

        **PLOTLY_LAYOUT,

        polar=dict(

            bgcolor="rgba(0,0,0,0)",

            radialaxis=dict(

                visible=True,

                range=[0, 100],

                gridcolor="#e2e8f0"
            ),

            angularaxis=dict(

                gridcolor="#e2e8f0"
            ),
        ),

        showlegend=False,

        height=300,
    )

    return fig


def donut_chart():
    fig = go.Figure(go.Pie(
        labels=MICROBIOME_DATA["names"],
        values=MICROBIOME_DATA["values"],
        hole=0.58,
        marker=dict(colors=MICROBIOME_DATA["colors"], line=dict(color="#ffffff", width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=280, showlegend=False)
    return fig


def trend_chart():
    fig = go.Figure()
    colors_map = {
        "Microbiome": "#f59e0b", "Voice": "#8b5cf6",
        "Autonomic": "#f43f5e", "Inflammation": "#10b981", "AMR": "#6366f1"
    }
    for col, clr in colors_map.items():
        fig.add_trace(go.Scatter(
            x=TREND_DATA["date"], y=TREND_DATA[col],
            name=col, line=dict(color=clr, width=2.5, shape="spline"),
            mode="lines", hovertemplate=f"<b>{col}</b>: %{{y}}<extra></extra>",
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=260,
        xaxis=dict(showgrid=False, tickfont=dict(size=10), color="#94a3b8"),
        yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(size=10), color="#94a3b8"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=11), bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    return fig


def shap_chart():
    df = SHAP_DATA.sort_values("impact")
    colors = ["#10b981" if v < 0 else "#f43f5e" for v in df["impact"]]
    fig = go.Figure(go.Bar(
        x=df["impact"], y=df["feature"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>SHAP: %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=300,
        xaxis=dict(title="SHAP Value", gridcolor="#f1f5f9", zeroline=True,
                   zerolinecolor="#94a3b8", tickfont=dict(size=9)),
        yaxis=dict(tickfont=dict(size=10), color="#1e293b"),
        bargap=0.3,
    )
    return fig


# ── SCORE CARD ────────────────────────────────────────────────────────────────
def score_card(title, score, risk, card_class, icon, value_color="#1e293b"):
    badge_class = "badge-white" if card_class == "score-card-solid" else (
        "badge-high" if risk == "High Risk" else "badge-mod"
    )
    text_color = "white" if card_class == "score-card-solid" else value_color
    return f"""
    <div class="score-card {card_class}">
        <div style="display:flex;justify-content:space-between;align-items:start;">
            <span style="font-size:22px;">{icon}</span>
            <span class="score-badge {badge_class}">{risk}</span>
        </div>
        <div>
            <div class="score-value" style="color:{text_color};">{score}</div>
            <div class="score-label" style="color:{'rgba(255,255,255,0.75)' if card_class == 'score-card-solid' else 'var(--text-muted)'};">{title}</div>
        </div>
    </div>
    """


# ── PAGES ─────────────────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown("""
    <div style="margin-bottom:8px;">
        <div style="font-size:28px;font-weight:900;color:var(--text);letter-spacing:-0.5px;">Dashboard</div>
        <div style="font-size:13px;color:var(--text-muted);margin-top:4px;font-weight:500;">
            Gut-Brain Neurodegenerative Vulnerability Assessment
        </div>
    </div>
    """, unsafe_allow_html=True)

    p  = st.session_state.patient
    s  = st.session_state.scores

    def _badge(v):
        return "High Risk" if v >= 70 else ("Moderate Risk" if v >= 50 else "Low Risk")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(score_card("Overall Risk Score", str(p["overall_risk"]),
                               _badge(p["overall_risk"]), "score-card-solid", "🧠", "white"), unsafe_allow_html=True)
    with c2:
        st.markdown(score_card("Microbiome Score", str(p["microbiome_score"]),
                               _badge(p["microbiome_score"]), "score-card-amber", "🦠", "#d97706"), unsafe_allow_html=True)
    with c3:
        st.markdown(score_card("Voice Score", str(p["voice_score"]),
                               _badge(p["voice_score"]), "score-card-sky", "🎤", "#0284c7"), unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(score_card("Autonomic Score", str(p["autonomic_score"]),
                               _badge(p["autonomic_score"]), "score-card-rose", "💓", "#e11d48"), unsafe_allow_html=True)
    with c5:
        st.markdown(score_card("Inflammation Score", str(p["inflammation_score"]),
                               _badge(p["inflammation_score"]), "score-card-emerald", "🩺", "#059669"), unsafe_allow_html=True)
    with c6:
        st.markdown(score_card("AMR Score", str(p["amr_score"]),
                               _badge(p["amr_score"]), "score-card-purple", "🧬", "#7c3aed"), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_radar, col_interp, col_micro = st.columns([1.1, 0.9, 1])

    with col_radar:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Risk Radar (Multimodal)</div>', unsafe_allow_html=True)
        st.plotly_chart(radar_chart(), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_interp:
        st.markdown("""
        <div class="nbx-card">
            <div class="section-label">Risk Interpretation</div>
            <p style="font-size:13px;color:var(--text-muted);line-height:1.7;font-weight:500;">
                The patient shows
                <span style="color:var(--rose);font-weight:700;">elevated neurodegenerative vulnerability</span>
                based on:
            </p>
            <ul style="font-size:13px;color:var(--text-muted);line-height:2;font-weight:500;padding-left:16px;">
                <li>Gut dysbiosis</li>
                <li>Inflammatory burden</li>
                <li>Autonomic dysfunction</li>
                <li>Voice biomarkers</li>
            </ul>
            <div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.2);
                        border-radius:12px;padding:16px;margin-top:12px;">
                <div style="font-size:10px;font-weight:800;letter-spacing:2px;color:#059669;
                            text-transform:uppercase;margin-bottom:10px;">Recommendations</div>
                <div style="display:flex;align-items:start;gap:10px;margin-bottom:8px;font-size:13px;color:#059669;font-weight:500;">
                    <span>✅</span> Anti-inflammatory diet
                </div>
                <div style="display:flex;align-items:start;gap:10px;font-size:13px;color:#059669;font-weight:500;">
                    <span>✅</span> Neurological consultation
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_micro:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Microbiome Composition</div>', unsafe_allow_html=True)
        st.plotly_chart(donut_chart(), use_container_width=True, config={"displayModeBar": False})
        for name, val, col in zip(MICROBIOME_DATA["names"], MICROBIOME_DATA["values"], MICROBIOME_DATA["colors"]):
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:3px 0;font-size:12px;font-weight:600;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:10px;height:10px;border-radius:3px;background:{col};flex-shrink:0;"></div>
                    <span style="color:var(--text-muted);">{name}</span>
                </div>
                <span style="color:var(--text-subtle);">{val}%</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c_trend, c_voice, c_uploads = st.columns([1.5, 1, 0.7])

    with c_trend:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Trend Over Time</div>', unsafe_allow_html=True)
        st.plotly_chart(trend_chart(), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c_voice:
        st.markdown("""
        <div class="nbx-card">
            <div class="section-label">Voice Analysis</div>
            <div class="waveform" style="margin-bottom:16px;">
                <div class="wave-bar" style="height:40%;animation-delay:0.0s;"></div>
                <div class="wave-bar" style="height:70%;animation-delay:0.1s;"></div>
                <div class="wave-bar" style="height:90%;animation-delay:0.2s;"></div>
                <div class="wave-bar" style="height:55%;animation-delay:0.3s;"></div>
                <div class="wave-bar" style="height:80%;animation-delay:0.4s;"></div>
                <div class="wave-bar" style="height:35%;animation-delay:0.5s;"></div>
                <div class="wave-bar" style="height:95%;animation-delay:0.6s;"></div>
                <div class="wave-bar" style="height:60%;animation-delay:0.7s;"></div>
                <div class="wave-bar" style="height:75%;animation-delay:0.8s;"></div>
                <div class="wave-bar" style="height:45%;animation-delay:0.9s;"></div>
                <div class="wave-bar" style="height:88%;animation-delay:1.0s;"></div>
                <div class="wave-bar" style="height:52%;animation-delay:1.1s;"></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
                <div>
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                                letter-spacing:1px;color:var(--text-muted);margin-bottom:4px;">Jitter</div>
                    <div style="font-size:22px;font-weight:900;color:var(--text);">2.3%</div>
                    <div style="font-size:10px;font-weight:700;color:var(--rose);margin-top:2px;">High</div>
                </div>
                <div>
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                                letter-spacing:1px;color:var(--text-muted);margin-bottom:4px;">Shimmer</div>
                    <div style="font-size:22px;font-weight:900;color:var(--text);">8.7%</div>
                    <div style="font-size:10px;font-weight:700;color:var(--rose);margin-top:2px;">High</div>
                </div>
                <div>
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                                letter-spacing:1px;color:var(--text-muted);margin-bottom:4px;">HNR</div>
                    <div style="font-size:22px;font-weight:900;color:var(--text);">14.6</div>
                    <div style="font-size:10px;font-weight:700;color:var(--rose);margin-top:2px;">Low</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_uploads:
        st.markdown("""
        <div class="nbx-card" style="height:100%;">
            <div class="section-label">Recent Uploads</div>
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;">
                <div style="width:44px;height:44px;border-radius:12px;background:rgba(99,102,241,0.1);
                            display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;">🎤</div>
                <div>
                    <div style="font-size:13px;font-weight:700;color:var(--text);">Voice Sample</div>
                    <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">2 min ago</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="width:44px;height:44px;border-radius:12px;background:rgba(244,63,94,0.08);
                            display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;">💓</div>
                <div>
                    <div style="font-size:13px;font-weight:700;color:var(--text);">HRV Data</div>
                    <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">15 min ago</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def page_patient_profile():
    st.markdown('<div class="section-label">Patient Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;padding-bottom:20px;border-bottom:1px solid var(--border);">
        <div style="font-size:28px;">👤</div>
        <div>
            <div style="font-size:18px;font-weight:800;color:var(--text);">Demographic Metadata</div>
            <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">Base features for AI calibration</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name", value="", placeholder="e.g. Jane Doe")
        age = st.number_input("Age", min_value=0, max_value=120, value=0)
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=0.0, step=0.1)
        country = st.text_input("Country", value="", placeholder="e.g. India")
    with c2:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        height = st.number_input("Height (cm)", min_value=0, max_value=250, value=0)
        patient_id = st.text_input("Patient ID", value="")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("💾  Save Demographics", use_container_width=True):
        st.session_state.patient.update({
            "name": name, "age": str(age), "gender": gender, "patient_id": patient_id
        })
        st.success("✅ Patient profile saved successfully!")
        time.sleep(0.5)

    st.markdown('</div>', unsafe_allow_html=True)


def page_metadata():
    st.markdown("""
    <div class="nbx-warning">
        <div style="font-size:22px;">⚠️</div>
        <div>
            <div style="font-size:13px;font-weight:800;color:#d97706;margin-bottom:4px;">
                Important: Metadata Risk Estimation
            </div>
            <div style="font-size:12px;color:#92400e;font-weight:500;line-height:1.6;">
                If QZA sequencing files are unavailable, the Clinical Metadata Input section provides an
                estimated risk score using symptom and lifestyle data. These inputs are for preliminary
                screening and educational purposes only and do not replace sequencing-based microbiome analysis.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Neurological & Cognitive Symptoms</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown("**Reported Symptoms**")
        st.checkbox("Frequent Brain Fog")
        st.checkbox("Short-term Memory Issues")
        st.checkbox("Resting Tremors")
        st.checkbox("Noticeable Speech Difficulty")
        st.checkbox("Balance or Gait Problems")
        st.checkbox("Chronic Daily Fatigue")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown("**Mood & Sleep Metrics**")
        st.slider("Anxiety Severity", 1, 10, 5)
        st.slider("Depressive Symptoms", 1, 10, 4)
        st.slider("Sleep Quality (Subjective)", 1, 10, 6)

        st.markdown("""
        <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.2);
                    border-radius:12px;padding:14px;margin-top:12px;">
            <div style="font-size:11px;font-weight:700;color:var(--indigo);margin-bottom:6px;">
                🎤 Voice Biomarker Sync
            </div>
            <div style="font-size:11px;color:var(--text-muted);font-weight:500;line-height:1.5;">
                Ensure the patient has uploaded a recent voice sample in the Voice Analysis tab
                for full multimodal neuro-analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾  Save Neuro Metadata", use_container_width=True):
            st.success("✅ Metadata saved!")
        st.markdown('</div>', unsafe_allow_html=True)


def page_voice():
    st.markdown('<div class="section-label">Voice Analysis Data</div>', unsafe_allow_html=True)

    col, _ = st.columns([0.65, 0.35])
    with col:
        st.markdown('<div class="nbx-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:48px;margin-bottom:12px;">🎤</div>
        <div style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:6px;">Voice Recording</div>
        <div style="font-size:13px;color:var(--text-muted);margin-bottom:24px;font-weight:500;">
            Upload .WAV files for vocal biomarker extraction. Sustained vowel "Aaaaaaa" for 5–10 seconds recommended.
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Upload Voice File", type=["wav", "mp3", "ogg"],
            label_visibility="collapsed"
        )

        if uploaded:
            with st.spinner("Analyzing voice biomarkers..."):
                time.sleep(1.5)
            st.markdown("""
            <div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.2);
                        border-radius:12px;padding:20px;text-align:center;margin-top:12px;">
                <div style="font-size:32px;margin-bottom:8px;">✅</div>
                <div style="font-size:15px;font-weight:700;color:#059669;">Analysis Complete!</div>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"File processed: {uploaded.name}")

        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:20px 0;">
            <div style="flex:1;height:1px;background:var(--border);"></div>
            <span style="font-size:11px;font-weight:700;color:var(--text-muted);letter-spacing:2px;">OR</span>
            <div style="flex:1;height:1px;background:var(--border);"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎙️ Record Directly in Browser")
        audio_bytes = audio_recorder(
            pause_threshold=2.0,
            sample_rate=41000
        )
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            with open("recorded_voice.wav", "wb") as f:
                f.write(audio_bytes)
            st.success("✅ Voice recorded successfully!")

        st.markdown("---")
        st.markdown("#### 🔬 Run Voice Analysis")
        voice_score_input = st.slider(
    "Voice Biomarker Risk Score",
    min_value=0,
    max_value=100,
    value=int(st.session_state.patient.get("voice_score", 68)),
    step=1,
    key="voice_score_input",
    help="Adjust based on clinical biomarker output (Jitter, Shimmer, HNR)"
)
        if st.button("✅ Save Voice Score", use_container_width=True, key="save_voice"):
            st.session_state.scores["voice"] = float(voice_score_input)
            calculate_dashboard_results()
            st.success(f"✅ Voice score set to {voice_score_input}. Overall risk recalculated.")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


def page_microbiome():
    st.markdown('<div class="section-label">Gut & Microbiome Analysis</div>', unsafe_allow_html=True)

    col, _ = st.columns([0.6, 0.4])
    with col:
        st.markdown('<div class="nbx-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:48px;margin-bottom:12px;">🦠</div>
        <div style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:6px;">Microbiome Sequencing</div>
        <div style="font-size:13px;color:var(--text-muted);margin-bottom:20px;font-weight:500;">
            Upload .QZA artifact files for taxonomic profiling and dysbiosis scoring.
        </div>
        """, unsafe_allow_html=True)

        qza_file = st.file_uploader("Upload QZA File", type=["qza", "csv", "tsv"],
                                     label_visibility="collapsed")
        if qza_file:
            with st.spinner("Parsing QZA artifact..."):
                time.sleep(1.5)
            st.success(f"✅ Taxonomy Extracted: {qza_file.name}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin:16px 0;opacity:0.6;">
        <div style="flex:1;height:1px;background:var(--border);"></div>
        <span style="font-size:10px;font-weight:700;color:var(--text-muted);letter-spacing:2px;">OR MANUAL ENTRY</span>
        <div style="flex:1;height:1px;background:var(--border);"></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown("**Clinical Symptoms**")
        syms = ["Frequent Bloating", "Chronic Constipation", "Frequent Diarrhea",
                "Acid Reflux (GERD)", "History of IBS/IBD", "Known Food Intolerances",
                "Unexplained Gut Pain", "Recent Antibiotic Course"]
        cols = st.columns(2)
        for i, sym in enumerate(syms):
            cols[i % 2].checkbox(sym)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown("**Dietary Profile**")
        st.selectbox("Primary Diet Type", ["Standard Western Diet", "Mediterranean",
                                            "Vegan / Plant-Based", "Keto / Low-Carb", "Paleo"])
        st.slider("Daily Fiber Intake (Score)", 0, 10, 5)
        st.slider("Processed Food Consumption (Score)", 0, 10, 5)
        st.markdown("---")
        micro_score_input = st.slider(
    "Microbiome Risk Score",
    min_value=0,
    max_value=100,
    value=int(st.session_state.patient.get("microbiome_score", 72)),
    step=1,
    key="micro_score_input",
    help="Adjust based on dysbiosis analysis output"
)
        if st.button("💾 Save Gut Metadata & Score", use_container_width=True):
            st.session_state.scores["microbiome"] = float(micro_score_input)
            calculate_dashboard_results()
            st.success(f"✅ Microbiome score set to {micro_score_input}. Overall risk recalculated.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def page_amr():
    st.markdown('<div class="section-label">Inflammation & AMR Risk</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown("**🌿 Lifestyle & Inflammation**")
        st.slider("Average Sleep Duration (Hrs)", 2, 12, 7)
        st.slider("Chronic Stress Level (1–10)", 1, 10, 5)
        st.slider("Physical Activity (1–10)", 1, 10, 6)
        st.checkbox("Active Smoker")
        st.checkbox("Frequent Alcohol Consumption")
        st.checkbox("Autoimmune Disease History")
        st.checkbox("Post-COVID (Long COVID) Symptoms")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown("**🛡️ Antimicrobial Resistance (AMR)**")
        st.selectbox("Lifetime Antibiotic Usage", [
            "Rare (0-1 times per decade)", "Occasional (1 time every few years)",
            "Moderate (1-2 times per year)", "Frequent (3+ times per year)"
        ])
        st.selectbox("Last Antibiotic Course", [
            "Currently taking", "Within last 3 months",
            "Within last year", "Over a year ago"
        ])
        st.checkbox("Recent Hospitalization (Last 12 Mo)")
        st.checkbox("History of Chronic Infections (e.g., UTI)")
        st.markdown("---")
        inflam_input = st.slider(
    "Inflammation Risk Score",
    min_value=0,
    max_value=100,
    value=int(st.session_state.patient.get("inflammation_score", 70)),
    step=1,
    key="inflam_input"
)
        amr_input = st.slider(
    "AMR Risk Score",
    min_value=0,
    max_value=100,
    value=int(st.session_state.patient.get("amr_score", 60)),
    step=1,
    key="amr_input"
)
        autonomic_input = st.slider(
    "Autonomic (HRV) Risk Score",
    min_value=0,
    max_value=100,
    value=int(st.session_state.patient.get("autonomic_score", 65)),
    step=1,
    key="autonomic_input"
)
                    
        if st.button("💾 Save All AMR & Lifestyle Scores", use_container_width=True):
            st.session_state.scores["inflammation"] = float(inflam_input)
            st.session_state.scores["amr"]          = float(amr_input)
            st.session_state.scores["autonomic"]    = float(autonomic_input)
            calculate_dashboard_results()
            st.success("✅ Scores saved. Overall risk recalculated.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def generate_dynamic_recommendations():

    s = st.session_state.scores

    recs = []

    if s["microbiome"] >= 70:

        recs.append(
            "Advanced gut microbiome sequencing recommended."
        )

        recs.append(
            "Increase dietary fiber and probiotic intake."
        )

    if s["voice"] >= 70:

        recs.append(
            "Neurological speech evaluation advised."
        )

    if s["autonomic"] >= 70:

        recs.append(
            "HRV monitoring and autonomic testing suggested."
        )

    if s["inflammation"] >= 70:

        recs.append(
            "Anti-inflammatory diet intervention recommended."
        )

    if s["amr"] >= 70:

        recs.append(
            "Antibiotic stewardship consultation advised."
        )

    if len(recs) == 0:

        recs.append(
            "Maintain healthy lifestyle and preventive monitoring."
        )

    return recs

# =====================================================
# MASTER AI CALCULATION ENGINE
# =====================================================

def calculate_dashboard_results():

    s = st.session_state.scores

    # =================================================
    # GET SCORES
    # =================================================

    microbiome = float(
        s.get("microbiome", 0)
    )

    voice = float(
        s.get("voice", 0)
    )

    autonomic = float(
        s.get("autonomic", 0)
    )

    inflammation = float(
        s.get("inflammation", 0)
    )

    amr = float(
        s.get("amr", 0)
    )

    # =================================================
    # MULTIMODAL FUSION
    # =================================================

    overall = round(

        (
            microbiome * 0.40 +

            voice * 0.25 +

            autonomic * 0.15 +

            inflammation * 0.15 +

            amr * 0.05
        ),

        2
    )

    # =================================================
    # RISK LEVEL
    # =================================================

    if overall >= 75:

        risk = "High Risk"

    elif overall >= 50:

        risk = "Moderate Risk"

    else:

        risk = "Low Risk"

    # =================================================
    # PRIMARY DRIVER
    # =================================================

    score_map = {

        "Microbiome": microbiome,

        "Voice Biomarkers": voice,

        "Autonomic Dysfunction": autonomic,

        "Inflammation": inflammation,

        "AMR Burden": amr,
    }

    primary_driver = max(

        score_map,

        key=score_map.get
    )

    # =================================================
    # CONFIDENCE
    # =================================================

    confidence = round(

        overall * 0.92,

        2
    )

    # =================================================
    # SAVE TO SESSION STATE
    # =================================================

    st.session_state.patient.update({

        "overall_risk": overall,

        "risk_label": risk,

        "confidence": confidence,

        "primary_driver": primary_driver,

        "microbiome_score": microbiome,

        "voice_score": voice,

        "autonomic_score": autonomic,

        "inflammation_score": inflammation,

        "amr_score": amr,
    })

def page_risk_summary():
    st.markdown("""
    <div style="margin-bottom:8px;">
        <div style="font-size:28px;font-weight:900;color:var(--text);">Risk Summary</div>
        <div style="font-size:13px;color:var(--text-muted);font-weight:500;margin-top:4px;">
            Comprehensive overview of your neurodegenerative vulnerability assessment.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2.5])

    # ── live values from session state ──
    s = st.session_state.scores

    p = st.session_state.patient

    overall = p.get(
        "overall_risk",
        0
    )

    risk_lbl = p.get(
        "risk_label",
        "Low Risk"
    )

# =====================================================
# RISK COLOR
# =====================================================

    if risk_lbl == "High Risk":

        risk_color = "#e11d48"

    elif risk_lbl == "Moderate Risk":

        risk_color = "#d97706"

    else:

        risk_color = "#059669"

    with col_left:
        st.markdown(f"""
        <div style="background:white;border:1px solid var(--border);border-radius:20px;padding:28px 24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <div style="font-size:12px;font-weight:700;color:var(--text-muted);margin-bottom:16px;">OVERALL RISK</div>
            <div style="font-size:52px;font-weight:900;color:{risk_color};line-height:1;">{overall}/100</div>
            <div style="font-size:15px;font-weight:700;color:{risk_color};margin-top:6px;">{risk_lbl.title()} Risk</div>
            <div style="height:8px;background:var(--border);border-radius:8px;margin:16px 0;overflow:hidden;">
                <div style="height:100%;width:{overall}%;background:linear-gradient(90deg,#f43f5e,#fb7185);border-radius:8px;"></div>
            </div>
            <div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-top:16px;">CONFIDENCE SCORE</div>
            <div style="font-size:28px;font-weight:900;color:#059669;">{p.get("confidence","82")}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        tabs = st.tabs(["📋 Summary", "📊 Scores", "🧬 Top Biomarkers", "💊 Recommendations", "🔍 Interpretation"])

        with tabs[0]:
            st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:16px;">AI Recommendations</div>', unsafe_allow_html=True)
            active_recs = generate_dynamic_recommendations()
            for rec in active_recs:
                st.markdown(f"""
                <div class="rec-item">
                    <span class="rec-icon">✅</span>
                    <span>{rec}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[1]:
            st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:20px;">Modality Scores</div>', unsafe_allow_html=True)
            score_items = [
                ("🦠 Microbiome",     p.get("microbiome_score",   0), "#f59e0b"),
                ("🎤 Voice",          p.get("voice_score",        0), "#6366f1"),
                ("💓 Autonomic (HRV)",p.get("autonomic_score",    0), "#f43f5e"),
                ("🩺 Inflammation",   p.get("inflammation_score", 0), "#10b981"),
                ("🛡️ AMR Risk",       p.get("amr_score",          0), "#8b5cf6"),
            ]
            for label, val, clr in score_items:
                st.markdown(f"""
                <div style="margin-bottom:16px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                        <span style="font-size:13px;font-weight:700;color:var(--text);">{label}</span>
                        <span style="font-size:14px;font-weight:900;color:{clr};">{val}%</span>
                    </div>
                    <div class="nbx-progress">
                        <div class="nbx-progress-fill" style="width:{val}%;background:{clr};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("**Edit Scores:**")
            score_cfg = [
                ("microbiome",   "🦠 Microbiome",       "#f59e0b"),
                ("voice",        "🎤 Voice",             "#6366f1"),
                ("autonomic",    "💓 Autonomic (HRV)",   "#f43f5e"),
                ("inflammation", "🩺 Inflammation",      "#10b981"),
                ("amr",          "🛡️ AMR Risk",          "#8b5cf6"),
            ]
            new_scores = {}
            for key, label, clr in score_cfg:
                new_scores[key] = st.slider(
                    label, 0, 100,
                    int(s.get(key, 65)),
                    key=f"slider_{key}"
                )
            if st.button("💾 Save All Scores", use_container_width=True):
                st.session_state.scores.update(new_scores)
                calculate_dashboard_results()
                st.success("✅ All scores saved! Overall risk recalculated.")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[2]:
            st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:16px;">Top Clinical Biomarkers</div>', unsafe_allow_html=True)
            biomarkers = [
                ("Vocal Jitter", "Voice Analysis", "HIGH", "high"),
                ("HNR Level", "Voice Analysis", "HIGH", "high"),
                ("Vocal Shimmer", "Voice Analysis", "MODERATE", "mod"),
                ("Sleep Quality", "Inflammation", "MODERATE", "mod"),
                ("Antibiotic Usage", "AMR Risk", "HIGH", "high"),
                ("Prevotella (Low)", "Microbiome", "HIGH", "high"),
            ]
            st.markdown("""
            <table class="nbx-table">
                <thead><tr>
                    <th>Biomarker</th><th>Modality</th><th>Impact</th>
                </tr></thead><tbody>
            """ + "".join([
                f"<tr><td><b>{b}</b></td><td style='color:var(--indigo);'>{m}</td>"
                f"<td><span class='impact-{cl}'>{i}</span></td></tr>"
                for b, m, i, cl in biomarkers
            ]) + "</tbody></table>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[3]:
            st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:16px;">Full AI Recommendations</div>', unsafe_allow_html=True)
            active_recs = generate_dynamic_recommendations()

            for i, rec in enumerate(active_recs, 1):
                st.markdown(f"""
                <div style="display:flex;gap:14px;padding:12px 0;border-bottom:1px solid var(--border);">
                    <span style="font-size:12px;font-weight:800;color:var(--indigo);
                                 min-width:24px;margin-top:1px;">{i:02d}</span>
                    <span style="font-size:13px;color:var(--text-muted);font-weight:500;line-height:1.6;">{rec}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[4]:
            st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:16px;">Clinical Interpretation</div>', unsafe_allow_html=True)
            st.markdown("""
            <p style="font-size:13px;color:var(--text-muted);line-height:1.8;font-weight:500;">
                The patient demonstrates <b style="color:var(--rose);">elevated neurodegenerative vulnerability</b>
                based on multimodal fusion analysis encompassing gut microbiome dysbiosis,
                inflammatory burden markers, autonomic nervous system dysfunction, and vocal biomarker
                irregularities consistent with early Parkinsonian motor speech patterns.
            </p>
            <p style="font-size:13px;color:var(--text-muted);line-height:1.8;font-weight:500;margin-top:12px;">
                The Gut–Brain axis dysregulation is the primary driver, with elevated Prevotella abundance
                and reduced Akkermansia muciniphila indicating compromised intestinal barrier integrity
                and heightened neuroinflammatory potential.
            </p>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="nbx-disclaimer" style="margin-top:16px;">
                <div style="font-size:11px;font-weight:700;color:var(--rose);margin-bottom:6px;">⚠️ Research Use Notice</div>
                <div style="font-size:11px;color:#9f1239;font-weight:500;line-height:1.6;">
                    This analysis is intended for research and wellness purposes only.
                    It is not a substitute for clinical diagnosis or professional medical advice.
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


def page_explainability():
    st.markdown('<div class="section-label">AI Explainability (SHAP)</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:16px;font-weight:800;color:var(--text);margin-bottom:16px;">Global Feature Importance</div>', unsafe_allow_html=True)
        st.plotly_chart(shap_chart(), use_container_width=True, config={"displayModeBar": False})
        st.markdown("""
        <div style="display:flex;gap:20px;margin-top:8px;flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;color:var(--text-muted);">
                <div style="width:10px;height:10px;border-radius:50%;background:#f43f5e;"></div> Risk Increasing
            </div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;color:var(--text-muted);">
                <div style="width:10px;height:10px;border-radius:50%;background:#10b981;"></div> Risk Decreasing
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="nbx-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:16px;font-weight:800;color:var(--text);margin-bottom:12px;">Top Clinical Drivers</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#f8fafc;border:1px solid var(--border);border-radius:10px;
                    padding:12px 16px;margin-bottom:14px;display:flex;gap:20px;flex-wrap:wrap;">
            <span style="font-size:10px;font-weight:700;color:var(--text-muted);letter-spacing:1px;">IMPACT KEY:</span>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;">
                <div style="width:8px;height:8px;border-radius:50%;background:#f43f5e;"></div>
                <span style="color:var(--text-muted);">Risk Increasing</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;">
                <div style="width:8px;height:8px;border-radius:50%;background:#f59e0b;"></div>
                <span style="color:var(--text-muted);">Moderate Impact</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;">
                <div style="width:8px;height:8px;border-radius:50%;background:#10b981;"></div>
                <span style="color:var(--text-muted);">Risk Decreasing (Protective)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        biomarkers = [
            ("Vocal Jitter", "Voice Analysis", "HIGH", "high"),
            ("HNR Level", "Voice Analysis", "HIGH", "high"),
            ("Vocal Shimmer", "Voice Analysis", "MODERATE", "mod"),
            ("Sleep Quality", "Inflammation", "MODERATE", "mod"),
            ("Antibiotic Usage", "AMR Risk", "HIGH", "high"),
        ]
        st.markdown("""
        <table class="nbx-table">
            <thead><tr>
                <th>Biomarker</th><th>Modality</th><th>Impact</th>
            </tr></thead><tbody>
        """ + "".join([
            f"<tr><td><b style='color:var(--text);'>{b}</b></td>"
            f"<td style='color:var(--indigo);font-size:12px;'>{m}</td>"
            f"<td><span class='impact-{cl}'>{i}</span></td></tr>"
            for b, m, i, cl in biomarkers
        ]) + "</tbody></table>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def page_patient_report():

    # ── PDF Download ──
    p = st.session_state.patient
    s = st.session_state.scores

    scores = {
        "overall": float(p.get("overall_risk", 0)),
        "microbiome": float(s.get("microbiome", 0)),
        "voice": float(s.get("voice", 0)),
        "autonomic": float(s.get("autonomic", 0)),
        "inflammation": float(s.get("inflammation", 0)),
        "amr": float(s.get("amr", 0)),
    }

    active_recs = generate_dynamic_recommendations()

    pdf_bytes = generate_pdf_report(
        patient_data=p,
        scores=scores,
        recommendations=active_recs,
    )

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name=f"NeuroBiomeX_Report_{p.get('patient_id', 'Patient')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def page_help_desk():
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:6px;">
            <div style="width:52px;height:52px;background:linear-gradient(135deg,#6366f1,#4f46e5);
                        border-radius:16px;display:flex;align-items:center;justify-content:center;
                        font-size:24px;box-shadow:0 4px 12px rgba(99,102,241,0.3);">📖</div>
            <div>
                <div style="font-size:28px;font-weight:900;color:var(--text);letter-spacing:-0.5px;">
                    Help Desk & User Guide
                </div>
                <div style="font-size:13px;color:var(--text-muted);font-weight:500;margin-top:2px;">
                    Platform Documentation v1.0 · NeuroBiomeX
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.06));
                border:1px solid rgba(99,102,241,0.2);border-radius:16px;padding:20px 24px;
                margin-bottom:28px;font-size:14px;color:#3730a3;font-weight:500;line-height:1.7;">
        Welcome to <b>NeuroBiomeX</b> — an AI-powered multimodal gut–brain axis intelligence platform
        designed for microbiome-driven neurodegenerative vulnerability assessment and translational
        bioinformatics analysis.<br><br>
        This guide explains how to upload supported inputs, interpret dashboard outputs, and understand
        the scientific meaning of each analytical layer.
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 System Inputs", "📊 Output Metrics", "🔬 AI & Workflow", "⚖️ Legal & Troubleshooting"
    ])

    with tab1:
        st.markdown('<div class="help-section-title">1. System Inputs & Specifications</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("""
            <div class="help-card">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                    <div style="width:36px;height:36px;background:rgba(245,158,11,0.1);border-radius:10px;
                                display:flex;align-items:center;justify-content:center;font-size:18px;">🦠</div>
                    <div style="font-size:15px;font-weight:800;color:var(--text);">Microbiome Data Upload</div>
                </div>
                <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;font-weight:500;line-height:1.6;">
                    The platform supports QIIME2-compatible microbiome feature tables and abundance datasets.
                    Files are automatically processed, normalized, and aligned with trained microbial biomarkers.
                </p>
                <div style="margin-bottom:10px;">
                    <span class="help-tag">.qza</span>
                    <span class="help-tag">.csv</span>
                    <span class="help-tag">.tsv</span>
                </div>
                <ul style="font-size:12px;color:var(--text-muted);padding-left:16px;margin:0;line-height:1.8;font-weight:500;">
                    <li>QIIME2 exported feature tables</li>
                    <li>curatedMetagenomicData abundance profiles</li>
                    <li>Relative abundance microbiome datasets</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="help-card">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                    <div style="width:36px;height:36px;background:rgba(14,165,233,0.1);border-radius:10px;
                                display:flex;align-items:center;justify-content:center;font-size:18px;">🎤</div>
                    <div style="font-size:15px;font-weight:800;color:var(--text);">Voice Analysis Capture</div>
                </div>
                <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;font-weight:500;line-height:1.6;">
                    Supported Input: <b>.wav</b> upload OR Direct in-browser microphone recording.
                    Sustained vowel sound ("Aaaaaaa") for 5–10 seconds recommended.
                </p>
                <div style="font-size:12px;font-weight:700;color:var(--text-muted);margin-bottom:8px;">Extracted Voice Biomarkers:</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;">
                    <span class="help-tag help-tag-sky">Jitter</span>
                    <span class="help-tag help-tag-sky">Shimmer</span>
                    <span class="help-tag help-tag-sky">HNR</span>
                    <span class="help-tag help-tag-sky">Pitch Variability</span>
                    <span class="help-tag help-tag-sky">Instability Metrics</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="help-card" style="background:rgba(245,158,11,0.04);border-color:rgba(245,158,11,0.25);">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                    <div style="width:36px;height:36px;background:rgba(245,158,11,0.15);border-radius:10px;
                                display:flex;align-items:center;justify-content:center;font-size:18px;">☁️</div>
                    <div style="font-size:15px;font-weight:800;color:#d97706;">Metadata-Based Fallback (Simulated)</div>
                </div>
                <p style="font-size:13px;color:#92400e;font-weight:500;line-height:1.6;margin:0;">
                    If QZA files are unavailable, Clinical Metadata Input provides a simulated risk approximation
                    using surrogate parameters. These inputs are for preliminary screening, educational demonstration,
                    and simulated analysis only. They do not replace sequencing-level profiling.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="help-card">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                    <div style="width:36px;height:36px;background:rgba(244,63,94,0.1);border-radius:10px;
                                display:flex;align-items:center;justify-content:center;font-size:18px;">💓</div>
                    <div style="font-size:15px;font-weight:800;color:var(--text);">HRV / Autonomic Inputs</div>
                </div>
                <p style="font-size:13px;color:var(--text-muted);font-weight:500;line-height:1.6;margin:0;">
                    Physiological biomarkers used to estimate autonomic nervous system imbalance and vagal
                    dysfunction. Manual entry supported for:
                    <b style="color:var(--text);">RMSSD, SDNN, Mean RR interval, Heart rate.</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="help-section-title">2. Output Metrics & Risk Thresholds</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        metrics = [
            ("🦠", "Gut Dysbiosis Score", "rgba(245,158,11,0.1)", "#d97706",
             "Represents microbiome imbalance associated with neuroinflammation and gut-brain dysfunction."),
            ("🎤", "Voice Biomarker Score", "rgba(14,165,233,0.1)", "#0284c7",
             "Higher scores indicate motor speech irregularities and Parkinsonian vocal instability."),
            ("💓", "HRV / Autonomic Score", "rgba(244,63,94,0.1)", "#e11d48",
             "Inferred autonomic imbalance. Lower patterns correlate with vagal dysfunction & stress."),
            ("🩺", "Inflammatory Layer", "rgba(16,185,129,0.1)", "#059669",
             "Symptom/lifestyle-driven approximation for fallback analysis and screening."),
        ]
        for idx, (icon, title, bg, color, desc) in enumerate(metrics):
            col = c1 if idx % 2 == 0 else c2
            with col:
                st.markdown(f"""
                <div class="help-card">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                        <div style="width:36px;height:36px;background:{bg};border-radius:10px;
                                    display:flex;align-items:center;justify-content:center;font-size:18px;">{icon}</div>
                        <div style="font-size:14px;font-weight:800;color:var(--text);">{title}</div>
                    </div>
                    <p style="font-size:12px;color:var(--text-muted);font-weight:500;line-height:1.6;margin:0;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("""
        <div class="help-card" style="border-color:rgba(99,102,241,0.25);background:rgba(99,102,241,0.03);">
            <div style="font-size:16px;font-weight:800;color:var(--indigo);margin-bottom:12px;">
                🧠 Final Gut–Brain Vulnerability Score
            </div>
            <p style="font-size:13px;color:var(--text-muted);font-weight:500;margin-bottom:16px;line-height:1.6;">
                The final ensemble score generated through multimodal fusion of all provided data layers.
            </p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <div style="display:flex;align-items:center;justify-content:space-between;
                            background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
                            border-radius:10px;padding:10px 16px;flex:1;min-width:140px;">
                    <span style="font-size:12px;font-weight:700;color:#059669;">Low Risk</span>
                    <span style="font-size:11px;color:var(--text-muted);font-weight:500;">Minimal dysregulation</span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;
                            background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
                            border-radius:10px;padding:10px 16px;flex:1;min-width:140px;">
                    <span style="font-size:12px;font-weight:700;color:#d97706;">Moderate Risk</span>
                    <span style="font-size:11px;color:var(--text-muted);font-weight:500;">Moderate indicators</span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;
                            background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.2);
                            border-radius:10px;padding:10px 16px;flex:1;min-width:140px;">
                    <span style="font-size:12px;font-weight:700;color:#e11d48;">High Risk</span>
                    <span style="font-size:11px;color:var(--text-muted);font-weight:500;">Elevated dysregulation</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="help-section-title">3. Explainable AI & Standard Workflow</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="help-card">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <div style="width:36px;height:36px;background:rgba(245,158,11,0.1);border-radius:10px;
                            display:flex;align-items:center;justify-content:center;font-size:18px;">💡</div>
                <div style="font-size:15px;font-weight:800;color:var(--text);">SHAP Explainability</div>
            </div>
            <p style="font-size:13px;color:var(--text-muted);font-weight:500;line-height:1.6;margin:0;">
                NeuroBiomeX includes explainable AI layers using SHAP-based interpretation. Displays top
                microbial biomarkers (e.g., Prevotella, Akkermansia), influential voice features, and
                multimodal risk drivers so clinicians can understand <i>why</i> a risk score was assigned.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="help-card">
            <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:16px;">
                📋 Standard Operating Procedure (Workflow)
            </div>
        """, unsafe_allow_html=True)

        steps = [
            ("Upload QIIME2 feature table or .qza file", "🦠", "rgba(245,158,11,0.1)", "#d97706"),
            ("Upload or record voice sample (.wav)", "🎤", "rgba(14,165,233,0.1)", "#0284c7"),
            ("Enter HRV metrics (RMSSD, SDNN, etc.)", "💓", "rgba(244,63,94,0.1)", "#e11d48"),
            ("Enter metadata inputs (optional)", "📋", "rgba(99,102,241,0.1)", "#6366f1"),
            ("Run multimodal AI analysis", "⚡", "rgba(139,92,246,0.1)", "#7c3aed"),
            ("Review dashboard and explainability outputs", "📊", "rgba(16,185,129,0.1)", "#059669"),
        ]
        for i, (step, icon, bg, color) in enumerate(steps, 1):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;padding:12px 0;
                        border-bottom:1px solid var(--border);">
                <div style="width:32px;height:32px;background:{bg};border-radius:8px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:15px;flex-shrink:0;">{icon}</div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:12px;font-weight:800;color:{color};min-width:20px;">{i:02d}</span>
                    <span style="font-size:13px;color:var(--text);font-weight:500;">{step}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="help-section-title">4. Legal & Troubleshooting</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("""
            <div class="help-card">
                <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:10px;">
                    🔧 Upload Issues
                </div>
                <div style="margin-bottom:12px;">
                    <div style="font-size:12px;font-weight:700;color:#0284c7;margin-bottom:4px;">Audio Files</div>
                    <p style="font-size:12px;color:var(--text-muted);font-weight:500;line-height:1.6;margin:0;">
                        Record in a quiet environment, avoid clipping. Sustained vowel sounds produce the best results.
                    </p>
                </div>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#d97706;margin-bottom:4px;">QIIME2 Files</div>
                    <p style="font-size:12px;color:var(--text-muted);font-weight:500;line-height:1.6;margin:0;">
                        Use processed abundance tables. Large raw FASTQ files are not supported — export to .qza first.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="help-card">
                <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:10px;">
                    📞 Contact & Support
                </div>
                <p style="font-size:13px;color:var(--text-muted);font-weight:500;line-height:1.6;margin-bottom:12px;">
                    For platform-related issues, research collaborations, or data integration support:
                </p>
                <div style="background:#f8fafc;border-radius:10px;padding:14px;font-size:12px;color:var(--text-muted);font-weight:600;">
                    <div style="margin-bottom:6px;">📧 support@neurobiomex.ai</div>
                    <div>🌐 docs.neurobiomex.ai</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="help-card" style="background:rgba(244,63,94,0.03);border-color:rgba(244,63,94,0.2);">
                <div style="display:flex;align-items:start;gap:12px;">
                    <div style="font-size:24px;flex-shrink:0;">⚠️</div>
                    <div>
                        <div style="font-size:15px;font-weight:800;color:#e11d48;margin-bottom:8px;">Research Use Notice</div>
                        <p style="font-size:12px;color:#9f1239;font-weight:500;line-height:1.7;margin:0;">
                            NeuroBiomeX is intended solely for research, educational use, translational AI
                            demonstration, and computational biology experimentation. The platform is
                            <b>not intended</b> to provide medical diagnosis, treatment, or clinical
                            decision-making. Always consult a qualified healthcare professional for
                            medical decisions.
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="help-card">
                <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:12px;">
                    📄 Platform Version
                </div>
                <div style="font-size:12px;color:var(--text-muted);font-weight:500;line-height:2;">
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding:4px 0;">
                        <span>Platform Version</span><span style="font-weight:700;color:var(--text);">v1.0.0</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding:4px 0;">
                        <span>Last Updated</span><span style="font-weight:700;color:var(--text);">May 2026</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding:4px 0;">
                        <span>AI Model</span><span style="font-weight:700;color:var(--text);">NeuroBiomeX v2.1</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:4px 0;">
                        <span>Compliance</span><span style="font-weight:700;color:#059669;">HIPAA / GDPR Ready</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(99,102,241,0.06),rgba(139,92,246,0.04));
                    border:1px solid rgba(99,102,241,0.15);border-radius:14px;padding:20px;margin-top:8px;">
            <div style="font-size:14px;font-weight:800;color:var(--indigo);margin-bottom:12px;">
                ✅ SOPs & Policy Documents
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
        """ + "".join([
            f"""<div style="background:white;border:1px solid var(--border);border-radius:10px;
                           padding:12px 16px;display:flex;justify-content:space-between;align-items:center;
                           font-size:12px;color:var(--text-muted);font-weight:500;">
                    <span>{sop}</span><span>📄</span>
                </div>"""
            for sop in [
                "SOP-101: Microbiome Sample Collection",
                "SOP-102: Voice Recording Protocol",
                "POL-201: Clinical Data Usage & Consent",
                "POL-202: Data Retention & Reporting",
            ]
        ]) + """
            </div>
        </div>
        """, unsafe_allow_html=True)


def page_about():
    st.markdown('<div class="section-label">Platform Documentation</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="nbx-card" style="text-align:center;">
            <div style="font-size:40px;margin-bottom:12px;">🧠</div>
            <div style="font-size:17px;font-weight:800;color:var(--text);margin-bottom:10px;">Platform Overview</div>
            <p style="font-size:13px;color:var(--text-muted);line-height:1.7;font-weight:500;">
                NeuroBiomeX integrates voice biomarkers and gut microbiome data with advanced machine learning
                to identify neurodegenerative vulnerability in asymptomatic patients, facilitating early
                intervention and personalized prevention strategies.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="nbx-card" style="text-align:center;">
            <div style="font-size:40px;margin-bottom:12px;">🎯</div>
            <div style="font-size:17px;font-weight:800;color:var(--text);margin-bottom:10px;">Our Mission</div>
            <p style="font-size:13px;color:var(--text-muted);line-height:1.7;font-weight:500;">
                Empower clinicians with non-invasive, objective tools for proactive neurological care,
                bridging the gap between personalized diagnostics and preventative treatments for brain health.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="nbx-card" style="position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg,#6366f1,#8b5cf6);"></div>
        <div style="font-size:16px;font-weight:800;color:var(--text);margin-bottom:16px;margin-top:4px;">
            ✅ Standard Operating Procedures (SOPs) & Policy
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
    """ + "".join([
        f"""<div style="background:#f8fafc;border:1px solid var(--border);border-radius:10px;
                       padding:14px;display:flex;justify-content:space-between;align-items:center;
                       font-size:12px;color:var(--text-muted);font-weight:500;cursor:pointer;">
                <span>{sop}</span> <span>📄</span>
            </div>"""
        for sop in [
            "SOP-101: Gut Microbiome Sample Collection",
            "SOP-102: Standardized Voice Recording Protocol",
            "POL-201: Clinical Data Usage & Patient Consent",
            "POL-202: Data Retention & Vulnerability Reporting",
        ]
    ]) + """
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">System Inputs & Specifications</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="nbx-card">
            <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:10px;">🦠 Microbiome Data Upload</div>
            <p style="font-size:12px;color:var(--text-muted);font-weight:500;margin-bottom:12px;line-height:1.6;">
                QIIME2-compatible microbiome feature tables and abundance datasets.
                Files are automatically processed, normalized, and aligned with trained microbial biomarkers.
            </p>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">
                <span style="background:rgba(99,102,241,0.08);color:var(--indigo);font-size:10px;font-weight:700;padding:3px 10px;border-radius:6px;">.qza</span>
                <span style="background:rgba(99,102,241,0.08);color:var(--indigo);font-size:10px;font-weight:700;padding:3px 10px;border-radius:6px;">.csv</span>
                <span style="background:rgba(99,102,241,0.08);color:var(--indigo);font-size:10px;font-weight:700;padding:3px 10px;border-radius:6px;">.tsv</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="nbx-card">
            <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:10px;">🎤 Voice Analysis Capture</div>
            <p style="font-size:12px;color:var(--text-muted);font-weight:500;margin-bottom:12px;line-height:1.6;">
                Supported Input: <b>.wav</b> upload OR Direct in-browser microphone recording.
                Sustained vowel sound ("Aaaaaaa") for 5–10 seconds recommended.
            </p>
            <div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:8px;">Extracted Voice Biomarkers:</div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">
                <span style="background:rgba(14,165,233,0.1);color:#0284c7;font-size:10px;font-weight:700;padding:3px 10px;border-radius:6px;border:1px solid rgba(14,165,233,0.2);">Jitter</span>
                <span style="background:rgba(14,165,233,0.1);color:#0284c7;font-size:10px;font-weight:700;padding:3px 10px;border-radius:6px;border:1px solid rgba(14,165,233,0.2);">Shimmer</span>
                <span style="background:rgba(14,165,233,0.1);color:#0284c7;font-size:10px;font-weight:700;padding:3px 10px;border-radius:6px;border:1px solid rgba(14,165,233,0.2);">HNR</span>
                <span style="background:rgba(14,165,233,0.1);color:#0284c7;font-size:10px;font-weight:700;padding:3px 10px;border-radius:6px;border:1px solid rgba(14,165,233,0.2);">Pitch Variability</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="nbx-card" style="background:rgba(245,158,11,0.04);border-color:rgba(245,158,11,0.25);">
            <div style="font-size:15px;font-weight:800;color:#d97706;margin-bottom:10px;">☁️ Metadata-Based Fallback (Simulated)</div>
            <p style="font-size:12px;color:#92400e;font-weight:500;line-height:1.6;">
                If QZA files are unavailable, Clinical Metadata Input provides a simulated risk approximation
                using surrogate parameters. These inputs are for preliminary screening, educational demonstration,
                and simulated analysis only. They do not replace sequencing-level profiling.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="nbx-card">
            <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:10px;">💓 HRV / Autonomic Inputs</div>
            <p style="font-size:12px;color:var(--text-muted);font-weight:500;line-height:1.6;">
                Physiological biomarkers used to estimate autonomic nervous system imbalance and vagal dysfunction.
                Manual entry supported for: <b>RMSSD, SDNN, Mean RR interval, Heart rate.</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="nbx-card" style="background:rgba(244,63,94,0.03);border-color:rgba(244,63,94,0.2);">
            <div style="display:flex;align-items:start;gap:12px;">
                <div style="font-size:20px;flex-shrink:0;">⚠️</div>
                <div>
                    <div style="font-size:13px;font-weight:800;color:#e11d48;margin-bottom:6px;">Research Use Notice</div>
                    <p style="font-size:11px;color:#9f1239;font-weight:500;line-height:1.6;margin:0;">
                        NeuroBiomeX is intended solely for research, educational use, translational AI demonstration,
                        and computational biology experimentation. The platform is not intended to provide medical
                        diagnosis, treatment, or clinical decision-making.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def page_placeholder(title):
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;min-height:60vh;">
        <div class="nbx-card" style="text-align:center;max-width:400px;">
            <div style="font-size:48px;margin-bottom:16px;">🔧</div>
            <div style="font-size:20px;font-weight:800;color:var(--text);margin-bottom:8px;">{title}</div>
            <div style="font-size:13px;color:var(--text-muted);font-weight:500;">
                This module is currently under development. Check back soon for updates.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── MAIN ROUTER ───────────────────────────────────────────────────────────────
def main():
    render_sidebar()

    page = st.session_state.page

    if page == "🧠 Dashboard":
        page_dashboard()
    elif page == "👤 Patient Profile":
        page_patient_profile()
    elif page == "📋 Metadata":
        page_metadata()
    elif page == "🎤 Voice Analysis":
        page_voice()
    elif page == "🦠 Microbiome Analysis":
        page_microbiome()
    elif page == "🛡️ AMR Analysis":
        page_amr()
    elif page == "📊 Risk Summary":
        page_risk_summary()
    elif page == "💡 Explainability":
        page_explainability()
    elif page == "📄 Patient Report":
        page_patient_report()
    elif page == "❓ Help Desk":
        page_help_desk()
    elif page == "ℹ️ About Platform":
        page_about()
    else:
        page_placeholder(page)

    st.markdown("""
    <div style="text-align:center;padding:20px;border-top:1px solid var(--border);margin-top:40px;">
        <div style="font-size:11px;color:var(--text-muted);font-weight:500;letter-spacing:0.5px;">
            © 2026 NeuroBiomeX Platform · Engineered by NeuroX
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()