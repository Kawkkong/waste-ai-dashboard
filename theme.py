import streamlit as st


def inject_theme() -> None:
    """Inject lightweight 60fps Liquid Glass theme with full Light/Dark mode support."""
    dark_mode = bool(st.session_state.get("theme_dark_mode", False))

    if dark_mode:
        tokens = """
        --ink: #f1f5f9;
        --ink-soft: #cbd5e1;
        --muted: #94a3b8;
        --accent: #2dd4bf;
        --accent-2: #818cf8;
        --accent-glow: rgba(45, 212, 191, 0.22);
        --bg-mesh:
            radial-gradient(55% 50% at 12% 10%, rgba(13, 148, 136, 0.28) 0%, transparent 70%),
            radial-gradient(50% 45% at 88% 12%, rgba(79, 70, 229, 0.25) 0%, transparent 70%),
            radial-gradient(55% 50% at 82% 88%, rgba(124, 58, 237, 0.20) 0%, transparent 70%),
            linear-gradient(135deg, #070d17 0%, #0c1626 50%, #101528 100%);
        --glass-surface: linear-gradient(135deg, rgba(22, 37, 56, 0.86) 0%, rgba(15, 25, 40, 0.76) 100%);
        --glass-surface-hover: linear-gradient(135deg, rgba(30, 49, 72, 0.94) 0%, rgba(20, 34, 52, 0.86) 100%);
        --glass-subtle: rgba(15, 26, 42, 0.75);
        --glass-border: rgba(148, 163, 184, 0.20);
        --glass-border-hover: rgba(45, 212, 191, 0.55);
        --glass-rim: inset 0 1px 0 rgba(255, 255, 255, 0.12);
        --shadow-card: 0 10px 26px -6px rgba(0, 0, 0, 0.50);
        --shadow-hover: 0 14px 32px -6px rgba(45, 212, 191, 0.20), 0 8px 20px -4px rgba(0, 0, 0, 0.55);
        --btn-bg: linear-gradient(135deg, rgba(30, 48, 68, 0.92) 0%, rgba(19, 32, 48, 0.85) 100%);
        --btn-bg-hover: linear-gradient(135deg, rgba(38, 62, 86, 0.98) 0%, rgba(25, 42, 62, 0.94) 100%);
        --input-bg: rgba(10, 18, 30, 0.88);
        --dropzone-bg: linear-gradient(135deg, rgba(17, 30, 46, 0.82), rgba(12, 22, 34, 0.68));
        --popover-bg: #112032;
        --title-gradient: linear-gradient(95deg, #ffffff 10%, #5eead4 55%, #a5b4fc 100%);
        """
    else:
        tokens = """
        --ink: #0f172a;
        --ink-soft: #334155;
        --muted: #64748b;
        --accent: #0d9488;
        --accent-2: #4f46e5;
        --accent-glow: rgba(13, 148, 136, 0.16);
        --bg-mesh:
            radial-gradient(55% 50% at 12% 10%, rgba(153, 246, 228, 0.60) 0%, transparent 70%),
            radial-gradient(50% 45% at 88% 12%, rgba(191, 219, 254, 0.65) 0%, transparent 70%),
            radial-gradient(55% 50% at 82% 88%, rgba(221, 214, 254, 0.55) 0%, transparent 70%),
            radial-gradient(45% 40% at 14% 88%, rgba(254, 215, 170, 0.42) 0%, transparent 70%),
            linear-gradient(135deg, #f0fdfa 0%, #eff6ff 50%, #f5f3ff 100%);
        --glass-surface: linear-gradient(135deg, rgba(255, 255, 255, 0.84) 0%, rgba(255, 255, 255, 0.62) 100%);
        --glass-surface-hover: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.80) 100%);
        --glass-subtle: rgba(255, 255, 255, 0.70);
        --glass-border: rgba(255, 255, 255, 0.90);
        --glass-border-hover: rgba(13, 148, 136, 0.48);
        --glass-rim: inset 0 1px 0 rgba(255, 255, 255, 0.96);
        --shadow-card: 0 8px 22px -4px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
        --shadow-hover: 0 14px 28px -6px rgba(13, 148, 136, 0.15), 0 6px 14px -3px rgba(79, 70, 229, 0.08);
        --btn-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(248, 250, 252, 0.80) 100%);
        --btn-bg-hover: linear-gradient(135deg, #ffffff 0%, #f0fdfa 100%);
        --input-bg: rgba(255, 255, 255, 0.92);
        --dropzone-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.78), rgba(240, 253, 250, 0.55));
        --popover-bg: #ffffff;
        --title-gradient: linear-gradient(95deg, #0f172a 15%, #0d9488 55%, #4f46e5 100%);
        """

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

    :root {{
        {tokens}
        --spring: cubic-bezier(0.22, 1, 0.36, 1);
        --radius-xl: 22px;
        --radius-lg: 18px;
        --radius-md: 14px;
        --radius-sm: 10px;
    }}

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {{
        display: none !important;
    }}
    #MainMenu, footer {{
        visibility: hidden !important;
    }}

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
        z-index: -1;
        background: var(--bg-mesh);
        pointer-events: none;
    }}

    .block-container {{
        max-width: 1180px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 2.8rem !important;
    }}

    [data-testid="stVerticalBlock"] {{
        gap: 0.65rem;
    }}

    html, body, button, input, textarea, select,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMetric"],
    [data-testid="stWidgetLabel"],
    [data-testid="stPopover"] {{
        font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
    }}

    /* Preserve Material Symbols Icons */
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
        font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
    }}

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {{
        color: var(--muted) !important;
    }}

    hr {{
        border: 0 !important;
        height: 1px !important;
        margin: 16px 0 !important;
        background: linear-gradient(90deg, transparent, var(--glass-border-hover), transparent) !important;
        opacity: 0.45;
    }}

    /* Header Bar */
    .app-brand {{
        display: flex;
        align-items: center;
        gap: 14px;
        min-height: 68px;
        padding: 12px 18px !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-xl) !important;
        background: var(--glass-surface) !important;
        -webkit-backdrop-filter: blur(12px);
        backdrop-filter: blur(12px);
        box-shadow: var(--shadow-card), var(--glass-rim) !important;
        transition: transform 0.24s var(--spring), box-shadow 0.24s var(--spring), border-color 0.24s ease !important;
    }}

    .app-brand:hover {{
        transform: translateY(-1.5px);
        border-color: var(--glass-border-hover) !important;
        box-shadow: var(--shadow-hover), var(--glass-rim) !important;
    }}

    .app-brand-icon {{
        width: 46px !important;
        height: 46px !important;
        flex: 0 0 46px;
        border-radius: 14px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        color: #fff;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%) !important;
        box-shadow: 0 6px 16px var(--accent-glow), inset 0 1px 1px rgba(255, 255, 255, 0.4) !important;
    }}

    .app-title {{
        font-size: 21px !important;
        font-weight: 700 !important;
        line-height: 1.25;
        background: var(--title-gradient);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .app-subtitle {{
        margin-top: 2px;
        color: var(--muted) !important;
        font-size: 12px !important;
    }}

    .header-divider {{
        height: 1px;
        margin: 10px 0 16px;
        background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
    }}

    /* Liquid Glass Cards */
    [data-testid="stMetric"],
    [data-testid="stExpander"],
    .settings-card,
    .collection-section,
    .collection-stop {{
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--glass-surface) !important;
        -webkit-backdrop-filter: blur(12px);
        backdrop-filter: blur(12px);
        box-shadow: var(--shadow-card), var(--glass-rim) !important;
        transition: transform 0.22s var(--spring), box-shadow 0.22s var(--spring), border-color 0.22s ease !important;
    }}

    [data-testid="stMetric"] {{
        padding: 12px 16px !important;
        border-radius: var(--radius-md) !important;
    }}

    [data-testid="stMetric"]:hover,
    .collection-stop:hover {{
        transform: translateY(-2px);
        background: var(--glass-surface-hover) !important;
        border-color: var(--glass-border-hover) !important;
        box-shadow: var(--shadow-hover), var(--glass-rim) !important;
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
        font-size: 1.35rem !important;
        font-weight: 700 !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        overflow: hidden !important;
        margin: 4px 0 12px !important;
    }}

    [data-testid="stExpander"]:hover {{
        border-color: var(--glass-border-hover) !important;
        box-shadow: var(--shadow-hover), var(--glass-rim) !important;
    }}

    [data-testid="stExpander"] details {{
        border: 0 !important;
        background: transparent !important;
    }}

    [data-testid="stExpander"] summary {{
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        min-height: 46px !important;
        padding: 10px 16px !important;
        background: transparent !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
        transition: background 0.2s ease, padding-left 0.22s var(--spring) !important;
    }}

    [data-testid="stExpander"] summary:hover {{
        background: var(--accent-glow) !important;
        padding-left: 19px !important;
    }}

    [data-testid="stExpander"] summary p {{
        margin: 0 !important;
        color: var(--ink) !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
    }}

    [data-testid="stExpander"] > div {{
        padding: 4px 14px 14px !important;
    }}

    /* Buttons & Controls */
    .stButton > button,
    [data-testid="stDownloadButton"] > button,
    [data-testid="stPopover"] > button {{
        border: 1px solid var(--glass-border) !important;
        border-radius: 13px !important;
        background: var(--btn-bg) !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        min-height: 42px !important;
        width: 100%;
        box-shadow: var(--shadow-card), var(--glass-rim) !important;
        transition: transform 0.2s var(--spring), box-shadow 0.2s var(--spring), border-color 0.2s ease, background 0.2s ease !important;
    }}

    .stButton > button:hover,
    [data-testid="stDownloadButton"] > button:hover,
    [data-testid="stPopover"] > button:hover {{
        transform: translateY(-2px) !important;
        background: var(--btn-bg-hover) !important;
        border-color: var(--glass-border-hover) !important;
        color: var(--accent) !important;
        box-shadow: var(--shadow-hover), var(--glass-rim) !important;
    }}

    .stButton > button:active,
    [data-testid="stPopover"] > button:active {{
        transform: translateY(0) scale(0.97) !important;
    }}

    .stButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"] {{
        border: 1px solid rgba(255, 255, 255, 0.28) !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%) !important;
        box-shadow: 0 8px 20px -4px var(--accent-glow) !important;
    }}

    .stButton > button[kind="primary"] *,
    [data-testid="stBaseButton-primary"] * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* Toggle Pill in Header */
    [data-testid="stToggle"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 42px !important;
        padding: 4px 12px !important;
        border-radius: 13px !important;
        border: 1px solid var(--glass-border) !important;
        background: var(--btn-bg) !important;
        box-shadow: var(--shadow-card), var(--glass-rim) !important;
    }}

    [data-testid="stToggle"] label,
    [data-testid="stToggle"] p,
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] p {{
        color: var(--ink) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }}

    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-testid="stPopoverBody"] {{
        background: var(--popover-bg) !important;
        color: var(--ink) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
    }}

    /* Inputs & Uploaders */
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
        border: 1px solid var(--glass-border) !important;
        background: var(--input-bg) !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
    }}

    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] > section {{
        background: transparent !important;
        border: 0 !important;
        padding: 0 !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        min-height: 76px !important;
        padding: 12px 14px !important;
        border: 1.5px dashed var(--glass-border-hover) !important;
        border-radius: 15px !important;
        background: var(--dropzone-bg) !important;
        transition: transform 0.22s var(--spring), border-color 0.22s ease !important;
    }}

    [data-testid="stFileUploaderDropzone"]:hover {{
        transform: translateY(-1.5px);
        border-color: var(--accent) !important;
    }}

    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploaderFile"] * {{
        color: var(--ink-soft) !important;
    }}

    [data-testid="stFileUploaderDropzone"] button {{
        border-radius: 10px !important;
        background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
        color: #ffffff !important;
        border: 0 !important;
        padding: 5px 12px !important;
        font-weight: 600 !important;
    }}

    [data-testid="stFileUploaderDropzone"] button * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* Camera Status & Collection Priority */
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
        padding: 12px 14px;
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        background: var(--glass-subtle);
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }}

    .camera-status-pill,
    .history-detail-status {{
        display: inline-flex;
        align-items: center;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12);
    }}

    .camera-action-card {{
        flex: 1 1 200px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
    }}

    .action-label {{
        font-weight: 700;
        color: var(--accent) !important;
        white-space: nowrap;
    }}

    .action-text {{
        color: var(--ink) !important;
    }}

    .camera-image-title {{
        display: block;
        margin: 4px 0 6px;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        color: var(--ink) !important;
    }}

    .chart-tip {{
        margin: 0 0 8px;
        padding: 7px 12px;
        border-radius: 10px;
        border: 1px solid var(--glass-border);
        background: var(--glass-subtle);
        color: var(--ink-soft) !important;
        font-size: 11.5px;
    }}

    .history-title {{
        margin: 14px 0 8px;
        font-size: 13.5px;
        font-weight: 700;
        color: var(--ink) !important;
    }}

    .settings-card {{
        margin: 6px 0 12px;
        padding: 14px 18px;
    }}
    .settings-title {{ font-size: 17px; font-weight: 700; color: var(--ink) !important; }}
    .settings-subtitle {{ margin-top: 2px; color: var(--muted) !important; font-size: 11.5px; }}
    .settings-section-label {{ margin: 12px 0 6px; color: var(--ink) !important; font-size: 12.5px; font-weight: 600; }}

    /* Collection Road & Cards */
    .collection-section {{
        margin-top: 14px;
        padding: 18px 20px;
        overflow: visible !important;
    }}
    .collection-head {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 14px;
        margin-bottom: 14px;
    }}
    .collection-title {{ font-size: 18px; font-weight: 700; color: var(--ink) !important; margin-bottom: 2px; }}
    .collection-subtitle {{ color: var(--muted) !important; font-size: 11.5px; }}
    .collection-road {{
        position: relative;
        height: 116px;
        margin: 0 0 16px;
        border-radius: 18px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        overflow: hidden;
        box-shadow: inset 0 4px 14px rgba(0, 0, 0, 0.35);
    }}
    .collection-lane {{
        position: absolute;
        left: 4%;
        right: 4%;
        top: 54%;
        height: 3px;
        transform: translateY(-50%);
        background: repeating-linear-gradient(90deg, rgba(255,255,255,0.75) 0 36px, transparent 36px 64px);
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
        border: 3px solid #ffffff;
        border-radius: 50%;
        display: grid;
        place-items: center;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35);
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
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.85);
    }}
    .collection-truck {{
        position: absolute;
        left: 4%;
        top: 56px;
        z-index: 6;
        font-size: 28px;
        transform: scaleX(-1);
        animation: collectionDriveOneWay 10s linear infinite;
        pointer-events: none;
    }}
    @keyframes collectionDriveOneWay {{
        0%   {{ left: 4%; opacity: 0; }}
        8%   {{ opacity: 1; }}
        92%  {{ opacity: 1; }}
        100% {{ left: 93%; opacity: 0; }}
    }}
    .collection-road-arrow {{ position: absolute; right: 3%; top: 46px; color: rgba(255,255,255,0.8); font-size: 18px; z-index: 5; }}
    .collection-road-label {{ position: absolute; left: 50%; bottom: 8px; transform: translateX(-50%); color: rgba(255,255,255,0.75) !important; font-size: 10px; font-weight: 500; }}
    .collection-stops {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    .collection-stop {{ position: relative; padding: 14px; }}
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
    .collection-war {{ font-size: 18px; font-weight: 700; color: var(--accent) !important; margin-top: 4px; }}
    .collection-level {{ font-size: 11.5px; color: var(--ink-soft) !important; margin-top: 2px; }}
    .collection-detail {{ margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--glass-border); font-size: 11px; line-height: 1.55; color: var(--muted) !important; }}
    .collection-note {{ margin-top: 10px; text-align: center; color: var(--muted) !important; font-size: 11px; }}
    .collection-empty {{ margin-top: 10px; padding: 18px; border-radius: 12px; border: 1px dashed var(--glass-border); background: var(--glass-subtle); color: var(--muted) !important; text-align: center; font-size: 12.5px; }}

    /* Plotly Container */
    .js-plotly-plot .plotly .main-svg {{ background: transparent !important; }}
    .js-plotly-plot .plotly .main-svg .bg {{ fill: transparent !important; }}
    [data-testid="stPlotlyChart"] {{
        padding: 8px;
        border-radius: var(--radius-md);
        border: 1px solid var(--glass-border);
        background: var(--glass-subtle);
    }}

    [data-testid="stAlert"] {{
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--glass-border) !important;
        background: var(--glass-surface) !important;
        color: var(--ink) !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
