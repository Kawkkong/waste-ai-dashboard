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
    """Apply glass theme without disturbing Streamlit's internal icon/layout fonts."""
    dark_mode = bool(st.session_state.get("theme_dark_mode", False))

    common_css = """
    <style>
    :root { --glass-radius: 24px; }

    /* Rounded, soft glass surfaces */
    [data-testid="stMetric"],
    [data-testid="stExpander"],
    .settings-card, .camera-detail-card, .collection-section,
    .collection-stop, .app-brand, .recommend, .camera-action-card,
    .chart-tip, .collection-example {
      border: 0 !important;
      border-radius: var(--glass-radius) !important;
      box-shadow: 0 14px 36px rgba(28,72,78,.075) !important;
      -webkit-backdrop-filter: blur(26px) saturate(165%) !important;
      backdrop-filter: blur(26px) saturate(165%) !important;
    }

    /* Preserve Streamlit's native Material Symbols font and ligatures */
    .material-icons, .material-icons-outlined, .material-symbols-rounded,
    .material-symbols-outlined, [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
      font-family: "Material Symbols Rounded", "Material Icons" !important;
      font-feature-settings: "liga" !important;
      font-weight: normal !important;
      letter-spacing: normal !important;
      text-transform: none !important;
      white-space: nowrap !important;
      word-wrap: normal !important;
      direction: ltr !important;
    }

    /* Set typeface on control roots only; never force fonts on every child */
    button, [role="button"], input, textarea, select,
    [data-testid="stWidgetLabel"], [data-testid="stExpander"] summary,
    [data-testid="stPopover"] {
      font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
    }
    button span:not(.material-icons):not(.material-icons-outlined):not(.material-symbols-rounded):not(.material-symbols-outlined),
    [role="button"] span:not(.material-icons):not(.material-symbols-rounded) {
      font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
    }

    /* Expander geometry and typography without changing its internal layout */
    [data-testid="stExpander"],
    [data-testid="stExpander"] details {
      border: 0 !important;
      border-radius: 24px !important;
      outline: 0 !important;
      overflow: hidden !important;
    }
    [data-testid="stExpander"] summary {
      display: flex !important;
      align-items: center !important;
      gap: .5rem !important;
      font-weight: 600 !important;
    }
    [data-testid="stExpander"] summary svg {
      flex: 0 0 auto !important;
      display: inline-block !important;
    }

    /* Uploader: a single rounded dropzone, transparent wrapper */
    [data-testid="stFileUploader"] {
      background: transparent !important;
      border: 0 !important;
      box-shadow: none !important;
      padding: 0 !important;
      margin: 0 !important;
      min-width: 0 !important;
    }
    [data-testid="stFileUploader"] > section {
      background: transparent !important;
      border: 0 !important;
      box-shadow: none !important;
      padding: 0 !important;
      min-width: 0 !important;
    }
    [data-testid="stFileUploaderDropzone"] {
      display: flex !important;
      align-items: center !important;
      flex-wrap: wrap !important;
      gap: 10px !important;
      box-sizing: border-box !important;
      min-height: 68px !important;
      padding: 12px 14px !important;
      border: 0 !important;
      outline: 0 !important;
      border-radius: 20px !important;
      box-shadow: none !important;
      transition: background .25s ease, transform .25s ease !important;
    }
    [data-testid="stFileUploaderDropzone"] > div {
      min-width: 0 !important;
      flex: 1 1 180px !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
      flex: 0 0 auto !important;
      border: 0 !important;
      border-radius: 12px !important;
      box-shadow: none !important;
      font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
      white-space: nowrap !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
      min-width: 0 !important;
      line-height: 1.45 !important;
    }

    /* Smooth hover; don't let browser defaults flash white */
    .stButton > button, [data-testid="stDownloadButton"] button,
    [data-testid="stPopover"] > button {
      border-radius: 13px !important;
      transition: transform .2s ease, box-shadow .2s ease, background .2s ease, color .2s ease !important;
    }
    .stButton > button:hover, [data-testid="stDownloadButton"] button:hover,
    [data-testid="stPopover"] > button:hover {
      transform: translateY(-1px);
    }

    /* Animated aurora background */
    [data-testid="stApp"]::before {
      background-size: 180% 180%,180% 180%,180% 180%,180% 180%,160% 160% !important;
      animation: auroraDrift 30s ease-in-out infinite alternate !important;
      will-change: background-position;
    }
    @keyframes auroraDrift {
      0% { background-position:0% 0%,100% 0%,100% 100%,0% 100%,0% 0%; }
      50% { background-position:12% 18%,88% 8%,80% 88%,18% 82%,50% 50%; }
      100% { background-position:20% 8%,78% 18%,88% 78%,8% 92%,100% 100%; }
    }
    @media (prefers-reduced-motion: reduce) {
      [data-testid="stApp"]::before { animation:none !important; }
      *,*::before,*::after { transition-duration:.01ms !important; }
    }
    </style>
    """

    light_css = """
    <style>
    :root { --ink:#17383b; --muted:#60797b; }
    [data-testid="stApp"],[data-testid="stAppViewContainer"] { color:var(--ink) !important; }
    [data-testid="stApp"]::before {
      background:
        radial-gradient(60% 55% at 12% 8%,rgba(171,235,213,.88),transparent 70%),
        radial-gradient(55% 50% at 92% 10%,rgba(184,207,255,.82),transparent 70%),
        radial-gradient(60% 55% at 85% 95%,rgba(218,196,255,.76),transparent 70%),
        radial-gradient(50% 45% at 8% 92%,rgba(255,220,195,.72),transparent 70%),
        linear-gradient(135deg,#f2fbf7 0%,#eff4ff 55%,#f8f2ff 100%) !important;
    }
    [data-testid="stMetric"],[data-testid="stExpander"],
    .settings-card,.camera-detail-card,.collection-section,
    .collection-stop,.app-brand,.recommend,.camera-action-card,
    .chart-tip,.collection-example {
      background:linear-gradient(145deg,rgba(255,255,255,.70),rgba(255,255,255,.38)) !important;
    }
    [data-testid="stFileUploaderDropzone"] { background:rgba(255,255,255,.48) !important; }
    [data-testid="stFileUploaderDropzone"] button { background:#e2f5ef !important; color:#155b59 !important; }
    [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] * {
      color:#49696a !important; -webkit-text-fill-color:#49696a !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] *,
    .settings-title,.settings-section-label,.section-title,
    .collection-title,.collection-camera,.upload-panel-title {
      color:#17383b !important; -webkit-text-fill-color:#17383b !important;
    }
    </style>
    """

    dark_css = """
    <style>
    :root { --ink:#eff8f6; --muted:#b8cecb; --accent:#75dfcf; --accent-2:#9aaaff; }
    [data-testid="stApp"],[data-testid="stAppViewContainer"],
    [data-testid="stMain"],[data-testid="stMainBlockContainer"] {
      background:transparent !important; color:var(--ink) !important;
    }
    [data-testid="stApp"]::before {
      background:
        radial-gradient(60% 55% at 12% 8%,rgba(22,133,116,.48),transparent 70%),
        radial-gradient(55% 50% at 92% 10%,rgba(70,91,177,.43),transparent 70%),
        radial-gradient(60% 55% at 85% 95%,rgba(116,73,157,.38),transparent 70%),
        radial-gradient(50% 45% at 8% 92%,rgba(145,91,70,.22),transparent 70%),
        linear-gradient(135deg,#0d1b23 0%,#142832 55%,#1b2031 100%) !important;
    }

    /* Readable text, excluding icons and SVGs */
    [data-testid="stMarkdownContainer"],[data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,[data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"],[data-testid="stExpander"] summary,
    [data-testid="stPopover"],[data-testid="stNumberInput"] label,
    [data-testid="stTextInput"] label,[data-testid="stSelectbox"] label,
    [data-testid="stMultiSelect"] label,[data-testid="stToggle"] label,
    [data-testid="stCheckbox"] label,.settings-card,.camera-detail-card,
    .collection-section,.collection-stop,.app-brand,.recommend,
    .camera-action-card,.chart-tip,.collection-example {
      color:#eff8f6 !important; -webkit-text-fill-color:#eff8f6 !important;
    }
    [data-testid="stCaptionContainer"],.app-subtitle,.upload-panel-subtitle,
    .upload-hint,.settings-subtitle,.collection-subtitle {
      color:#b8cecb !important; -webkit-text-fill-color:#b8cecb !important;
    }

    [data-testid="stMetric"],[data-testid="stExpander"],
    .settings-card,.camera-detail-card,.collection-section,
    .collection-stop,.app-brand,.recommend,.camera-action-card,
    .chart-tip,.collection-example {
      background:linear-gradient(145deg,rgba(35,65,75,.86),rgba(19,39,49,.78)) !important;
      border:0 !important;
      box-shadow:0 16px 40px rgba(0,0,0,.20),inset 0 1px 0 rgba(255,255,255,.055) !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details {
      background:transparent !important; border:0 !important;
      color:#eff8f6 !important; -webkit-text-fill-color:#eff8f6 !important;
    }
    [data-testid="stExpander"] summary:hover {
      background:rgba(117,223,207,.10) !important;
      color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;
    }

    /* Single dark dropzone; uploader wrapper stays transparent */
    [data-testid="stFileUploader"],[data-testid="stFileUploader"] > section {
      background:transparent !important; border:0 !important; box-shadow:none !important;
    }
    [data-testid="stFileUploaderDropzone"] {
      background:rgba(15,32,41,.66) !important; border:0 !important;
      border-radius:20px !important; box-shadow:none !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
      background:#d8f4ed !important; color:#164e4d !important;
      border:0 !important;
    }
    [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stFileUploaderDropzone"] button span {
      color:#164e4d !important; fill:#164e4d !important;
      -webkit-text-fill-color:#164e4d !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] * {
      color:#c6ddda !important; -webkit-text-fill-color:#c6ddda !important;
    }

    /* Explicit dark hover/focus states to prevent white flashes */
    .stButton > button,[data-testid="stDownloadButton"] button,
    [data-testid="stPopover"] > button,[data-testid="stFormSubmitButton"] button,
    [data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-primary"] {
      background:#274653 !important; color:#eff8f6 !important;
      border:0 !important; border-radius:13px !important;
      box-shadow:0 6px 18px rgba(0,0,0,.18) !important;
    }
    .stButton > button:hover,[data-testid="stDownloadButton"] button:hover,
    [data-testid="stPopover"] > button:hover,
    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {
      background:#356273 !important; color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
      box-shadow:0 8px 22px rgba(0,0,0,.24) !important;
    }
    .stButton > button:focus-visible,[data-testid="stDownloadButton"] button:focus-visible,
    [data-testid="stPopover"] > button:focus-visible {
      outline:2px solid #75dfcf !important; outline-offset:2px !important;
    }
    .stButton > button span:not(.material-icons):not(.material-symbols-rounded),
    [data-testid="stDownloadButton"] button span:not(.material-icons):not(.material-symbols-rounded),
    [data-testid="stPopover"] > button span:not(.material-icons):not(.material-symbols-rounded) {
      color:inherit !important; -webkit-text-fill-color:currentColor !important;
    }
    .stButton > button svg,[data-testid="stPopover"] > button svg {
      fill:currentColor !important; color:currentColor !important;
    }
    .stButton > button[kind="primary"],[data-testid="stBaseButton-primary"] {
      background:linear-gradient(135deg,#137f78,#596ed0) !important;
    }
    .stButton > button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover {
      background:linear-gradient(135deg,#19998f,#6b7fe0) !important;
    }

    /* Popover menu surfaces and their content */
    [data-baseweb="popover"],[data-baseweb="popover"] > div,
    [data-testid="stPopover"] [data-baseweb="popover"] {
      background:#1b3540 !important; color:#eff8f6 !important;
      border:0 !important; border-radius:18px !important;
    }
    [data-baseweb="popover"] [role="option"],
    [data-baseweb="popover"] [role="menuitem"] {
      color:#eff8f6 !important;
    }
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [role="menuitem"]:hover {
      background:#315765 !important; color:#ffffff !important;
    }

    [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,[data-baseweb="select"] > div {
      background:rgba(10,24,31,.82) !important; color:#eff8f6 !important;
      border-color:rgba(180,220,215,.16) !important;
      -webkit-text-fill-color:#eff8f6 !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
      color:#91aaa9 !important; -webkit-text-fill-color:#91aaa9 !important;
    }
    [data-testid="stAlert"] {
      background:rgba(25,48,58,.88) !important; color:#eff8f6 !important;
      border:0 !important; border-radius:16px !important;
    }
    .collection-info summary {
      background:rgba(37,63,73,.90) !important; color:#eff8f6 !important; border:0 !important;
    }
    .collection-info-pop {
      background:rgba(20,38,47,.98) !important; color:#eff8f6 !important;
      border:0 !important; border-radius:16px !important;
    }
    </style>
    """

    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.markdown(common_css, unsafe_allow_html=True)
    if dark_mode:
        st.markdown(dark_css, unsafe_allow_html=True)
    else:
        st.markdown(light_css, unsafe_allow_html=True)


    mode_overrides = """
    [data-testid="stApp"] button:hover, [data-testid="stApp"] [role="button"]:hover,
    [data-testid="stApp"] [data-baseweb="select"] > div:hover,
    [data-testid="stApp"] [data-testid="stExpander"] summary:hover {
      background-color:#294b57 !important; color:#f2fbf9 !important;
      border-color:rgba(139,220,207,.34) !important;
      -webkit-text-fill-color:#f2fbf9 !important;
    }
    [data-testid="stApp"] button:hover *, [data-testid="stApp"] [role="button"]:hover *,
    [data-testid="stApp"] [data-testid="stExpander"] summary:hover * {
      color:#f2fbf9 !important; -webkit-text-fill-color:#f2fbf9 !important;
    }
    [data-testid="stApp"] button[kind="primary"]:hover,
    [data-testid="stApp"] [data-testid="stBaseButton-primary"]:hover {
      background:linear-gradient(135deg,#19998f,#6b7fe0) !important;
    }
    [data-testid="stFileUploaderDropzone"], [data-testid="stFileUploaderDropzone"] * {
      color:#eaf6f3 !important; -webkit-text-fill-color:#eaf6f3 !important;
    }
    [data-testid="stFileUploaderDropzone"] { background:rgba(18,39,48,.82) !important; }
    [data-testid="stFileUploaderDropzone"]:hover { background:rgba(39,75,86,.92) !important; }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] *,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] * {
      color:#edf8f5 !important; -webkit-text-fill-color:#edf8f5 !important;
    }
    """ if dark_mode else """
    [data-testid="stFileUploaderDropzone"] {
      background:rgba(255,255,255,.52) !important; color:#17383b !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
      color:#17383b !important; -webkit-text-fill-color:#17383b !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover { background:rgba(220,246,239,.82) !important; }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {
      color:#17383b !important; -webkit-text-fill-color:#17383b !important;
    }
    """

    final_overrides = """
    <style>
    [data-testid="stFileUploader"] {
      display:block !important; background:transparent !important;
      border:0 !important; padding:0 !important; box-shadow:none !important;
    }
    [data-testid="stFileUploader"] > section {
      display:block !important; background:transparent !important;
      border:0 !important; padding:0 !important; box-shadow:none !important;
    }
    [data-testid="stFileUploaderDropzone"] {
      display:revert !important; box-sizing:border-box !important;
      min-height:76px !important; padding:14px 16px !important;
      border:0 !important; outline:0 !important;
      border-radius:22px !important; box-shadow:none !important; overflow:hidden !important;
    }
    [data-testid="stFileUploaderDropzone"] > div {
      display:revert !important; flex:initial !important; min-width:0 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
      display:inline-block !important; max-width:100% !important;
      line-height:1.5 !important; white-space:normal !important;
    }
    span[data-testid="stIconMaterial"], [data-testid="stIconMaterial"],
    .material-icons, .material-icons-outlined,
    .material-symbols-rounded, .material-symbols-outlined {
      font-family:"Material Symbols Rounded","Material Icons" !important;
      font-feature-settings:"liga" !important; font-weight:normal !important;
      letter-spacing:normal !important; text-transform:none !important;
      white-space:nowrap !important; line-height:1 !important;
    }
    button span[data-testid="stIconMaterial"],
    [role="button"] span[data-testid="stIconMaterial"] {
      display:inline-flex !important; align-items:center !important;
      justify-content:center !important; flex:0 0 1.25em !important;
      width:1.25em !important; height:1.25em !important; overflow:hidden !important;
    }
    __MODE_OVERRIDES__
    [data-testid="stPopover"] > button, [data-testid="stToolbar"] button,
    button[aria-label] {
      display:inline-flex !important; align-items:center !important;
      justify-content:center !important; gap:.45rem !important;
    }
    [data-testid="stApp"]::before {
      background-size:240% 240%,240% 240%,240% 240%,240% 240%,180% 180% !important;
      animation:auroraFlow 17s ease-in-out infinite alternate !important;
      will-change:background-position;
    }
    @keyframes auroraFlow {
      0% { background-position:0% 12%,100% 0%,90% 100%,0% 88%,0% 0%; }
      35% { background-position:28% 42%,70% 18%,62% 72%,32% 60%,40% 35%; }
      70% { background-position:12% 82%,88% 56%,100% 22%,10% 20%,80% 70%; }
      100% { background-position:65% 15%,18% 78%,35% 8%,75% 92%,100% 100%; }
    }
    @media (prefers-reduced-motion:reduce) {
      [data-testid="stApp"]::before { animation:none !important; }
    }
    </style>
    """.replace("__MODE_OVERRIDES__", mode_overrides)
    st.markdown(final_overrides, unsafe_allow_html=True)


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
