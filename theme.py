"""
theme.py — ธีม UI ใหม่สำหรับ waste-ai-dashboard
สไตล์: Aurora gradient + Frosted glass + Minimal

วิธีใช้ (ไม่ต้องแก้ logic เดิมเลย):
    1) วางไฟล์นี้ไว้ข้าง app.py
    2) ใน app.py เพิ่ม
           from theme import inject_theme
       แล้วเรียก  inject_theme()  ต่อจาก  st.set_page_config(...)
       และ "หลัง" บล็อก st.markdown("<style>...") เดิม (เพื่อให้ธีมนี้ override ได้)
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
# ink        #0f2a2e  ข้อความหลัก (เขียวเข้มเกือบดำ)
# muted      #5b7178  ข้อความรอง
# accent     #0e7c86  teal — สีเน้นเดียวของทั้งระบบ
# accent-2   #4f6bed  indigo — ใช้เฉพาะในเฉดกราเดียนต์
# bg mesh    mint → sky → lavender → peach (อ่อนมาก เพื่อให้ยัง minimal)
# ---------------------------------------------------------------------------

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
  --glass: rgba(255, 255, 255, .62);
  --glass-strong: rgba(255, 255, 255, .82);
  --glass-border: rgba(255, 255, 255, .75);
  --shadow-sm: 0 1px 2px rgba(15, 42, 46, .04), 0 4px 14px rgba(15, 42, 46, .05);
  --shadow-md: 0 2px 4px rgba(15, 42, 46, .04), 0 14px 34px rgba(15, 42, 46, .09);
  --radius-lg: 20px;
  --radius-md: 14px;
  --radius-sm: 10px;
}

/* ============ 1) พื้นหลัง Aurora gradient (เคลื่อนไหวช้า ๆ) ============ */
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
  background-size: 140% 140%, 140% 140%, 140% 140%, 140% 140%, 100% 100%;
  animation: auroraDrift 26s ease-in-out infinite alternate;
}

/* เกรนบาง ๆ ให้พื้นหลังดูมีมิติ ไม่แบนเกินไป */
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

@keyframes auroraDrift {
  0%   { background-position: 0% 0%,   100% 0%,   100% 100%, 0% 100%, 0 0; }
  100% { background-position: 18% 12%, 82% 16%,   84% 84%,   16% 88%, 0 0; }
}

/* ============ 2) Layout & Typography ============ */
.block-container {
  max-width: 1180px !important;
  padding-top: 1.4rem !important;
  padding-bottom: 3rem !important;
}

html, body, button, input, textarea, select,
[data-testid="stMarkdownContainer"],
[data-testid="stMetric"], [data-testid="stExpander"],
[data-testid="stAppViewContainer"] {
  font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
}

h1, h2, h3, h4 { color: var(--ink) !important; letter-spacing: -.02em; font-weight: 600 !important; }
[data-testid="stCaptionContainer"], .upload-hint, .upload-panel-subtitle,
.collection-subtitle, .settings-subtitle { color: var(--muted) !important; }

hr {
  border: 0 !important;
  height: 1px !important;
  margin: 26px 0 !important;
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
  animation: riseIn .7s cubic-bezier(.2,.7,.2,1) both;   /* ลูกเล่นตอนโหลดหน้า: จุดเดียว */
}
.app-brand::after {                                      /* แสงกราเดียนต์มุมขวา */
  content: "";
  position: absolute; right: -60px; top: -80px;
  width: 260px; height: 260px; border-radius: 50%;
  background: radial-gradient(circle, rgba(79,107,237,.20), transparent 65%);
  pointer-events: none;
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
  font-size: 26px !important; font-weight: 700 !important;
  letter-spacing: -.03em;
  background: linear-gradient(90deg, var(--ink) 30%, var(--accent) 100%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.app-subtitle { color: var(--muted) !important; font-size: 12.5px !important; }
.header-divider { display: none !important; }

@keyframes riseIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: none; }
}

/* ============ 4) การ์ดแบบ Frosted glass ============ */
[data-testid="stMetric"],
[data-testid="stExpander"],
.settings-card, .camera-detail-card, .collection-section, .collection-stop {
  border: 1px solid var(--glass-border) !important;
  background: var(--glass) !important;
  -webkit-backdrop-filter: blur(16px) saturate(140%);
          backdrop-filter: blur(16px) saturate(140%);
  box-shadow: var(--shadow-sm) !important;
}

[data-testid="stMetric"] { border-radius: var(--radius-md) !important; padding: 14px 18px !important; }
[data-testid="stExpander"] { border-radius: var(--radius-md) !important; }
.settings-card, .camera-detail-card { border-radius: var(--radius-md) !important; }
.collection-section { border-radius: var(--radius-lg) !important; box-shadow: var(--shadow-md) !important; }
.collection-stop { border-radius: var(--radius-md) !important; }

[data-testid="stMetric"]:hover,
[data-testid="stExpander"]:hover,
.collection-stop:hover {
  transform: translateY(-2px);
  border-color: #fff !important;
  background: var(--glass-strong) !important;
  box-shadow: var(--shadow-md) !important;
}

[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: var(--ink) !important; font-weight: 700 !important; letter-spacing: -.02em; }

/* Expander header */
[data-testid="stExpander"] summary {
  background: transparent !important;
  color: var(--ink) !important;
  font-weight: 600 !important;
}
[data-testid="stExpander"] summary:hover { background: var(--accent-soft) !important; }

/* ============ 5) ปุ่ม ============ */
.stButton > button,
[data-testid="stDownloadButton"] > button,
[data-testid="stPopover"] > button {
  border: 1px solid rgba(15,42,46,.10) !important;
  border-radius: 12px !important;
  background: var(--glass-strong) !important;
  color: var(--ink) !important;
  font-weight: 600 !important;
  min-height: 40px !important;
  box-shadow: var(--shadow-sm);
  transition: transform .18s ease, box-shadow .18s ease, background .18s ease, border-color .18s ease;
}
.stButton > button:hover,
[data-testid="stDownloadButton"] > button:hover,
[data-testid="stPopover"] > button:hover {
  transform: translateY(-1px);
  border-color: rgba(14,124,134,.45) !important;
  color: var(--accent) !important;
  box-shadow: 0 8px 20px rgba(14,124,134,.16) !important;
}
.stButton > button:active { transform: translateY(0) scale(.98); }

/* ปุ่มหลัก (type="primary") ใช้กราเดียนต์ */
.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"] {
  border: 0 !important;
  color: #fff !important;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%) !important;
  box-shadow: 0 8px 22px rgba(14,124,134,.30) !important;
}
.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
  color: #fff !important;
  filter: brightness(1.06);
  box-shadow: 0 12px 28px rgba(79,107,237,.32) !important;
}

/* ============ 6) Input / Upload ============ */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] > div {
  border-radius: var(--radius-sm) !important;
  border: 1px solid rgba(15,42,46,.10) !important;
  background: rgba(255,255,255,.75) !important;
  transition: border-color .18s ease, box-shadow .18s ease;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(14,124,134,.16) !important;
}

[data-testid="stFileUploader"] {
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--glass) !important;
}
[data-testid="stFileUploaderDropzone"] {
  border: 1.5px dashed rgba(14,124,134,.35) !important;
  border-radius: var(--radius-sm) !important;
  background: rgba(255,255,255,.55) !important;
  transition: background .2s ease, border-color .2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--accent) !important;
  background: rgba(14,124,134,.07) !important;
}

/* ============ 7) Sidebar ============ */
section[data-testid="stSidebar"] {
  background: rgba(255,255,255,.55) !important;
  -webkit-backdrop-filter: blur(22px) saturate(150%);
          backdrop-filter: blur(22px) saturate(150%);
  border-right: 1px solid var(--glass-border) !important;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: var(--glass) !important;
  border-radius: var(--radius-md) !important;
}

/* ============ 8) Tabs (ถ้ามี) ============ */
[data-baseweb="tab-list"] { gap: 6px; border-bottom: 0 !important; }
[data-baseweb="tab"] {
  border-radius: 999px !important;
  padding: 6px 16px !important;
  color: var(--muted) !important;
  font-weight: 600 !important;
  transition: background .2s ease, color .2s ease;
}
[data-baseweb="tab"][aria-selected="true"] {
  color: #fff !important;
  background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
  box-shadow: 0 6px 16px rgba(14,124,134,.28);
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

/* ============ 9) Alert / Level / Recommend ============ */
[data-testid="stAlert"] {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--glass-border) !important;
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
}
.level-box {
  border-radius: 12px !important;
  box-shadow: 0 6px 16px rgba(15,42,46,.10) !important;
  letter-spacing: .01em;
}
.recommend, .camera-action-card, .chart-tip, .collection-example {
  background: rgba(255,255,255,.55) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 12px !important;
  color: #2f4a51 !important;
}
.settings-section-label::before {
  background: linear-gradient(180deg, var(--accent), var(--accent-2)) !important;
}
.action-label { color: var(--ink) !important; }

/* ============ 10) ส่วนรถเก็บขยะ ============ */
.collection-road {
  background: linear-gradient(180deg, #33545c 0%, #23393f 100%) !important;
  border-radius: 18px !important;
  box-shadow: inset 0 4px 14px rgba(0,0,0,.22) !important;
}
.collection-title, .settings-title, .section-title,
.upload-panel-title, .history-title, .collection-camera { color: var(--ink) !important; }
.collection-info summary {
  background: var(--glass-strong) !important;
  border-color: rgba(15,42,46,.10) !important;
  border-radius: 12px !important;
}
.collection-info-pop {
  background: rgba(255,255,255,.92) !important;
  -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-md) !important;
}

/* ============ 11) รูปภาพ / กราฟ / ตาราง ============ */
[data-testid="stImage"] img { border-radius: 14px !important; box-shadow: var(--shadow-sm); }

.js-plotly-plot .plotly .main-svg { background: transparent !important; }
.js-plotly-plot .plotly .main-svg .bg { fill: transparent !important; }
[data-testid="stPlotlyChart"] {
  padding: 8px;
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
  background: var(--glass);
  -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
  box-shadow: var(--shadow-sm);
}
[data-testid="stDataFrame"] {
  border-radius: var(--radius-md); overflow: hidden;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-sm);
}

/* ============ 12) Scrollbar & Selection ============ */
::selection { background: rgba(14,124,134,.22); }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb {
  background: rgba(14,124,134,.28); border-radius: 999px;
  border: 2px solid transparent; background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover { background: rgba(14,124,134,.5); background-clip: content-box; border: 2px solid transparent; }

/* ============ 13) Accessibility ============ */
:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  [data-testid="stApp"]::before, .app-brand { animation: none !important; }
  * { transition-duration: .01ms !important; }
}

@media (max-width: 700px) {
  .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
  .app-title { font-size: 21px !important; }
}
</style>
"""


def inject_theme() -> None:
    """ฉีดธีมใหม่ลงในแอป — เรียกหลัง st.set_page_config และหลัง CSS เดิมของ app.py"""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# (ทางเลือก) ตั้งค่ากราฟ Plotly ให้เข้ากับธีม
#   fig = style_plotly(fig)
# ---------------------------------------------------------------------------
def style_plotly(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Prompt, Noto Sans Thai, sans-serif", color="#0f2a2e"),
        margin=dict(l=12, r=12, t=40, b=12),
        colorway=["#0e7c86", "#4f6bed", "#7fd1b9", "#f2a65a", "#e5646e"],
    )
    fig.update_xaxes(gridcolor="rgba(15,42,46,.07)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(15,42,46,.07)", zeroline=False)
    return fig
