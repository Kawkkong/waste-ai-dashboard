import streamlit as st


def inject_theme() -> None:
    """Inject Client-Side 0ms Theme & Drawer Engine with 100% Dark Mode coverage."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

    /* ============ 1) DARK MODE VARIABLES (ค่าเริ่มต้น) ============ */
    :root,
    html[data-wv-theme="dark"] {
        --ink: #f8fafc;
        --ink-soft: #cbd5e1;
        --muted: #94a3b8;
        --accent: #00f5d4;
        --accent-2: #6366f1;
        --accent-3: #a855f7;
        --accent-glow: rgba(0, 245, 212, 0.25);
        --bg-solid: #040914;
        --bg-mesh:
            radial-gradient(45% 45% at 15% 12%, rgba(0, 245, 212, 0.20) 0%, transparent 70%),
            radial-gradient(45% 45% at 86% 16%, rgba(99, 102, 241, 0.24) 0%, transparent 70%),
            radial-gradient(50% 50% at 78% 88%, rgba(168, 85, 247, 0.18) 0%, transparent 70%),
            linear-gradient(135deg, #030712 0%, #071022 50%, #090d1c 100%);
        --grid-line: rgba(0, 245, 212, 0.045);
        --liquid-bg: linear-gradient(135deg, rgba(15, 27, 46, 0.62) 0%, rgba(9, 17, 32, 0.42) 100%);
        --liquid-bg-hover: linear-gradient(135deg, rgba(22, 39, 66, 0.75) 0%, rgba(14, 25, 45, 0.55) 100%);
        --liquid-subtle: rgba(12, 21, 38, 0.60);
        --liquid-border: rgba(148, 163, 184, 0.20);
        --liquid-border-hover: rgba(0, 245, 212, 0.58);
        --liquid-rim: inset 0 1px 1px rgba(255, 255, 255, 0.16), inset 0 -1px 1px rgba(0, 245, 212, 0.08);
        --shadow-glass: 0 12px 32px -6px rgba(0, 0, 0, 0.55);
        --shadow-hover: 0 18px 40px -6px rgba(0, 245, 212, 0.20), 0 8px 24px -4px rgba(0, 0, 0, 0.65);
        --btn-bg: linear-gradient(135deg, rgba(28, 44, 70, 0.72) 0%, rgba(15, 25, 44, 0.55) 100%);
        --btn-bg-hover: linear-gradient(135deg, rgba(0, 245, 212, 0.24) 0%, rgba(99, 102, 241, 0.24) 100%);
        --input-bg: #0b1528;
        --input-bg-hover: #11203a;
        --popover-bg: #0f1c30;
        --title-gradient: linear-gradient(90deg, #ffffff 0%, #5eead4 48%, #a5b4fc 100%);
        --spring: cubic-bezier(0.22, 1, 0.36, 1);
        --radius-xl: 24px;
        --radius-lg: 20px;
        --radius-md: 15px;
        --radius-sm: 11px;
    }

    /* ============ 2) LIGHT MODE VARIABLES (สลับทันทีใน 0ms ไม่ต้อง Rerun) ============ */
    html[data-wv-theme="light"] {
        --ink: #0f172a;
        --ink-soft: #334155;
        --muted: #64748b;
        --accent: #0d9488;
        --accent-2: #4f46e5;
        --accent-3: #9333ea;
        --accent-glow: rgba(13, 148, 136, 0.20);
        --bg-solid: #eef6ff;
        --bg-mesh:
            radial-gradient(45% 45% at 14% 12%, rgba(45, 212, 191, 0.42) 0%, transparent 70%),
            radial-gradient(45% 45% at 86% 15%, rgba(129, 140, 248, 0.38) 0%, transparent 70%),
            radial-gradient(50% 50% at 80% 88%, rgba(192, 132, 252, 0.32) 0%, transparent 70%),
            linear-gradient(135deg, #e0f2fe 0%, #eef2ff 50%, #f3e8ff 100%);
        --grid-line: rgba(13, 148, 136, 0.055);
        --liquid-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.65) 0%, rgba(255, 255, 255, 0.38) 100%);
        --liquid-bg-hover: linear-gradient(135deg, rgba(255, 255, 255, 0.82) 0%, rgba(255, 255, 255, 0.55) 100%);
        --liquid-subtle: rgba(255, 255, 255, 0.55);
        --liquid-border: rgba(255, 255, 255, 0.85);
        --liquid-border-hover: rgba(13, 148, 136, 0.55);
        --liquid-rim: inset 0 1.5px 1px rgba(255, 255, 255, 0.95), inset 0 -1px 1px rgba(13, 148, 136, 0.08);
        --shadow-glass: 0 10px 28px -6px rgba(15, 23, 42, 0.07);
        --shadow-hover: 0 16px 34px -6px rgba(13, 148, 136, 0.16), 0 6px 16px -4px rgba(79, 70, 229, 0.10);
        --btn-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.78) 0%, rgba(255, 255, 255, 0.50) 100%);
        --btn-bg-hover: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(204, 251, 241, 0.60) 100%);
        --input-bg: #ffffff;
        --input-bg-hover: #f8fafc;
        --popover-bg: #ffffff;
        --title-gradient: linear-gradient(90deg, #0f172a 0%, #0d9488 50%, #4f46e5 100%);
    }

    /* ซ่อนแถบ預設ของ Streamlit */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        display: none !important;
    }
    #MainMenu, footer {
        visibility: hidden !important;
    }

    /* พื้นหลังหลักของแอป */
    html, body, .stApp,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background-color: var(--bg-solid) !important;
        background-image: var(--bg-mesh) !important;
        background-attachment: fixed !important;
        color: var(--ink) !important;
        transition: background-color 0.25s ease, color 0.2s ease !important;
    }

    .stApp::after {
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        background-image:
            linear-gradient(to right, var(--grid-line) 1px, transparent 1px),
            linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
        background-size: 36px 36px;
        mask-image: radial-gradient(circle at 50% 35%, black 30%, transparent 85%);
        -webkit-mask-image: radial-gradient(circle at 50% 35%, black 30%, transparent 85%);
        pointer-events: none;
    }

    .block-container {
        position: relative;
        z-index: 1;
        max-width: 1240px !important;
        padding-top: 1.15rem !important;
        padding-bottom: 3rem !important;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }

    html, body, button, input, textarea, select,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMetric"],
    [data-testid="stWidgetLabel"],
    [data-testid="stPopover"] {
        font-family: 'Prompt', 'Noto Sans Thai', sans-serif !important;
    }

    /* รักษาไอคอนของ Streamlit */
    span[data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"],
    .material-icons,
    .material-icons-outlined,
    .material-symbols-rounded,
    .material-symbols-outlined,
    [data-testid="stExpander"] summary svg {
        font-family: "Material Symbols Rounded", "Material Icons" !important;
        font-feature-settings: "liga" !important;
        font-weight: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        direction: ltr !important;
        line-height: 1 !important;
        color: var(--ink) !important;
        fill: var(--ink) !important;
    }

    h1, h2, h3, h4,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span:not([data-testid="stIconMaterial"]) {
        color: var(--ink) !important;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {
        color: var(--muted) !important;
    }

    /* ============ 3) Smooth Settings Drawer (ควบคุมด้วย html[data-wv-drawer] ทันที 0ms) ============ */
    .st-key-settings_drawer {
        overflow: hidden !important;
        border-radius: var(--radius-xl) !important;
        background: var(--liquid-bg) !important;
        -webkit-backdrop-filter: blur(26px) saturate(190%) !important;
        backdrop-filter: blur(26px) saturate(190%) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim) !important;
        transition:
            max-height 0.48s var(--spring),
            opacity 0.32s ease,
            transform 0.45s var(--spring),
            padding 0.42s var(--spring),
            margin 0.42s var(--spring),
            border-width 0.25s ease !important;
    }

    html:not([data-wv-drawer="open"]) .st-key-settings_drawer {
        max-height: 0px !important;
        opacity: 0 !important;
        transform: translateY(-14px) scale(0.985) !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        border: 0px solid transparent !important;
        pointer-events: none !important;
    }

    html[data-wv-drawer="open"] .st-key-settings_drawer {
        max-height: 920px !important;
        opacity: 1 !important;
        transform: translateY(0) scale(1) !important;
        padding: 20px 22px !important;
        margin: 6px 0 18px 0 !important;
        border: 1px solid var(--liquid-border-hover) !important;
        pointer-events: auto !important;
    }

    /* ============ 4) Top Header Bar & Instant Client-Side Action Buttons ============ */
    .wv-topbar {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        margin-bottom: 6px;
    }

    .app-brand {
        flex: 1 1 380px;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        min-height: 72px;
        padding: 12px 20px !important;
        border: 1px solid var(--liquid-border) !important;
        border-radius: var(--radius-xl) !important;
        background: var(--liquid-bg) !important;
        -webkit-backdrop-filter: blur(22px) saturate(180%) !important;
        backdrop-filter: blur(22px) saturate(180%) !important;
        box-shadow: var(--shadow-glass), var(--liquid-rim) !important;
        transition: all 0.3s var(--spring) !important;
    }

    .app-brand-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .app-brand-icon {
        width: 48px !important;
        height: 48px !important;
        flex: 0 0 48px;
        border-radius: 15px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 23px;
        color: #fff;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 60%, var(--accent-3) 100%) !important;
        box-shadow: 0 8px 22px var(--accent-glow), inset 0 1px 2px rgba(255, 255, 255, 0.55) !important;
    }

    .app-title {
        font-size: 21px !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        background: var(--title-gradient);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .app-subtitle {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 2px;
        color: var(--muted) !important;
        font-size: 12px !important;
        font-family: 'JetBrains Mono', 'Prompt', monospace !important;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 10px #10b981;
        display: inline-block;
        animation: pulseGlow 2s infinite;
    }

    @keyframes pulseGlow {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.3); opacity: 0.65; }
    }

    .wv-actions {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: nowrap;
    }

    .wv-btn {
        position: relative;
        overflow: hidden;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 7px;
        min-height: 46px;
        padding: 0 18px;
        border: 1px solid var(--liquid-border);
        border-radius: 15px;
        background: var(--btn-bg);
        -webkit-backdrop-filter: blur(18px) saturate(170%);
        backdrop-filter: blur(18px) saturate(170%);
        color: var(--ink) !important;
        font-family: 'Prompt', 'Noto Sans Thai', sans-serif;
        font-size: 13.5px;
        font-weight: 600;
        cursor: pointer;
        user-select: none;
        white-space: nowrap;
        box-shadow: var(--shadow-glass), var(--liquid-rim);
        transition: transform 0.25s var(--spring), box-shadow 0.25s var(--spring), border-color 0.2s ease, background 0.2s ease;
    }

    .wv-btn:hover {
        transform: translateY(-2.5px) scale(1.02);
        background: var(--btn-bg-hover);
        border-color: var(--liquid-border-hover);
        color: var(--accent) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim);
    }

    .wv-btn:active {
        transform: translateY(0) scale(0.96);
    }

    /* สลับข้อความบนปุ่มตามสถานะทันทีด้วย CSS */
    html[data-wv-theme="dark"] .wv-theme-light-txt { display: inline; }
    html[data-wv-theme="dark"] .wv-theme-dark-txt { display: none; }
    html[data-wv-theme="light"] .wv-theme-light-txt { display: none; }
    html[data-wv-theme="light"] .wv-theme-dark-txt { display: inline; }

    html[data-wv-drawer="open"] .wv-set-open-txt { display: none; }
    html[data-wv-drawer="open"] .wv-set-close-txt { display: inline; color: var(--accent); }
    html:not([data-wv-drawer="open"]) .wv-set-open-txt { display: inline; }
    html:not([data-wv-drawer="open"]) .wv-set-close-txt { display: none; }

    /* ปุ่ม Help แบบ Details/Summary ที่ไม่ต้อง Rerun */
    .wv-help-wrap {
        position: relative;
    }
    .wv-help-wrap summary {
        list-style: none;
    }
    .wv-help-wrap summary::-webkit-details-marker {
        display: none;
    }
    .wv-help-pop {
        position: absolute;
        right: 0;
        top: calc(100% + 10px);
        z-index: 9999;
        width: min(340px, 85vw);
        padding: 16px 18px;
        border: 1px solid var(--liquid-border-hover);
        border-radius: 18px;
        background: var(--popover-bg);
        -webkit-backdrop-filter: blur(24px);
        backdrop-filter: blur(24px);
        box-shadow: var(--shadow-hover);
        color: var(--ink) !important;
        font-size: 12.5px;
        line-height: 1.65;
        animation: hudFadeIn 0.25s var(--spring) both;
    }

    @keyframes hudFadeIn {
        from { opacity: 0; transform: translateY(-6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ============ 5) ครอบคลุมทุก Input / Selectbox / NumberInput / Dropdown ในโหมดมืด 100% (ไม่มีพื้นขาวตัวหนังสือขาวอีกต่อไป) ============ */
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label,
    [data-testid="stWidgetLabel"] p {
        color: var(--ink-soft) !important;
        font-size: 12.5px !important;
        font-weight: 500 !important;
    }

    /* กล่องครอบ Input และ Selectbox ของ BaseWeb ทุกชั้น */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-testid="stNumberInputContainer"],
    div[data-testid="stNumberInput"] > div > div,
    div[data-baseweb="select"] > div {
        background-color: var(--input-bg) !important;
        background: var(--input-bg) !important;
        color: var(--ink) !important;
        border: 1px solid var(--liquid-border) !important;
        border-radius: var(--radius-sm) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        background-color: transparent !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
        caret-color: var(--accent) !important;
    }

    /* ปุ่ม + / - ใน NumberInput */
    div[data-testid="stNumberInput"] button,
    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"] {
        background-color: var(--liquid-subtle) !important;
        background: var(--liquid-subtle) !important;
        color: var(--ink) !important;
        border: 0 !important;
    }
    div[data-testid="stNumberInput"] button:hover {
        background: var(--accent-glow) !important;
        color: var(--accent) !important;
    }
    div[data-testid="stNumberInput"] button svg,
    div[data-baseweb="select"] svg {
        fill: var(--ink) !important;
        color: var(--ink) !important;
    }

    /* เมนู Dropdown (Selectbox list) และ Popover เวลาคลิกเปิด */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    ul[data-testid="stSelectboxVirtualDropdown"],
    ul[role="listbox"],
    li[role="option"],
    [data-testid="stPopoverBody"] {
        background-color: var(--popover-bg) !important;
        background: var(--popover-bg) !important;
        color: var(--ink) !important;
        border-color: var(--liquid-border) !important;
    }

    li[role="option"] *,
    div[data-baseweb="menu"] * {
        color: var(--ink) !important;
    }

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: var(--accent-glow) !important;
        background: var(--accent-glow) !important;
        color: var(--accent) !important;
    }

    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] p,
    [data-testid="stCheckbox"] span {
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
    }

    /* ============ 6) File Uploader (แก้พื้นขาวในโหมดมืด 100%) ============ */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] > section {
        background: transparent !important;
        border: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        min-height: 82px !important;
        padding: 14px 16px !important;
        border: 1.5px dashed var(--liquid-border-hover) !important;
        border-radius: 16px !important;
        background-color: var(--liquid-subtle) !important;
        background: var(--liquid-subtle) !important;
        color: var(--ink) !important;
        transition: all 0.25s var(--spring) !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        transform: translateY(-2px);
        border-color: var(--accent) !important;
        background: var(--liquid-bg-hover) !important;
        box-shadow: var(--shadow-hover) !important;
    }

    [data-testid="stFileUploaderDropzone"] div,
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] *,
    [data-testid="stFileUploaderFile"] * {
        color: var(--ink-soft) !important;
        -webkit-text-fill-color: var(--ink-soft) !important;
    }

    [data-testid="stFileUploaderDropzone"] svg {
        fill: var(--accent) !important;
        color: var(--accent) !important;
    }

    /* ปุ่ม Browse files ในตัวอัปโหลด */
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] {
        border-radius: 11px !important;
        background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
        color: #ffffff !important;
        border: 0 !important;
        padding: 6px 15px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px var(--accent-glow) !important;
    }

    [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* ============ 7) การ์ด Liquid Glass, Expander & ปุ่ม Streamlit ============ */
    [data-testid="stMetric"],
    [data-testid="stExpander"],
    .collection-section,
    .collection-stop,
    .tech-stat-card {
        border: 1px solid var(--liquid-border) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--liquid-bg) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        box-shadow: var(--shadow-glass), var(--liquid-rim) !important;
        transition:
            transform 0.28s var(--spring),
            box-shadow 0.28s var(--spring),
            border-color 0.22s ease,
            background 0.22s ease !important;
    }

    [data-testid="stMetric"] {
        padding: 14px 16px !important;
        border-radius: var(--radius-md) !important;
    }

    [data-testid="stMetric"]:hover,
    .collection-stop:hover,
    .tech-stat-card:hover {
        transform: translateY(-3px);
        background: var(--liquid-bg-hover) !important;
        border-color: var(--liquid-border-hover) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim) !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted) !important;
        font-size: 11.5px !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
        font-family: 'JetBrains Mono', 'Prompt', sans-serif !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stExpander"] {
        overflow: hidden !important;
        margin: 6px 0 14px !important;
    }

    [data-testid="stExpander"] details,
    [data-testid="stExpanderDetails"] {
        border: 0 !important;
        background: transparent !important;
        color: var(--ink) !important;
    }

    [data-testid="stExpander"] summary {
        display: flex !important;
        align-items: center !important;
        gap: 0.55rem !important;
        min-height: 48px !important;
        padding: 10px 18px !important;
        background: transparent !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
        transition: background 0.22s ease, padding-left 0.25s var(--spring) !important;
    }

    [data-testid="stExpander"] summary:hover {
        background: var(--accent-glow) !important;
        padding-left: 22px !important;
    }

    [data-testid="stExpander"] summary p {
        margin: 0 !important;
        color: var(--ink) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    [data-testid="stExpander"] > div,
    [data-testid="stExpanderDetails"] {
        padding: 6px 16px 16px !important;
    }

    /* ปุ่มของ Streamlit */
    .stButton > button,
    [data-testid="stDownloadButton"] > button,
    [data-testid="stPopover"] > button {
        border: 1px solid var(--liquid-border) !important;
        border-radius: 14px !important;
        background: var(--btn-bg) !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        min-height: 42px !important;
        width: 100%;
        box-shadow: var(--shadow-glass), var(--liquid-rim) !important;
        transition: all 0.25s var(--spring) !important;
    }

    .stButton > button *,
    [data-testid="stPopover"] > button * {
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
    }

    .stButton > button:hover,
    [data-testid="stPopover"] > button:hover {
        transform: translateY(-2px) !important;
        background: var(--btn-bg-hover) !important;
        border-color: var(--liquid-border-hover) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim) !important;
    }

    .stButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"] {
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #0d9488 0%, #4f46e5 55%, #9333ea 100%) !important;
        box-shadow: 0 10px 24px -4px var(--accent-glow) !important;
    }

    .stButton > button[kind="primary"] *,
    [data-testid="stBaseButton-primary"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* ============ 8) Custom Tech HUD & Collection Route ============ */
    .tech-stat-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin: 6px 0 14px;
    }
    .tech-stat-card {
        padding: 13px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .tech-stat-label { font-size: 11.5px; color: var(--muted) !important; font-weight: 500; }
    .tech-stat-val { font-size: 20px; font-weight: 700; color: var(--ink) !important; font-family: 'JetBrains Mono', 'Prompt', sans-serif; }

    .upload-camera-label {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 4px 0;
        color: var(--ink) !important;
        font-size: 13.5px;
        font-weight: 600;
    }
    .upload-hint { color: var(--muted) !important; font-size: 11.5px; margin: 0 0 8px; }

    .camera-detail-card {
        margin: 4px 0 12px;
        padding: 12px 15px;
        border: 1px solid var(--liquid-border);
        border-radius: var(--radius-md);
        background: var(--liquid-subtle);
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }
    .camera-status-pill {
        display: inline-flex;
        align-items: center;
        padding: 5px 13px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .camera-action-card { flex: 1 1 200px; display: flex; align-items: center; gap: 8px; font-size: 12.5px; }
    .action-label { font-weight: 700; color: var(--accent) !important; white-space: nowrap; }
    .action-text { color: var(--ink) !important; }
    .camera-image-title { display: block; margin: 4px 0 6px; font-size: 12.5px !important; font-weight: 600 !important; color: var(--ink) !important; }
    .chart-tip { margin: 0 0 8px; padding: 7px 12px; border-radius: 10px; border: 1px solid var(--liquid-border); background: var(--liquid-subtle); color: var(--ink-soft) !important; font-size: 11.5px; }
    .history-title { margin: 14px 0 8px; font-size: 13.5px; font-weight: 700; color: var(--ink) !important; }
    .settings-title { font-size: 17px; font-weight: 700; color: var(--ink) !important; }
    .settings-subtitle { margin-top: 2px; color: var(--muted) !important; font-size: 12px; margin-bottom: 10px; }
    .settings-section-label { margin: 12px 0 6px; color: var(--accent) !important; font-size: 12.5px; font-weight: 600; }

    .collection-section { margin-top: 14px; padding: 20px 22px; }
    .collection-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; margin-bottom: 14px; }
    .collection-title { font-size: 18px; font-weight: 700; color: var(--ink) !important; margin-bottom: 2px; }
    .collection-subtitle { color: var(--muted) !important; font-size: 12px; }
    .collection-road {
        position: relative;
        height: 116px;
        margin: 0 0 16px;
        border-radius: 18px;
        background: linear-gradient(135deg, #111c33 0%, #091020 100%) !important;
        border: 1px solid var(--liquid-border);
        overflow: hidden;
        box-shadow: inset 0 4px 16px rgba(0, 0, 0, 0.45);
    }
    .collection-lane {
        position: absolute;
        left: 4%;
        right: 4%;
        top: 54%;
        height: 3px;
        transform: translateY(-50%);
        background: repeating-linear-gradient(90deg, rgba(0, 245, 212, 0.65) 0 36px, transparent 36px 64px);
    }
    .collection-checkpoints {
        position: absolute;
        left: 6%;
        right: 8%;
        top: 32px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        z-index: 4;
    }
    .collection-checkpoint-wrap { min-width: 40px; text-align: center; }
    .collection-checkpoint {
        width: 30px;
        height: 30px;
        margin: 0 auto;
        border: 2.5px solid #ffffff;
        border-radius: 50%;
        display: grid;
        place-items: center;
        box-shadow: 0 0 14px rgba(0, 245, 212, 0.45);
        color: #ffffff !important;
        font-size: 11px;
        font-weight: 700;
    }
    .collection-checkpoint-label { margin-top: 6px; color: #f8fafc !important; font-size: 10.5px; font-weight: 600; white-space: nowrap; }
    .collection-truck {
        position: absolute;
        left: 4%;
        top: 56px;
        z-index: 6;
        font-size: 28px;
        transform: scaleX(-1);
        animation: collectionDriveOneWay 9s linear infinite;
        pointer-events: none;
    }
    @keyframes collectionDriveOneWay {
        0%   { left: 4%; opacity: 0; }
        8%   { opacity: 1; }
        92%  { opacity: 1; }
        100% { left: 93%; opacity: 0; }
    }
    .collection-road-arrow { position: absolute; right: 3%; top: 46px; color: var(--accent) !important; font-size: 18px; z-index: 5; }
    .collection-road-label { position: absolute; left: 50%; bottom: 8px; transform: translateX(-50%); color: rgba(255,255,255,0.75) !important; font-size: 10px; font-family: 'JetBrains Mono', monospace; }
    .collection-stops { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
    .collection-stop { position: relative; padding: 15px; }
    .collection-rank {
        position: absolute;
        top: 12px;
        right: 12px;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        color: #fff !important;
        font-weight: 700;
        font-size: 12px;
    }
    .collection-camera { font-size: 13.5px; font-weight: 700; color: var(--ink) !important; padding-right: 34px; }
    .collection-war { font-size: 19px; font-weight: 700; color: var(--accent) !important; margin-top: 4px; font-family: 'JetBrains Mono', sans-serif; }
    .collection-level { font-size: 11.5px; color: var(--ink-soft) !important; margin-top: 2px; }
    .collection-detail { margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--liquid-border); font-size: 11px; line-height: 1.55; color: var(--muted) !important; }
    .collection-note { margin-top: 10px; text-align: center; color: var(--muted) !important; font-size: 11px; }
    .collection-empty { margin-top: 10px; padding: 18px; border-radius: 14px; border: 1px dashed var(--liquid-border); background: var(--liquid-subtle); color: var(--muted) !important; text-align: center; font-size: 12.5px; }

    /* กราฟ Plotly ปรับสีตัวอักษรตามโหมดมืด/สว่างอัตโนมัติ */
    .js-plotly-plot .plotly .main-svg { background: transparent !important; }
    .js-plotly-plot .plotly .main-svg .bg { fill: transparent !important; }
    .js-plotly-plot .plotly text { fill: var(--ink) !important; }
    [data-testid="stPlotlyChart"] {
        padding: 10px;
        border-radius: var(--radius-md);
        border: 1px solid var(--liquid-border);
        background: var(--liquid-subtle);
    }

    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--liquid-border) !important;
        background: var(--liquid-bg) !important;
        color: var(--ink) !important;
    }
    [data-testid="stAlert"] * {
        color: var(--ink) !important;
    }

    /* ============ 9) เก็บตกทุก element ที่ยังเป็นพื้นขาวในโหมดมืด ============ */
    html[data-wv-theme="dark"] { color-scheme: dark; }
    html[data-wv-theme="light"] { color-scheme: light; }

    /* Scrollbar */
    * { scrollbar-color: var(--muted) transparent; }

    /* inline code / code block ใน markdown */
    [data-testid="stMarkdownContainer"] code,
    [data-testid="stCode"],
    [data-testid="stCode"] pre,
    pre {
        background-color: var(--liquid-subtle) !important;
        color: var(--accent) !important;
        border-radius: 8px !important;
    }

    /* Tooltip (ไอคอน ? ของ widget) */
    [data-testid="stTooltipContent"],
    div[data-baseweb="tooltip"],
    div[data-baseweb="tooltip"] > div {
        background-color: var(--popover-bg) !important;
        color: var(--ink) !important;
        border: 1px solid var(--liquid-border) !important;
    }

    /* Popover (ปุ่ม ℹ️) และเนื้อหาข้างใน */
    [data-testid="stPopoverBody"] * {
        color: var(--ink) !important;
    }
    [data-testid="stPopoverBody"] {
        border: 1px solid var(--liquid-border-hover) !important;
        box-shadow: var(--shadow-hover) !important;
    }

    /* Selectbox: รายการใน dropdown + ช่องค้นหา */
    ul[data-testid="stSelectboxVirtualDropdown"] li,
    div[data-baseweb="menu"] li {
        background-color: var(--popover-bg) !important;
    }
    div[data-baseweb="select"] [data-baseweb="tag"] {
        background-color: var(--accent-glow) !important;
    }

    /* Checkbox กล่องติ๊ก */
    [data-testid="stCheckbox"] label > span:first-child:not([data-testid]) {
        background-color: var(--input-bg) !important;
        border-color: var(--liquid-border-hover) !important;
    }

    /* File uploader: รายการไฟล์ที่อัปโหลดแล้ว + ปุ่มลบ */
    [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploaderFileData"],
    [data-testid="stFileUploader"] section + div,
    [data-testid="stFileUploader"] [data-testid="stFileChips"] {
        background-color: var(--liquid-subtle) !important;
        color: var(--ink) !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
        color: var(--ink-soft) !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"] button {
        background: transparent !important;
        box-shadow: none !important;
        border: 0 !important;
        min-height: 0 !important;
    }

    /* Alert (st.info / st.error / st.success) ให้ใช้พื้นกระจกเหมือนการ์ดอื่น */
    [data-testid="stAlert"],
    [data-testid="stAlertContainer"] {
        background-color: transparent !important;
        background: var(--liquid-bg) !important;
        color: var(--ink) !important;
    }

    /* Expander: ส่วน header/ตัวห่อด้านนอกบางเวอร์ชันมีพื้นหลังของตัวเอง */
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] > div {
        background-color: transparent !important;
    }

    /* Plotly: hover label / modebar / ข้อความ annotation */
    .js-plotly-plot .hoverlayer .hovertext path {
        fill: var(--popover-bg) !important;
        stroke: var(--liquid-border-hover) !important;
    }
    .js-plotly-plot .hoverlayer .hovertext text,
    .js-plotly-plot .annotation-text {
        fill: var(--ink) !important;
    }
    .js-plotly-plot .modebar { background: transparent !important; }
    .js-plotly-plot .modebar-btn path { fill: var(--muted) !important; }
    .js-plotly-plot .modebar-btn:hover path { fill: var(--accent) !important; }
    .js-plotly-plot .gridlayer path { stroke: var(--liquid-border) !important; }

    /* รูปภาพ (st.image) */
    [data-testid="stImage"] img,
    [data-testid="stImageContainer"] img {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--liquid-border) !important;
    }

    /* Dialog / Modal */
    div[data-testid="stDialog"] div[role="dialog"] {
        background-color: var(--popover-bg) !important;
        color: var(--ink) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # สคริปต์สลับโหมด/ลิ้นชักตั้งค่า
    # หมายเหตุ: st.html จะตัด <script> และ onclick ทิ้งโดยค่าเริ่มต้น ต้องเปิด unsafe_allow_javascript=True
    # และใช้ event delegation (data-wv-action) เพื่อให้ปุ่มทำงานแม้ element ถูกวาดใหม่หลัง rerun
    init_js = """
    <script>
    (function () {
        const root = document.documentElement;

        function safeGet(store, key, fallback) {
            try { return store.getItem(key) || fallback; } catch (e) { return fallback; }
        }
        function safeSet(store, key, value) {
            try { store.setItem(key, value); } catch (e) {}
        }

        function applyTheme(theme) {
            root.setAttribute('data-wv-theme', theme);
            root.style.colorScheme = theme;
            safeSet(localStorage, 'wv_theme', theme);
        }
        function applyDrawer(state) {
            root.setAttribute('data-wv-drawer', state);
            safeSet(sessionStorage, 'wv_drawer', state);
        }

        // ตั้งค่าเริ่มต้น (ทำทุกครั้งที่สคริปต์รัน แต่ไม่ทับค่าที่ผู้ใช้เลือกไว้แล้ว)
        if (!root.hasAttribute('data-wv-theme')) {
            applyTheme(safeGet(localStorage, 'wv_theme', 'dark'));
        }
        if (!root.hasAttribute('data-wv-drawer')) {
            applyDrawer(safeGet(sessionStorage, 'wv_drawer', 'closed'));
        }

        window.wvToggleTheme = function () {
            applyTheme(root.getAttribute('data-wv-theme') === 'light' ? 'dark' : 'light');
        };
        window.wvToggleDrawer = function (forceState) {
            const open = root.getAttribute('data-wv-drawer') === 'open';
            applyDrawer(forceState || (open ? 'closed' : 'open'));
        };

        // ผูก listener ครั้งเดียวทั้งหน้า (กันซ้ำเมื่อ Streamlit rerun)
        if (!window.__wvBound) {
            window.__wvBound = true;
            document.addEventListener('click', function (ev) {
                const el = ev.target.closest && ev.target.closest('[data-wv-action]');
                if (!el) return;
                const action = el.getAttribute('data-wv-action');
                if (action === 'toggle-theme') {
                    window.wvToggleTheme();
                } else if (action === 'toggle-drawer') {
                    window.wvToggleDrawer();
                } else if (action === 'close-drawer') {
                    window.wvToggleDrawer('closed');
                } else if (action === 'dismiss') {
                    const target = el.closest(el.getAttribute('data-wv-target') || '');
                    if (target) target.remove();
                }
            });
        }
    })();
    </script>
    """
    st.html(init_js, unsafe_allow_javascript=True)
