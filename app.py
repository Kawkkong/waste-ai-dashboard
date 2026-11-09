
# framework หลัก
import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import base64
import copy
import inference as inference_module
from datetime import datetime
import time

# ฟังก์ชันวิเคราะห์ภาพด้วยโมเดล AI
from inference import analyze_frame
from config import CAMERA_CONFIG
from theme import inject_theme

# ส่วนแสดงภาพแบบเต็มจอ กดขยายดูรายละเอียดได้
def show_image_viewer(img_bgr, title="", display_width=340, viewer_height=300):
    if img_bgr is None:
        return

    h, w = img_bgr.shape[:2]

    if w <= 0 or h <= 0:
        return
    ok, encoded = cv2.imencode(
        ".jpg",
        img_bgr,
        [cv2.IMWRITE_JPEG_QUALITY, 92]
    )
    if not ok:
        st.error("ไม่สามารถแสดงภาพได้")
        return

    image_b64 = base64.b64encode(
        encoded.tobytes()
    ).decode("utf-8")

    # ความสูงของภาพตาม aspect ratio จริง
    aspect_height = int(display_width * h / w)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700&display=swap" rel="stylesheet">

        <style>
            * {{
                box-sizing: border-box;
            }}

            html, body {{
                margin: 0;
                padding: 0;
                width: 100%;
                background: transparent;
                overflow: hidden;
            }}

            body {{
                font-family:
                    "Prompt",
                    "Noto Sans Thai",
                    Tahoma,
                    sans-serif;
            }}

            .viewer {{
                position: relative;
                width: 100%;
                max-width: {display_width}px;
                aspect-ratio: {w} / {h};
                margin: 0 auto 2px;
                overflow: hidden;
                background: transparent;
                border-radius: 8px;
                cursor: zoom-in;
            }}

            .viewer img {{
                display: block;
                width: 100%;
                height: 100%;
                object-fit: cover;
                object-position: center;
            }}

            .zoom-btn {{
                position: absolute;
                top: 8px;
                right: 8px;
                z-index: 10;
                border: 0;
                border-radius: 7px;
                padding: 6px 9px;
                background: rgba(0, 0, 0, 0.65);
                color: white;
                font-size: 13px;
                cursor: pointer;
            }}

            .zoom-btn:hover {{
                background: rgba(0, 0, 0, 0.85);
            }}

            .viewer:fullscreen {{
                width: 100vw;
                height: 100vh;
                aspect-ratio: auto;
                max-width: none;
                border-radius: 0;
                background: #000;
                cursor: zoom-out;
            }}

            .viewer:fullscreen img {{
                width: 100vw;
                height: 100vh;
                object-fit: contain;
            }}
        </style>
    </head>

    <body>
        <div class="viewer" id="viewer" title="ดับเบิลคลิกเพื่อขยายภาพ">
            <button class="zoom-btn" id="zoom">⛶ ขยายภาพ</button>
            <img src="data:image/jpeg;base64,{image_b64}" alt="{title}">
        </div>

        <script>
            const viewer = document.getElementById("viewer");
            const zoom = document.getElementById("zoom");

            async function toggleFullscreen() {{
                try {{
                    if (!document.fullscreenElement) {{
                        await viewer.requestFullscreen();
                    }} else {{
                        await document.exitFullscreen();
                    }}
                }} catch (error) {{
                    console.log("Fullscreen unavailable:", error);
                }}
            }}

            zoom.addEventListener("click", function(event) {{
                event.stopPropagation();
                toggleFullscreen();
            }});

            viewer.addEventListener("dblclick", function(event) {{
                if (event.target !== zoom) {{
                    toggleFullscreen();
                }}
            }});

            document.addEventListener("fullscreenchange", function() {{
                zoom.textContent = document.fullscreenElement
                    ? "⛶ ออกจากเต็มหน้าจอ"
                    : "⛶ ขยายภาพ";
            }});
        </script>
    </body>
    </html>
    """

    components.html(
        html,
        height=aspect_height + 20,
        scrolling=False
    )


# =====================================================
# ตั้งค่าหน้าตาเริ่มต้นของ Streamlit

st.set_page_config(
    page_title="ระบบตรวจสอบขยะด้วย AI",
    layout="wide"
)


# =====================================================
# กำหนดสีและคำอธิบายของระดับความหนาแน่นขยะ

LEVEL_INFO = {
    "Normal": {
        "name": "Normal (ไม่มีขยะ)",
        "color": "#4CAF50",
        "action": "ไม่พบขยะ"
    },
    "Low": {
        "name": "Low (ต่ำ)",
        "color": "#2196F3",
        "action": "เฝ้าระวังพื้นที่"
    },
    "Medium": {
        "name": "Medium (ปานกลาง)",
        "color": "#FFD600",
        "action": "เตรียมวางแผนเก็บขยะ"
    },
    "High": {
        "name": "High (สูง)",
        "color": "#FF9800",
        "action": "แจ้งเตือนเจ้าหน้าที่"
    },
    "Critical": {
        "name": "Critical (วิกฤต)",
        "color": "#F44336",
        "action": "แจ้งเจ้าหน้าที่และดำเนินการเก็บขยะด่วน"
    }
}


# =====================================================
# CSS SMALL UI
# =====================================================

st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700&display=swap');

/* Hide Streamlit top chrome / toolbar */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

#MainMenu, footer {
    visibility: hidden !important;
}

:root {
    --ink: #172033;
    --muted: #667085;
    --line: #e5eaf1;
    --accent: #315b8a;
    --accent-soft: #edf4fb;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
button, input, textarea, select,
[data-testid="stMarkdownContainer"],
[data-testid="stMetric"] {
    font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
}

.block-container {
    max-width: 1180px !important;
    padding-top: 1.15rem !important;
    padding-bottom: 1.8rem !important;
}

[data-testid="stVerticalBlock"] { gap: 0.5rem; }

h1, h2, h3, h4, p, label {
    font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
}
h1 { font-size: 1.55rem !important; line-height: 1.25 !important; letter-spacing: -.02em; color: var(--ink) !important; }
h2 { font-size: 1.28rem !important; color: var(--ink) !important; }
h3 { font-size: 1.08rem !important; color: var(--ink) !important; }

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    line-height: 1.55;
}

[data-testid="stCaptionContainer"] { color: var(--muted); }

[data-testid="stMetric"] {
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 11px 14px;
    box-shadow: 0 2px 8px rgba(15,23,42,.035);
    transition: transform .18s ease, box-shadow .18s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(15,23,42,.07);
}

[data-testid="stMetricValue"] {
    font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
    font-size: 11px !important;
    color: var(--muted) !important;
}

.level-box {
    padding: 10px 12px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 7px;
    box-shadow: 0 2px 8px rgba(15,23,42,.05);
}

.recommend {
    background: #f4f6f9;
    border: 1px solid #e6eaf0;
    padding: 10px 12px;
    border-radius: 10px;
    font-size: 13px;
    color: #344054;
}

hr {
    border: 0 !important;
    border-top: 1px solid #e7ebf0 !important;
    margin: 20px 0 !important;
}

.stButton > button {
    border-radius: 9px !important;
    border: 1px solid #d7dee8 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    min-height: 38px !important;
    white-space: nowrap !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.stButton > button:hover {
    border-color: #9eb4cd !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(49,91,138,.10);
}

[data-testid="stImage"] img { border-radius: 9px; }

/* Camera + history dropdowns */
[data-testid="stExpander"] {
    border: 1px solid #dfe6ee !important;
    border-radius: 14px !important;
    background: #ffffff !important;
    box-shadow: 0 4px 14px rgba(15,23,42,.035);
    overflow: hidden !important;
    margin: 5px 0 14px !important;
    transition: box-shadow .18s ease, border-color .18s ease;
}

[data-testid="stExpander"]:hover {
    border-color: #cbd8e6 !important;
    box-shadow: 0 7px 18px rgba(49,91,138,.07);
}

[data-testid="stExpander"] summary {
    min-height: 44px !important;
    padding: 8px 13px !important;
    box-sizing: border-box !important;
    font-family: "Prompt", "Noto Sans Thai", Tahoma, sans-serif !important;
    font-weight: 600 !important;
    color: #172033 !important;
}

[data-testid="stExpander"] summary p {
    margin: 0 !important;
    font-size: 12.5px !important;
    font-weight: 650 !important;
    line-height: 1.45 !important;
}

[data-testid="stExpander"] > div {
    padding: 0 12px 12px !important;
}

.history-detail-status {
    display: inline-flex;
    align-items: center;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    margin: 2px 0 10px;
}

.history-title {
    margin: 16px 0 8px;
    font-size: 13px;
    font-weight: 700;
    color: #172033;
}

.camera-detail-card {
    margin: 4px 0 10px;
    padding: 12px;
    border: 1px solid #e1e8f0;
    border-radius: 13px;
    background: #ffffff;
    box-shadow: 0 5px 16px rgba(15,23,42,.045);
}

.camera-status-pill {
    display: inline-flex;
    align-items: center;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 9px;
}

.camera-action-card {
    display: flex;
    align-items: baseline;
    gap: 7px;
    padding: 8px 10px;
    border: 1px solid #e5eaf0;
    border-radius: 9px;
    background: #f8fafc;
    margin-bottom: 2px;
    font-size: 11px;
    line-height: 1.5;
}

.action-label {
    font-weight: 700;
    color: #172033;
    white-space: nowrap;
}

.action-text {
    color: #475467;
}

.settings-card {
    margin: 6px 0 12px;
    padding: 14px 16px;
    border: 1px solid #e4e9f0;
    border-radius: 14px;
    background: linear-gradient(135deg, #fbfcfe, #f6f8fb);
    box-shadow: 0 4px 14px rgba(15,23,42,.04);
}

.settings-title {
    font-size: 18px;
    font-weight: 700;
    color: #172033;
}

.settings-subtitle {
    margin-top: 2px;
    color: #7a8492;
    font-size: 11px;
}

.settings-section-label {
    margin: 13px 0 7px;
    color: #475467;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .01em;
}

.settings-section-label::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 14px;
    margin-right: 7px;
    vertical-align: -2px;
    border-radius: 4px;
    background: #8da9c7;
}

.upload-camera-label {
    display:flex; align-items:center; justify-content:space-between;
    gap:8px; margin:8px 0 6px; color:var(--ink);
    font-size:13px; font-weight:600;
}

.upload-hint {
    color:var(--muted); font-size:11px; line-height:1.5; margin:0 0 8px;
}

.chart-tip {
    margin:0 4px 8px; padding:7px 10px; border-radius:9px;
    background:#f6f9fc; color:#667085; font-size:11px;
}

/* Collection widget */
.collection-section {
    margin-top: 12px;
    padding: 18px;
    border: 1px solid #dfe6ee;
    border-radius: 18px;
    background: #ffffff;
    box-shadow: 0 8px 24px rgba(15,23,42,.045);
    overflow: hidden;
}
.collection-head { display:flex; align-items:flex-start; justify-content:space-between; gap:14px; margin-bottom:14px; }
.collection-title { font-size:18px; font-weight:700; color:#172033; margin-bottom:2px; }
.collection-subtitle { color:#667085; font-size:11px; line-height:1.55; }
.collection-info { position:relative; flex:0 0 auto; }
.collection-info summary {
    list-style:none; cursor:pointer; width:32px !important; height:32px !important; padding:0 !important;
    display:grid; place-items:center;
    border:1px solid #d7dee8; border-radius:10px; color:#344054; background:#fff;
    transition:transform .18s ease, box-shadow .18s ease, background .18s ease;
}
.collection-info summary::-webkit-details-marker { display:none; }
.collection-info summary:hover { transform:translateY(-1px); background:#f7faff; box-shadow:0 5px 14px rgba(49,91,138,.10); }
.collection-info .info-icon {
    width: 17px;
    height: 17px;
    border: 1.5px solid #667085;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 12px;
    font-style: italic;
    font-weight: 700;
    line-height: 1;
    color: #475467;
    background: #fff;
}
.collection-info-pop {
    position:absolute; right:0; top:40px; z-index:20; width:min(330px,78vw); padding:13px;
    border:1px solid #dfe6ee; border-radius:12px; background:#fff;
    box-shadow:0 14px 30px rgba(15,23,42,.13); color:#344054; font-size:11px; line-height:1.6;
}
.collection-info-pop ol { margin:7px 0; padding-left:20px; }
.collection-example { padding:9px 10px; border-radius:9px; background:#f6f9fc; }

.collection-road {
    position:relative; height:122px; margin:0 2px 15px; border-radius:16px;
    background:linear-gradient(180deg,#4b5563 0%,#364152 100%); overflow:hidden;
    box-shadow:inset 0 4px 12px rgba(0,0,0,.18);
}
.collection-lane {
    position:absolute; left:3%; right:3%; top:54%; height:4px; transform:translateY(-50%);
    background:repeating-linear-gradient(90deg,#f8fafc 0 40px,transparent 40px 68px); opacity:.9;
}
.collection-checkpoints {
    position:absolute; left:3%; right:3%; top:37px; display:flex;
    justify-content:space-between; align-items:flex-start; z-index:4;
}
.collection-checkpoint-wrap { min-width:34px; text-align:center; }
.collection-checkpoint {
    width:30px; height:30px; margin:0 auto; border:4px solid #fff; border-radius:50%;
    display:grid; place-items:center; box-shadow:0 2px 8px rgba(0,0,0,.28);
    color:#fff; font-size:10px; font-weight:700;
}
.collection-checkpoint-label {
    margin-top:7px; color:#fff; font-size:10px; font-weight:600; white-space:nowrap;
    text-shadow:0 1px 2px rgba(0,0,0,.7);
}
.collection-truck {
    position:absolute; left:3%; top:61px; z-index:6; font-size:31px;
    filter:drop-shadow(0 4px 3px rgba(0,0,0,.28)); transform:scaleX(-1);
    animation:collectionDriveOneWay 9s linear infinite; pointer-events:none;
}
@keyframes collectionDriveOneWay {
    0% { left:3%; opacity:0; } 6% { opacity:1; } 94% { opacity:1; } 100% { left:96%; opacity:0; }
}
.collection-road-arrow { position:absolute; right:3%; top:51px; color:rgba(255,255,255,.85); font-size:20px; z-index:5; }
.collection-road-label { position:absolute; left:50%; bottom:9px; transform:translateX(-50%); color:rgba(255,255,255,.78); font-size:10px; font-weight:600; white-space:nowrap; }
.collection-stops { display:grid; grid-template-columns:repeat(auto-fit,minmax(205px,1fr)); gap:10px; }
.collection-stop {
    position:relative; background:#fff; border:1px solid #e2e8f0; border-radius:13px;
    padding:12px; box-shadow:0 2px 8px rgba(15,23,42,.035);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.collection-stop:hover { transform:translateY(-2px); border-color:#cbd8e8; box-shadow:0 8px 20px rgba(15,23,42,.08); }
.collection-rank {
    position:absolute; top:10px; right:10px; width:28px; height:28px; border-radius:50%;
    display:grid; place-items:center; color:#fff; font-weight:700; font-size:12px;
}
.collection-camera { font-size:13px; font-weight:700; color:#1f2937; padding-right:34px; }
.collection-war { font-size:18px; font-weight:700; color:#111827; margin-top:5px; }
.collection-level { font-size:11px; color:#667085; margin-top:2px; }
.collection-detail { margin-top:8px; padding-top:8px; border-top:1px dashed #e5eaf1; font-size:10px; line-height:1.6; color:#667085; }
.collection-note { margin-top:11px; text-align:center; color:#667085; font-size:10px; }
.collection-empty { padding:18px; border-radius:12px; background:#f8fafc; color:#667085; text-align:center; font-size:12px; }

.app-brand {
    display: flex;
    align-items: center;
    gap: 13px;
    min-height: 62px;
    padding: 9px 14px;
    border: 1px solid #e0e8f2;
    border-radius: 16px;
    background: linear-gradient(135deg, #f7fbff 0%, #ffffff 72%);
    box-shadow: 0 6px 20px rgba(49,91,138,.055);
}

.app-brand-icon {
    width: 46px;
    height: 46px;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #eef4fb, #f7f9fc);
    border: 1px solid #dbe5f0;
    box-shadow: 0 5px 16px rgba(49,91,138,.08);
    font-size: 23px;
}

.app-title {
    font-size: 25px;
    line-height: 1.2;
    font-weight: 700;
    letter-spacing: -.025em;
    color: #172033;
}

.app-subtitle {
    margin-top: 4px;
    color: #718096;
    font-size: 12px;
}

.header-divider {
    height: 1px;
    margin: 15px 0 20px;
    background: linear-gradient(90deg, transparent, #e5eaf1 10%, #e5eaf1 90%, transparent);
}

.camera-image-title {
    display: block !important;
    position: relative !important;
    z-index: 2 !important;
    min-height: 24px !important;
    margin: 4px 0 9px !important;
    padding: 0 !important;
    font-family: "Prompt", "Noto Sans Thai", Tahoma, sans-serif !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    line-height: 1.5 !important;
    color: #172033 !important;
}

@media (max-width:700px) {
    .collection-section { padding:13px; }
    .collection-title { font-size:18px; }
    .collection-road { height:112px; }
    .collection-stops { grid-template-columns:1fr; }
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# เก็บข้อมูลระหว่างการใช้งานหน้าเว็บ

if "camera_results" not in st.session_state:
    st.session_state.camera_results = {}

if "history" not in st.session_state:
    st.session_state.history = {}

if "selected_history_by_camera" not in st.session_state:
    st.session_state.selected_history_by_camera = {}

if "selected_history_camera" not in st.session_state:
    st.session_state.selected_history_camera = None

if "density_alert" not in st.session_state:
    st.session_state.density_alert = None

for cam in CAMERA_CONFIG:
    if cam not in st.session_state.history:
        st.session_state.history[cam] = []


# =====================================================
# การตั้งค่า ROI และ Threshold จากหน้าเว็บ

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

if "default_camera_config" not in st.session_state:
    st.session_state.default_camera_config = copy.deepcopy(CAMERA_CONFIG)

if "runtime_camera_config" not in st.session_state:
    st.session_state.runtime_camera_config = copy.deepcopy(
        st.session_state.default_camera_config
    )
else:
    CAMERA_CONFIG.clear()
    CAMERA_CONFIG.update(
        copy.deepcopy(st.session_state.runtime_camera_config)
    )


def save_camera_config(camera, roi, thresholds):
    new_config = copy.deepcopy(st.session_state.runtime_camera_config)
    if camera not in new_config:
        new_config[camera] = {}
    new_config[camera]["roi"] = tuple(int(v) for v in roi)
    new_config[camera]["threshold"] = {
        "low": float(thresholds["low"]),
        "medium": float(thresholds["medium"]),
        "high": float(thresholds["high"]),
    }
    st.session_state.runtime_camera_config = new_config
    CAMERA_CONFIG.clear()
    CAMERA_CONFIG.update(copy.deepcopy(new_config))


def restore_camera_default(camera, restore_roi=True, restore_threshold=True):
    default_cfg = copy.deepcopy(
        st.session_state.default_camera_config[camera]
    )

    new_config = copy.deepcopy(
        st.session_state.runtime_camera_config
    )

    if camera not in new_config:
        new_config[camera] = {}

    if restore_roi:
        new_config[camera]["roi"] = tuple(default_cfg["roi"])

    if restore_threshold:
        new_config[camera]["threshold"] = copy.deepcopy(
            default_cfg["threshold"]
        )

    st.session_state.runtime_camera_config = new_config

    CAMERA_CONFIG.clear()
    CAMERA_CONFIG.update(
        copy.deepcopy(new_config)
    )


def reset_roi_callback(camera):
    restore_camera_default(
        camera,
        restore_roi=True,
        restore_threshold=False
    )

    default_roi = st.session_state.default_camera_config[camera]["roi"]
    st.session_state[f"roi_x1_{camera}"] = int(default_roi[0])
    st.session_state[f"roi_y1_{camera}"] = int(default_roi[1])
    st.session_state[f"roi_x2_{camera}"] = int(default_roi[2])
    st.session_state[f"roi_y2_{camera}"] = int(default_roi[3])


def reset_threshold_callback(camera):
    restore_camera_default(
        camera,
        restore_roi=False,
        restore_threshold=True
    )

    default_threshold = st.session_state.default_camera_config[camera]["threshold"]
    st.session_state[f"threshold_low_{camera}"] = float(default_threshold["low"])
    st.session_state[f"threshold_medium_{camera}"] = float(default_threshold["medium"])
    st.session_state[f"threshold_high_{camera}"] = float(default_threshold["high"])


if st.session_state.show_settings:
    st.markdown(
        """
        <div class="settings-card">
            <div class="settings-heading">
                <div>
                    <div class="settings-title">⚙️ การตั้งค่ากล้อง</div>
                    <div class="settings-subtitle">ปรับพื้นที่ ROI และเกณฑ์ความหนาแน่นสำหรับกล้องที่เลือก</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    setting_camera = st.selectbox(
        "กล้อง",
        list(CAMERA_CONFIG.keys()),
        key="setting_camera",
        label_visibility="collapsed"
    )

    cfg = CAMERA_CONFIG[setting_camera]
    current_roi = cfg["roi"]
    current_threshold = cfg["threshold"]

    if setting_camera in st.session_state.camera_results:
        setting_img = st.session_state.camera_results[setting_camera].get("original")
        if setting_img is not None:
            image_h, image_w = setting_img.shape[:2]
        else:
            image_w = max(int(current_roi[2]), 1000)
            image_h = max(int(current_roi[3]), 1000)
    else:
        image_w = max(int(current_roi[2]), 1000)
        image_h = max(int(current_roi[3]), 1000)

    st.markdown('<div class="settings-section-label">พื้นที่ ROI</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        new_x1 = st.number_input(
            "X1", min_value=0, max_value=max(0, image_w - 1),
            value=min(max(0, int(current_roi[0])), max(0, image_w - 1)),
            step=1, key=f"roi_x1_{setting_camera}"
        )
    with r2:
        new_y1 = st.number_input(
            "Y1", min_value=0, max_value=max(0, image_h - 1),
            value=min(max(0, int(current_roi[1])), max(0, image_h - 1)),
            step=1, key=f"roi_y1_{setting_camera}"
        )
    with r3:
        new_x2 = st.number_input(
            "X2", min_value=1, max_value=max(1, image_w),
            value=min(max(1, int(current_roi[2])), max(1, image_w)),
            step=1, key=f"roi_x2_{setting_camera}"
        )
    with r4:
        new_y2 = st.number_input(
            "Y2", min_value=1, max_value=max(1, image_h),
            value=min(max(1, int(current_roi[3])), max(1, image_h)),
            step=1, key=f"roi_y2_{setting_camera}"
        )

    st.markdown('<div class="settings-section-label">ระดับความหนาแน่น</div>', unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)
    with t1:
        new_low = st.number_input(
            "Low", min_value=0.0, max_value=100.0,
            value=float(current_threshold["low"]), step=0.1,
            key=f"threshold_low_{setting_camera}"
        )
    with t2:
        new_medium = st.number_input(
            "Medium", min_value=0.0, max_value=100.0,
            value=float(current_threshold["medium"]), step=0.1,
            key=f"threshold_medium_{setting_camera}"
        )
    with t3:
        new_high = st.number_input(
            "High", min_value=0.0, max_value=100.0,
            value=float(current_threshold["high"]), step=0.1,
            key=f"threshold_high_{setting_camera}"
        )

    apply_current = st.checkbox(
        "วิเคราะห์ภาพล่าสุดของกล้องนี้ใหม่ทันทีหลังบันทึก",
        value=False,
        key=f"reanalyze_{setting_camera}"
    )

    reset_roi_col, reset_threshold_col = st.columns(2)

    with reset_roi_col:
        st.button(
            "↩️ ROI กลับค่าเริ่มต้น",
            use_container_width=True,
            key=f"reset_roi_{setting_camera}",
            help="คืนค่า ROI ของกล้องนี้ตาม config.py",
            on_click=reset_roi_callback,
            args=(setting_camera,)
        )

    with reset_threshold_col:
        st.button(
            "↩️ Threshold กลับค่าเริ่มต้น",
            use_container_width=True,
            key=f"reset_threshold_{setting_camera}",
            help="คืนค่า Threshold ของกล้องนี้ตาม config.py",
            on_click=reset_threshold_callback,
            args=(setting_camera,)
        )

    save_col, close_col = st.columns(2)
    with save_col:
        if st.button("💾 บันทึกการตั้งค่า", type="primary", use_container_width=True, key="save_camera_config"):
            if not (new_x1 < new_x2 and new_y1 < new_y2):
                st.error("ROI ไม่ถูกต้อง: ต้องให้ X1 < X2 และ Y1 < Y2")
            elif not (new_low < new_medium < new_high):
                st.error("Threshold ต้องเรียงจากน้อยไปมาก: Low < Medium < High")
            else:
                save_camera_config(setting_camera, (new_x1, new_y1, new_x2, new_y2), {"low": new_low, "medium": new_medium, "high": new_high})
                if apply_current and setting_camera in st.session_state.camera_results:
                    current_img = st.session_state.camera_results[setting_camera]["original"]
                    inference_module.previous_WAR.pop(setting_camera, None)
                    refreshed = analyze_frame(current_img, setting_camera)
                    st.session_state.camera_results[setting_camera]["result"] = refreshed
                    st.session_state.camera_results[setting_camera]["config_roi"] = tuple(CAMERA_CONFIG[setting_camera].get("roi", (0, 0, 0, 0)))
                    st.session_state.camera_results[setting_camera]["config_threshold"] = dict(CAMERA_CONFIG[setting_camera].get("threshold", {}))
                st.session_state.show_settings = True
                st.rerun()
    with close_col:
        if st.button("✕ ปิดการตั้งค่า", use_container_width=True, key="close_camera_config"):
            st.session_state.show_settings = False
            st.rerun()

    st.divider()


# =====================================================
# HEADER

header_left, header_actions = st.columns(
    [0.68, 0.32],
    vertical_alignment="center"
)

header_settings, header_theme, header_help = header_actions.columns(
    [0.85, 2.7, 0.85],
    vertical_alignment="center"
)

with header_left:
    st.markdown(
        '<div class="app-brand">'
        '<div class="app-brand-icon">🗑️</div>'
        '<div>'
        '<div class="app-title">ระบบตรวจสอบปริมาณขยะด้วย AI</div>'
        '<div class="app-subtitle">YOLOv11-Seg · Waste Area Ratio (WAR)</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

with header_settings:
    if st.button(
        "⚙️",
        key="header_settings",
        help="ตั้งค่า ROI และเกณฑ์ระดับความหนาแน่น"
    ):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()

with header_theme:
    st.toggle(
        "🌙 โหมดมืด",
        key="theme_dark_mode",
        help="สลับระหว่างโหมดสว่างและโหมดมืด",
        label_visibility="visible"
    )

with header_help:
    with st.popover("❔", use_container_width=False):
        st.markdown("### วิธีใช้งานระบบ")
        st.markdown(
            "**1. อัปโหลดภาพ**  \n"
          
