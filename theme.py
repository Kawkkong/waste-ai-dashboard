import streamlit as st


def inject_theme() -> None:
    """Inject High-Tech Ultra-Transparent Liquid Glass UI with Smooth CSS Drawer & Animations."""
    dark_mode = bool(st.session_state.get("dark_mode", True))
    drawer_open = bool(st.session_state.get("show_settings", False))

    if dark_mode:
        tokens = """
        --ink: #f8fafc;
        --ink-soft: #cbd5e1;
        --muted: #94a3b8;
        --accent: #00f5d4;
        --accent-2: #6366f1;
        --accent-3: #a855f7;
        --accent-glow: rgba(0, 245, 212, 0.28);
        --bg-mesh:
            radial-gradient(45% 45% at 15% 12%, rgba(0, 245, 212, 0.22) 0%, transparent 70%),
            radial-gradient(45% 45% at 86% 16%, rgba(99, 102, 241, 0.25) 0%, transparent 70%),
            radial-gradient(50% 50% at 78% 88%, rgba(168, 85, 247, 0.20) 0%, transparent 70%),
            radial-gradient(40% 40% at 18% 85%, rgba(14, 165, 233, 0.18) 0%, transparent 70%),
            linear-gradient(135deg, #030712 0%, #071022 50%, #090d1c 100%);
        --grid-line: rgba(0, 245, 212, 0.045);
        --liquid-bg: linear-gradient(135deg, rgba(15, 28, 48, 0.36) 0%, rgba(10, 18, 34, 0.18) 100%);
        --liquid-bg-hover: linear-gradient(135deg, rgba(22, 40, 68, 0.48) 0%, rgba(14, 26, 48, 0.28) 100%);
        --liquid-subtle: rgba(15, 23, 42, 0.32);
        --liquid-border: rgba(255, 255, 255, 0.16);
        --liquid-border-hover: rgba(0, 245, 212, 0.55);
        --liquid-rim: inset 0 1px 1px rgba(255, 255, 255, 0.22), inset 0 -1px 1px rgba(0, 245, 212, 0.08);
        --shadow-glass: 0 12px 32px -6px rgba(0, 0, 0, 0.55);
        --shadow-hover: 0 18px 40px -6px rgba(0, 245, 212, 0.20), 0 8px 24px -4px rgba(0, 0, 0, 0.65);
        --btn-bg: linear-gradient(135deg, rgba(30, 45, 72, 0.45) 0%, rgba(15, 25, 45, 0.28) 100%);
        --btn-bg-hover: linear-gradient(135deg, rgba(0, 245, 212, 0.22) 0%, rgba(99, 102, 241, 0.22) 100%);
        --input-bg: rgba(8, 15, 28, 0.55);
        --popover-bg: rgba(12, 21, 38, 0.92);
        --title-gradient: linear-gradient(90deg, #ffffff 0%, #5eead4 48%, #a5b4fc 100%);
        """
    else:
        tokens = """
        --ink: #0f172a;
        --ink-soft: #334155;
        --muted: #64748b;
        --accent: #0d9488;
        --accent-2: #4f46e5;
        --accent-3: #9333ea;
        --accent-glow: rgba(13, 148, 136, 0.20);
        --bg-mesh:
            radial-gradient(45% 45% at 14% 12%, rgba(94, 234, 212, 0.55) 0%, transparent 70%),
            radial-gradient(45% 45% at 86% 15%, rgba(165, 180, 252, 0.55) 0%, transparent 70%),
            radial-gradient(50% 50% at 80% 88%, rgba(216, 180, 254, 0.48) 0%, transparent 70%),
            radial-gradient(40% 40% at 15% 86%, rgba(186, 230, 253, 0.52) 0%, transparent 70%),
            linear-gradient(135deg, #ecfeff 0%, #eef2ff 50%, #f5f3ff 100%);
        --grid-line: rgba(13, 148, 136, 0.05);
        --liquid-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.42) 0%, rgba(255, 255, 255, 0.20) 100%);
        --liquid-bg-hover: linear-gradient(135deg, rgba(255, 255, 255, 0.58) 0%, rgba(255, 255, 255, 0.34) 100%);
        --liquid-subtle: rgba(255, 255, 255, 0.34);
        --liquid-border: rgba(255, 255, 255, 0.72);
        --liquid-border-hover: rgba(13, 148, 136, 0.55);
        --liquid-rim: inset 0 1.5px 1px rgba(255, 255, 255, 0.92), inset 0 -1px 1px rgba(13, 148, 136, 0.08);
        --shadow-glass: 0 10px 30px -6px rgba(15, 23, 42, 0.08);
        --shadow-hover: 0 18px 36px -6px rgba(13, 148, 136, 0.18), 0 6px 18px -4px rgba(79, 70, 229, 0.10);
        --btn-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.56) 0%, rgba(255, 255, 255, 0.32) 100%);
        --btn-bg-hover: linear-gradient(135deg, rgba(255, 255, 255, 0.82) 0%, rgba(204, 251, 241, 0.45) 100%);
        --input-bg: rgba(255, 255, 255, 0.52);
        --popover-bg: rgba(255, 255, 255, 0.92);
        --title-gradient: linear-gradient(90deg, #0f172a 0%, #0d9488 50%, #4f46e5 100%);
        """

    drawer_css = (
        """
        div:has(> . st-key-settings_drawer) {
            grid-template-rows: 1fr !important;
            opacity: 1 !important;
            transform: translateY(0) !important;
            margin-bottom: 18px !important;
            pointer-events: auto !important;
        }
        """
        if drawer_open
        else """
        div:has(> .st-key-settings_drawer) {
            grid-template-rows: 0fr !important;
            opacity: 0 !important;
            transform: translateY(-14px) !important;
            margin-bottom: 0px !important;
            pointer-events: none !important;
        }
        """
    ).replace(". st-key-settings_drawer", ".st-key-settings_drawer")

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {{
        {tokens}
        --spring: cubic-bezier(0.22, 1, 0.36, 1);
        --radius-xl: 24px;
        --radius-lg: 20px;
        --radius-md: 15px;
        --radius-sm: 11px;
    }}

    /* ซ่อนแถบ預設ของ Streamlit */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {{
        display: none !important;
    }}
    #MainMenu, footer {{
        visibility: hidden !important;
    }}

    /* พื้นหลัง Cyber Aurora + Tech Grid */
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {{
        background: transparent !important;
        color: var(--ink) !important;
    }}

    [data-testid="stApp"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        z-index: -2;
        background: var(--bg-mesh);
        pointer-events: none;
    }}

    [data-testid="stApp"]::after {{
        content: "";
        position: fixed;
        inset: 0;
        z-index: -1;
        background-image:
            linear-gradient(to right, var(--grid-line) 1px, transparent 1px),
            linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
        background-size: 36px 36px;
        mask-image: radial-gradient(circle at 50% 35%, black 30%, transparent 85%);
        -webkit-mask-image: radial-gradient(circle at 50% 35%, black 30%, transparent 85%);
        pointer-events: none;
    }}

    .block-container {{
        max-width: 1240px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
    }}

    [data-testid="stVerticalBlock"] {{
        gap: 0.7rem;
    }}

    html, body, button, input, textarea, select,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMetric"],
    [data-testid="stWidgetLabel"],
    [data-testid="stPopover"] {{
        font-family: 'Prompt', 'Noto Sans Thai', sans-serif !important;
    }}

    /* รักษาไอคอนของ Streamlit ไม่ให้เพี้ยน */
    span[data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"],
    .material-icons,
    .material-icons-outlined,
    .material-symbols-rounded,
    .material-symbols-outlined,
    [data-testid="stExpander"] summary svg {{
        font-family: "Material Symbols Rounded", "Material Icons" !important;
        font-feature-settings: "liga" !important;
        font-weight: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        direction: ltr !important;
        line-height: 1 !important;
    }}

    h1, h2, h3, h4,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
        color: var(--ink) !important;
    }}

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {{
        color: var(--muted) !important;
    }}

    /* ============ Smooth Settings Slide-Down Drawer ============ */
    div:has(> .st-key-settings_drawer) {{
        display: grid !important;
        transition:
            grid-template-rows 0.48s var(--spring),
            opacity 0.38s ease,
            transform 0.48s var(--spring),
            margin-bottom 0.48s var(--spring) !important;
        overflow: hidden !important;
    }}

    .st-key-settings_drawer {{
        min-height: 0 !important;
        overflow: hidden !important;
        padding: 20px 22px !important;
        border: 1px solid var(--liquid-border-hover) !important;
        border-radius: var(--radius-xl) !important;
        background: var(--liquid-bg) !important;
        -webkit-backdrop-filter: blur(26px) saturate(190%) !important;
        backdrop-filter: blur(26px) saturate(190%) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim) !important;
    }}

    {drawer_css}

    /* ============ Header Capsule (Tech HUD Style) ============ */
    .app-brand {{
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        min-height: 74px;
        padding: 13px 22px !important;
        border: 1px solid var(--liquid-border) !important;
        border-radius: var(--radius-xl) !important;
        background: var(--liquid-bg) !important;
        -webkit-backdrop-filter: blur(24px) saturate(185%) !important;
        backdrop-filter: blur(24px) saturate(185%) !important;
        box-shadow: var(--shadow-glass), var(--liquid-rim) !important;
        transition: all 0.35s var(--spring) !important;
        animation: hudFadeIn 0.6s var(--spring) both;
    }}

    .app-brand:hover {{
        transform: translateY(-2px);
        border-color: var(--liquid-border-hover) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim) !important;
    }}

    .app-brand-left {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}

    .app-brand-icon {{
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
    }}

    .app-title {{
        font-size: 22px !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        background: var(--title-gradient);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .app-subtitle {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 2px;
        color: var(--muted) !important;
        font-size: 12px !important;
        font-family: 'JetBrains Mono', 'Prompt', monospace !important;
    }}

    .live-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 10px #10b981;
        display: inline-block;
        animation: pulseGlow 2s infinite;
    }}

    @keyframes pulseGlow {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.3); opacity: 0.65; }}
    }}

    @keyframes hudFadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ============ Ultra-Transparent Liquid Glass Surfaces ============ */
    [data-testid="stMetric"],
    [data-testid="stExpander"],
    .collection-section,
    .collection-stop,
    .tech-stat-card {{
        border: 1px solid var(--liquid-border) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--liquid-bg) !important;
        -webkit-backdrop-filter: blur(22px) saturate(180%) !important;
        backdrop-filter: blur(22px) saturate(180%) !important;
        box-shadow: var(--shadow-glass), var(--liquid-rim) !important;
        transition:
            transform 0.32s var(--spring),
            box-shadow 0.32s var(--spring),
            border-color 0.25s ease,
            background 0.25s ease !important;
    }}

    [data-testid="stMetric"] {{
        padding: 14px 16px !important;
        border-radius: var(--radius-md) !important;
    }}

    [data-testid="stMetric"]:hover,
    .collection-stop:hover,
    .tech-stat-card:hover {{
        transform: translateY(-3px) scale(1.01);
        background: var(--liquid-bg-hover) !important;
        border-color: var(--liquid-border-hover) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim) !important;
    }}

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {{
        color: var(--muted) !important;
        font-size: 11.5px !important;
        font-weight: 500 !important;
    }}

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {{
        color: var(--ink) !important;
        font-family: 'JetBrains Mono', 'Prompt', sans-serif !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }}

    /* ============ Smooth Animated Expanders ============ */
    [data-testid="stExpander"] {{
        overflow: hidden !important;
        margin: 6px 0 14px !important;
        animation: hudFadeIn 0.45s var(--spring) both;
    }}

    [data-testid="stExpander"]:hover {{
        border-color: var(--liquid-border-hover) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim) !important;
    }}

    [data-testid="stExpander"] details {{
        border: 0 !important;
        background: transparent !important;
    }}

    [data-testid="stExpander"] summary {{
        display: flex !important;
        align-items: center !important;
        gap: 0.55rem !important;
        min-height: 48px !important;
        padding: 10px 18px !important;
        background: transparent !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
        transition: background 0.25s ease, padding-left 0.28s var(--spring) !important;
    }}

    [data-testid="stExpander"] summary:hover {{
        background: var(--accent-glow) !important;
        padding-left: 22px !important;
    }}

    [data-testid="stExpander"] summary p {{
        margin: 0 !important;
        color: var(--ink) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }}

    [data-testid="stExpander"] summary svg {{
        transition: transform 0.32s var(--spring) !important;
    }}

    [data-testid="stExpander"] details[open] > summary svg {{
        transform: rotate(90deg);
    }}

    [data-testid="stExpander"] > div,
    [data-testid="stExpanderDetails"] {{
        padding: 6px 16px 16px !important;
        animation: hudFadeIn 0.35s var(--spring) both;
    }}

    /* ============ Liquid Pill Buttons (Spring + Shimmer) ============ */
    .stButton > button,
    [data-testid="stDownloadButton"] > button,
    [data-testid="stPopover"] > button {{
        position: relative !important;
        overflow: hidden !important;
        border: 1px solid var(--liquid-border) !important;
        border-radius: 14px !important;
        background: var(--btn-bg) !important;
        -webkit-backdrop-filter: blur(18px) saturate(170%) !important;
        backdrop-filter: blur(18px) saturate(170%) !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        min-height: 44px !important;
        width: 100%;
        box-shadow: var(--shadow-glass), var(--liquid-rim) !important;
        transition:
            transform 0.28s var(--spring),
            box-shadow 0.28s var(--spring),
            border-color 0.22s ease,
            background 0.22s ease !important;
    }}

    .stButton > button::before,
    [data-testid="stPopover"] > button::before {{
        content: "";
        position: absolute;
        top: 0;
        left: -110%;
        width: 70%;
        height: 100%;
        background: linear-gradient(110deg, transparent, rgba(255, 255, 255, 0.35), transparent);
        transition: left 0.5s var(--spring);
        pointer-events: none;
    }}

    .stButton > button:hover::before,
    [data-testid="stPopover"] > button:hover::before {{
        left: 125%;
    }}

    .stButton > button:hover,
    [data-testid="stDownloadButton"] > button:hover,
    [data-testid="stPopover"] > button:hover {{
        transform: translateY(-2.5px) scale(1.015) !important;
        background: var(--btn-bg-hover) !important;
        border-color: var(--liquid-border-hover) !important;
        color: var(--accent) !important;
        box-shadow: var(--shadow-hover), var(--liquid-rim) !important;
    }}

    .stButton > button:active,
    [data-testid="stPopover"] > button:active {{
        transform: translateY(0) scale(0.96) !important;
    }}

    .stButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"] {{
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #0d9488 0%, #4f46e5 55%, #9333ea 100%) !important;
        box-shadow: 0 10px 24px -4px var(--accent-glow), inset 0 1px 1px rgba(255, 255, 255, 0.45) !important;
    }}

    .stButton > button[kind="primary"] *,
    [data-testid="stBaseButton-primary"] * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-testid="stPopoverBody"] {{
        background: var(--popover-bg) !important;
        -webkit-backdrop-filter: blur(22px) !important;
        backdrop-filter: blur(22px) !important;
        color: var(--ink) !important;
        border: 1px solid var(--liquid-border) !important;
        border-radius: 18px !important;
        box-shadow: var(--shadow-hover) !important;
    }}

    /* ============ Inputs & File Uploader ============ */
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label {{
        color: var(--ink-soft) !important;
        font-size: 12px !important;
    }}

    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="select"] > div {{
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--liquid-border) !important;
        background: var(--input-bg) !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
    }}

    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] p {{
        color: var(--ink) !important;
    }}

    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] > section {{
        background: transparent !important;
        border: 0 !important;
        padding: 0 !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        min-height: 80px !important;
        padding: 14px 16px !important;
        border: 1.5px dashed var(--liquid-border-hover) !important;
        border-radius: 16px !important;
        background: var(--liquid-subtle) !important;
        transition: all 0.28s var(--spring) !important;
    }}

    [data-testid="stFileUploaderDropzone"]:hover {{
        transform: translateY(-2px);
        border-color: var(--accent) !important;
        background: var(--liquid-bg-hover) !important;
        box-shadow: var(--shadow-hover) !important;
    }}

    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploaderFile"] * {{
        color: var(--ink-soft) !important;
    }}

    [data-testid="stFileUploaderDropzone"] button {{
        border-radius: 10px !important;
        background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
        color: #030712 !important;
        border: 0 !important;
        padding: 5px 14px !important;
        font-weight: 700 !important;
    }}

    [data-testid="stFileUploaderDropzone"] button * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* ============ Custom Tech HUD Elements ============ */
    .tech-stat-row {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin: 6px 0 14px;
    }}

    .tech-stat-card {{
        padding: 13px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .tech-stat-label {{
        font-size: 11.5px;
        color: var(--muted);
        font-weight: 500;
    }}

    .tech-stat-val {{
        font-size: 20px;
        font-weight: 700;
        color: var(--ink);
        font-family: 'JetBrains Mono', 'Prompt', sans-serif;
    }}

    .upload-camera-label {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 4px 0;
        color: var(--ink) !important;
        font-size: 13.5px;
        font-weight: 600;
    }}

    .upload-hint {{
        color: var(--muted) !important;
        font-size: 11.5px;
        margin: 0 0 8px;
    }}

    .camera-detail-card {{
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
    }}

    .camera-status-pill {{
        display: inline-flex;
        align-items: center;
        padding: 5px 13px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }}

    .camera-action-card {{
        flex: 1 1 200px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12.5px;
    }}

    .action-label {{ font-weight: 700; color: var(--accent) !important; white-space: nowrap; }}
    .action-text {{ color: var(--ink) !important; }}
    .camera-image-title {{ display: block; margin: 4px 0 6px; font-size: 12.5px !important; font-weight: 600 !important; color: var(--ink) !important; }}
    .chart-tip {{ margin: 0 0 8px; padding: 7px 12px; border-radius: 10px; border: 1px solid var(--liquid-border); background: var(--liquid-subtle); color: var(--ink-soft) !important; font-size: 11.5px; }}
    .history-title {{ margin: 14px 0 8px; font-size: 13.5px; font-weight: 700; color: var(--ink) !important; }}
    .settings-title {{ font-size: 17px; font-weight: 700; color: var(--ink) !important; }}
    .settings-subtitle {{ margin-top: 2px; color: var(--muted) !important; font-size: 12px; margin-bottom: 10px; }}
    .settings-section-label {{ margin: 12px 0 6px; color: var(--accent) !important; font-size: 12.5px; font-weight: 600; }}

    /* Collection Priority Route */
    .collection-section {{ margin-top: 14px; padding: 20px 22px; }}
    .collection-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; margin-bottom: 14px; }}
    .collection-title {{ font-size: 18px; font-weight: 700; color: var(--ink) !important; margin-bottom: 2px; }}
    .collection-subtitle {{ color: var(--muted) !important; font-size: 12px; }}
    .collection-road {{
        position: relative;
        height: 116px;
        margin: 0 0 16px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.78) 0%, rgba(9, 14, 28, 0.88) 100%) !important;
        border: 1px solid var(--liquid-border);
        overflow: hidden;
        box-shadow: inset 0 4px 16px rgba(0, 0, 0, 0.45);
    }}
    .collection-lane {{
        position: absolute;
        left: 4%;
        right: 4%;
        top: 54%;
        height: 3px;
        transform: translateY(-50%);
        background: repeating-linear-gradient(90deg, rgba(0, 245, 212, 0.65) 0 36px, transparent 36px 64px);
    }}
    .collection-checkpoints {{
        position: absolute;
        left: 6%;
        right: 8%;
        top: 32px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        z-index: 4;
    }}
    .collection-checkpoint-wrap {{ min-width: 40px; text-align: center; }}
    .collection-checkpoint {{
        width: 30px;
        height: 30px;
        margin: 0 auto;
        border: 2.5px solid #ffffff;
        border-radius: 50%;
        display: grid;
        place-items: center;
        box-shadow: 0 0 14px rgba(0, 245, 212, 0.45);
        color: #ffffff;
        font-size: 11px;
        font-weight: 700;
    }}
    .collection-checkpoint-label {{
        margin-top: 6px;
        color: #f8fafc !important;
        font-size: 10.5px;
        font-weight: 600;
        white-space: nowrap;
    }}
    .collection-truck {{
        position: absolute;
        left: 4%;
        top: 56px;
        z-index: 6;
        font-size: 28px;
        transform: scaleX(-1);
        animation: collectionDriveOneWay 9s linear infinite;
        pointer-events: none;
    }}
    @keyframes collectionDriveOneWay {{
        0%   {{ left: 4%; opacity: 0; }}
        8%   {{ opacity: 1; }}
        92%  {{ opacity: 1; }}
        100% {{ left: 93%; opacity: 0; }}
    }}
    .collection-road-arrow {{ position: absolute; right: 3%; top: 46px; color: var(--accent); font-size: 18px; z-index: 5; }}
    .collection-road-label {{ position: absolute; left: 50%; bottom: 8px; transform: translateX(-50%); color: rgba(255,255,255,0.7) !important; font-size: 10px; font-family: 'JetBrains Mono', monospace; }}
    .collection-stops {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    .collection-stop {{ position: relative; padding: 15px; }}
    .collection-rank {{
        position: absolute;
        top: 12px;
        right: 12px;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        color: #fff;
        font-weight: 700;
        font-size: 12px;
    }}
    .collection-camera {{ font-size: 13.5px; font-weight: 700; color: var(--ink) !important; padding-right: 34px; }}
    .collection-war {{ font-size: 19px; font-weight: 700; color: var(--accent) !important; margin-top: 4px; font-family: 'JetBrains Mono', sans-serif; }}
    .collection-level {{ font-size: 11.5px; color: var(--ink-soft) !important; margin-top: 2px; }}
    .collection-detail {{ margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--liquid-border); font-size: 11px; line-height: 1.55; color: var(--muted) !important; }}
    .collection-note {{ margin-top: 10px; text-align: center; color: var(--muted) !important; font-size: 11px; }}
    .collection-empty {{ margin-top: 10px; padding: 18px; border-radius: 14px; border: 1px dashed var(--liquid-border); background: var(--liquid-subtle); color: var(--muted) !important; text-align: center; font-size: 12.5px; }}

    /* Plotly Glass Container */
    .js-plotly-plot .plotly .main-svg {{ background: transparent !important; }}
    .js-plotly-plot .plotly .main-svg .bg {{ fill: transparent !important; }}
    [data-testid="stPlotlyChart"] {{
        padding: 10px;
        border-radius: var(--radius-md);
        border: 1px solid var(--liquid-border);
        background: var(--liquid-subtle);
        -webkit-backdrop-filter: blur(16px);
        backdrop-filter: blur(16px);
    }}

    [data-testid="stAlert"] {{
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--liquid-border) !important;
        background: var(--liquid-bg) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        backdrop-filter: blur(16px) !important;
        color: var(--ink) !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
