"""
theme.py — ธีม UI สำหรับ waste-ai-dashboard
สไตล์: Aurora gradient + Frosted glass + Minimal (รองรับ Light / Dark Mode สมบูรณ์)
"""

import streamlit as st

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

:root {
  --ink: #0f2a2e;
  --muted: #5b7178;
  --line: rgba(15, 42, 46, .08);
  --accent: #0e7c86;
  --accent-2: #4f6bed;
  --accent-soft: rgba(14, 124, 134, .10);
  --glass: rgba(255, 255, 255, .66);
  --glass-strong: rgba(255, 255, 255, .85);
  --glass-border: rgba(255, 255, 255, .75);
  --shadow-sm: 0 1px 2px rgba(15, 42, 46, .04), 0 4px 14px rgba(15, 42, 46, .05);
  --shadow-md: 0 2px 4px rgba(15, 42, 46, .04), 0 14px 34px rgba(15, 42, 46, .09);
  --radius-lg: 20px;
  --radius-md: 14px;
  --radius-sm: 10px;
}

/* ============ 1) พื้นหลัง Aurora gradient ============ */
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
  background: transparent !important;
  color: var(--ink);
}

[data-testid="stApp"]::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -2;
  background:
    radial-gradient(60% 55% at 12% 8%,  #c9f2e3 0%, transparent 70%),
    radial-gradient(55% 50% at 92% 10%, #cfe0ff 0%, transparent 70%),
    radial-gradient(60% 55% at 85% 95%, #e3d9ff 0%, transparent 70%),
    radial-gradient(50% 45% at 8%  92%, #ffe4d3 0%, transparent 70%),
    linear-gradient(135deg, #f3fbf8 0%, #f1f5ff 55%, #f8f3ff 100%);
  background-size: 180% 180%, 180% 180%, 180% 180%, 180% 180%, 160% 160%;
  animation: auroraFlow 22s ease-in-out infinite alternate;
}

[data-testid="stApp"]::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  opacity: .35;
  background-image: radial-gradient(rgba(15,42,46,.045) 1px, transparent 1px);
  background-size: 22px 22px;
  -webkit-mask-image: linear-gradient(180deg, #000 0%, transparent 70%);
          mask-image: linear-gradient(180deg, #000 0%, transparent 70%);
}

@keyframes auroraFlow {
  0%   { background-position: 0% 12%, 100% 0%, 90% 100%, 0% 88%, 0% 0%; }
  50%  { background-position: 20% 30%, 75% 18%, 70% 80%, 25% 70%, 50% 50%; }
  100% { background-position: 65% 15%, 18% 78%, 35% 8%, 75% 92%, 100% 100%; }
}

/* ============ 2) Layout & Typography (Preserving Material Icons) ============ */
.block-container {
  max-width: 1180px !important;
  padding-top: 1.4rem !important;
  padding-bottom: 3rem !important;
}

html, body, button, input, textarea, select,
[data-testid="stMarkdownContainer"],
[data-testid="stMetric"],
[data-testid="stWidgetLabel"],
[data-testid="stPopover"] {
  font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
}

/* ป้องกันไอคอนลูกศรของ Streamlit กลายเป็นข้อความ _arrow_right */
span[data-testid="stIconMaterial"], [data-testid="stIconMaterial"],
.material-icons, .material-icons-outlined,
.material-symbols-rounded, .material-symbols-outlined,
[data-testid="stExpander"] summary svg {
  font-family: "Material Symbols Rounded", "Material Icons" !important;
  font-feature-settings: "liga" !important;
  font-weight: normal !important;
  letter-spacing: normal !important;
  text-transform: none !important;
  white-space: nowrap !important;
  word-wrap: normal !important;
  direction: ltr !important;
  line-height: 1 !important;
}

h1, h2, h3, h4 {
  color: var(--ink) !important;
  letter-spacing: -.02em;
  font-weight: 600 !important;
  font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
}

[data-testid="stCaptionContainer"], .upload-hint, .upload-panel-subtitle,
.collection-subtitle, .settings-subtitle {
  color: var(--muted) !important;
}

hr {
  border: 0 !important;
  height: 1px !important;
  margin: 24px 0 !important;
  background: linear-gradient(90deg, transparent, rgba(14,124,134,.28), transparent) !important;
}

/* ============ 3) Header / Brand ============ */
.app-brand {
  position: relative;
  overflow: hidden;
  min-height: 74px;
  padding: 14px 20px !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
  background: linear-gradient(120deg, rgba(255,255,255,.85), rgba(255,255,255,.55)) !important;
  -webkit-backdrop-filter: blur(18px) saturate(140%);
          backdrop-filter: blur(18px) saturate(140%);
  box-shadow: var(--shadow-md) !important;
}
.app-brand-icon {
  width: 50px !important; height: 50px !important;
  border-radius: 15px !important;
  border: 0 !important;
  color: #fff;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%) !important;
  box-shadow: 0 8px 20px rgba(14,124,134,.32) !important;
}
.app-title {
  font-size: 25px !important;
  font-weight: 700 !important;
  letter-spacing: -.025em;
  color: var(--ink) !important;
}
.app-subtitle { color: var(--muted) !important; font-size: 12.5px !important; }
.header-divider { display: none !important; }

/* ============ 4) การ์ดแบบ Frosted glass ============ */
[data-testid="stMetric"],
[data-testid="stExpander"],
.settings-card, .camera-detail-card, .collection-section, .collection-stop {
  border: 1px solid var(--glass-border) !important;
  border-radius: 20px !important;
  background: var(--glass) !important;
  -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
          backdrop-filter: blur(20px) saturate(150%) !important;
  box-shadow: var(--shadow-sm) !important;
}

[data-testid="stMetric"] { padding: 14px 18px !important; }
[data-testid="stExpander"], [data-testid="stExpander"] details {
  overflow: hidden !important;
}
[data-testid="stExpander"] summary {
  display: flex !important;
  align-items: center !important;
  gap: .5rem !important;
  background: transparent !important;
  color: var(--ink) !important;
  font-weight: 600 !important;
  font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
}
[data-testid="stExpander"] summary p {
  font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
  color: inherit !important;
}
[data-testid="stExpander"] summary:hover {
  background: var(--accent-soft) !important;
}

[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: var(--ink) !important; font-weight: 700 !important; }

/* ============ 5) ปุ่ม & File Uploader ============ */
.stButton > button,
[data-testid="stDownloadButton"] > button,
[data-testid="stPopover"] > button {
  border: 1px solid rgba(15,42,46,.10) !important;
  border-radius: 13px !important;
  background: var(--glass-strong) !important;
  color: var(--ink) !important;
  font-weight: 600 !important;
  min-height: 40px !important;
  box-shadow: var(--shadow-sm);
  transition: transform .18s ease, box-shadow .18s ease, background .18s ease !important;
}
.stButton > button:hover,
[data-testid="stDownloadButton"] > button:hover,
[data-testid="stPopover"] > button:hover {
  transform: translateY(-1px);
  border-color: rgba(14,124,134,.45) !important;
  color: var(--accent) !important;
}

.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"] {
  border: 0 !important;
  color: #fff !important;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%) !important;
  box-shadow: 0 8px 22px rgba(14,124,134,.30) !important;
}

[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > section {
  background: transparent !important;
  border: 0 !important;
  padding: 0 !important;
  box-shadow: none !important;
}
[data-testid="stFileUploaderDropzone"] {
  min-height: 76px !important;
  padding: 14px 16px !important;
  border: 1.5px dashed rgba(14,124,134,.35) !important;
  border-radius: 18px !important;
  background: rgba(255,255,255,.55) !important;
}

/* ============ 6) กราฟ Plotly ============ */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
.js-plotly-plot .plotly .main-svg .bg { fill: transparent !important; }
[data-testid="stPlotlyChart"] {
  padding: 8px;
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
  background: var(--glass);
  -webkit-backdrop-filter: blur(14px);
          backdrop-filter: blur(14px);
  box-shadow: var(--shadow-sm);
}
</style>
"""


def inject_theme() -> None:
    """Apply glass theme with clean Light / Dark mode support."""
    dark_mode = bool(st.session_state.get("theme_dark_mode", False))
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    if dark_mode:
        dark_css = """
        <style>
        :root {
          --ink: #eff8f6;
          --muted: #b8cecb;
          --accent: #75dfcf;
          --accent-2: #9aaaff;
          --glass: rgba(28, 53, 63, .82);
          --glass-strong: rgba(39, 70, 83, .92);
          --glass-border: rgba(180, 225, 220, .14);
        }
        [data-testid="stApp"], [data-testid="stAppViewContainer"],
        [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
          background: transparent !important;
          color: var(--ink) !important;
        }
        [data-testid="stApp"]::before {
          background:
            radial-gradient(60% 55% at 12% 8%, rgba(22,133,116,.48), transparent 70%),
            radial-gradient(55% 50% at 92% 10%, rgba(70,91,177,.43), transparent 70%),
            radial-gradient(60% 55% at 85% 95%, rgba(116,73,157,.38), transparent 70%),
            radial-gradient(50% 45% at 8% 92%, rgba(145,91,70,.22), transparent 70%),
            linear-gradient(135deg, #0d1b23 0%, #142832 55%, #1b2031 100%) !important;
        }
        [data-testid="stMetric"], [data-testid="stExpander"],
        .settings-card, .camera-detail-card, .collection-section,
        .collection-stop, .app-brand, .recommend, .camera-action-card,
        .chart-tip, .collection-example, [data-testid="stPlotlyChart"] {
          background: linear-gradient(145deg, rgba(35,65,75,.86), rgba(19,39,49,.78)) !important;
          border: 1px solid rgba(180, 225, 220, .12) !important;
          color: #eff8f6 !important;
        }
        .app-title, .collection-title, .settings-title, .section-title,
        .upload-camera-label, .history-title, .collection-camera,
        .collection-war, .camera-image-title, .action-label,
        [data-testid="stMetricValue"], [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary p, [data-testid="stWidgetLabel"] {
          color: #eff8f6 !important;
          -webkit-text-fill-color: #eff8f6 !important;
        }
        .app-subtitle, .upload-hint, .settings-subtitle, .collection-subtitle,
        .collection-level, .collection-detail, .collection-note, .action-text,
        [data-testid="stCaptionContainer"], [data-testid="stMetricLabel"] {
          color: #b8cecb !important;
          -webkit-text-fill-color: #b8cecb !important;
        }
        .stButton > button, [data-testid="stDownloadButton"] button,
        [data-testid="stPopover"] > button {
          background: #274653 !important;
          color: #eff8f6 !important;
          border: 1px solid rgba(180, 225, 220, .16) !important;
        }
        .stButton > button:hover, [data-testid="stDownloadButton"] button:hover,
        [data-testid="stPopover"] > button:hover {
          background: #356273 !important;
          color: #ffffff !important;
        }
        [data-testid="stFileUploaderDropzone"] {
          background: rgba(15, 32, 41, .72) !important;
          border: 1.5px dashed rgba(117, 223, 207, .35) !important;
          color: #eaf6f3 !important;
        }
        [data-testid="stFileUploaderDropzone"] button {
          background: #d8f4ed !important;
          color: #164e4d !important;
        }
        [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
        [data-baseweb="select"] > div {
          background: rgba(10, 24, 31, .82) !important;
          color: #eff8f6 !important;
          border-color: rgba(180, 220, 215, .20) !important;
        }
        .collection-info summary {
          background: rgba(37, 63, 73, .90) !important;
          color: #eff8f6 !important;
          border-color: rgba(180, 220, 215, .20) !important;
        }
        .collection-info-pop {
          background: rgba(20, 38, 47, .98) !important;
          color: #eff8f6 !important;
          border: 1px solid rgba(180, 220, 215, .18) !important;
        }
        </style>
        """
        st.markdown(dark_css, unsafe_allow_html=True)


def style_plotly(fig):
    dark_mode = bool(st.session_state.get("theme_dark_mode", False))
    text_color = "#eff8f6" if dark_mode else "#0f2a2e"
    grid_color = "rgba(239, 248, 246, .12)" if dark_mode else "rgba(15, 42, 46, .08)"

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Prompt, Noto Sans Thai, sans-serif", size=11, color=text_color),
        margin=dict(l=12, r=12, t=20, b=12),
    )
    fig.update_xaxes(gridcolor=grid_color, zeroline=False, tickfont=dict(color=text_color), title_font=dict(color=text_color))
    fig.update_yaxes(gridcolor=grid_color, zeroline=False, tickfont=dict(color=text_color), title_font=dict(color=text_color))
    return fig
