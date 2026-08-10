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

from inference import analyze_frame
from config import CAMERA_CONFIG




# =====================================================
# FULLSCREEN IMAGE VIEWER
# =====================================================

def show_image_viewer(img_bgr, title="", display_width=400, viewer_height=300):
    """
    แสดงภาพตามสัดส่วนจริง ไม่มีแถบดำบน-ล่าง
    และสามารถเปิดภาพเต็มหน้าจอด้วย Fullscreen API
    """
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
                    "IBM Plex Sans Thai",
                    "Noto Sans Thai",
                    Arial,
                    sans-serif;
            }}

            .viewer {{
                position: relative;
                width: min(100%, {display_width}px);
                aspect-ratio: {w} / {h};
                margin: 0 auto;
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

        <div
            class="viewer"
            id="viewer"
            title="ดับเบิลคลิกเพื่อขยายภาพ"
        >

            <button
                class="zoom-btn"
                id="zoom"
            >
                ⛶ ขยายภาพ
            </button>

            <img
                src="data:image/jpeg;base64,{image_b64}"
                alt="{title}"
            >

        </div>

        <script>

            const viewer =
                document.getElementById("viewer");

            const zoom =
                document.getElementById("zoom");


            async function toggleFullscreen() {{

                try {{

                    if (!document.fullscreenElement) {{

                        await viewer.requestFullscreen();

                    }} else {{

                        await document.exitFullscreen();

                    }}

                }} catch (error) {{

                    console.log(
                        "Fullscreen unavailable:",
                        error
                    );

                }}

            }}


            zoom.addEventListener(
                "click",
                function(event) {{

                    event.stopPropagation();

                    toggleFullscreen();

                }}
            );


            viewer.addEventListener(
                "dblclick",
                function(event) {{

                    if (event.target !== zoom) {{

                        toggleFullscreen();

                    }}

                }}
            );


            document.addEventListener(
                "fullscreenchange",
                function() {{

                    zoom.textContent =
                        document.fullscreenElement
                        ? "⛶ ออกจากเต็มหน้าจอ"
                        : "⛶ ขยายภาพ";

                }}
            );

        </script>

    </body>
    </html>
    """

    components.html(
        html,
        height=aspect_height + 12,
        scrolling=False
    )


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(

    page_title="ระบบตรวจสอบขยะด้วย AI",

    layout="wide"

)



# =====================================================
# LEVEL CONFIG
# =====================================================

LEVEL_INFO = {

    "Normal": {

        "name":"Normal (ไม่มีขยะ)",

        "color":"#4CAF50",

        "action":"ไม่พบขยะ"

    },


    "Low": {

        "name":"Low (ต่ำ)",

        "color":"#2196F3",

        "action":"เฝ้าระวังพื้นที่"

    },


    "Medium": {

        "name":"Medium (ปานกลาง)",

        "color":"#FFD600",

        "action":"เตรียมวางแผนเก็บขยะ"

    },


    "High": {

        "name":"High (สูง)",

        "color":"#FF9800",

        "action":"แจ้งเตือนเจ้าหน้าที่"

    },


    "Critical": {

        "name":"Critical (วิกฤต)",

        "color":"#F44336",

        "action":"แจ้งเตือนด่วนและดำเนินการเก็บขยะทันที"

    }

}




# =====================================================
# CSS SMALL UI
# =====================================================

st.markdown(

"""
<style>

@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');

:root {
    --ink: #172033;
    --muted: #667085;
    --line: #e5eaf1;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
button, input, textarea, select {
    font-family: 'IBM Plex Sans Thai', 'Noto Sans Thai', Tahoma, sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 85% 0%, rgba(49,91,138,.05), transparent 30%),
        #fff;
    color: var(--ink);
    font-size: 14px;
}

.block-container {
    max-width: 1380px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
}

h1 {
    font-size: 30px !important;
    line-height: 1.25 !important;
    letter-spacing: -.02em;
    color: var(--ink) !important;
}

h2 { font-size: 21px !important; color: var(--ink) !important; }
h3 { font-size: 16px !important; color: var(--ink) !important; }

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
}

[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Sans Thai', 'Noto Sans Thai', Tahoma, sans-serif !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Sans Thai', 'Noto Sans Thai', Tahoma, sans-serif !important;
    font-size: 12px !important;
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

[data-testid="stExpander"] {
    border: 1px solid var(--line) !important;
    border-radius: 11px !important;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(15,23,42,.025);
}

[data-testid="stExpander"] summary { font-size: 12px !important; }

.stButton > button {
    border-radius: 9px !important;
    border: 1px solid #d7dee8 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    min-height: 38px !important;
}

.stButton > button:hover { border-color: #9eb4cd !important; }

[data-testid="stPopover"] button {
    border-radius: 9px !important;
    min-height: 34px !important;
    width: 34px !important;
    padding: 0 !important;
}

[data-testid="stImage"] img { border-radius: 9px; }

section[data-testid="stSidebar"] { border-right: 1px solid #e7ebf0; }

/* Collection */
.collection-section {
    margin-top: 10px;
    padding: 18px 16px 17px;
    border-radius: 18px;
    background: linear-gradient(180deg,#f8fafc 0%,#f1f5f9 100%);
    border: 1px solid #dfe6ee;
    box-shadow: 0 7px 22px rgba(15,23,42,.045);
    overflow: hidden;
}

.collection-title {
    text-align: center;
    font-size: 22px;
    font-weight: 700;
    color: #23344d;
    margin-bottom: 3px;
}

.collection-subtitle {
    text-align: center;
    color: #6b7789;
    font-size: 12px;
    margin-bottom: 15px;
}

.collection-road {
    position: relative;
    height: 106px;
    margin: 0 8px 16px;
    border-radius: 18px;
    background: linear-gradient(180deg,#4b5563 0%,#364152 100%);
    box-shadow: inset 0 4px 12px rgba(0,0,0,.18), 0 5px 14px rgba(15,23,42,.08);
    overflow: hidden;
}

.collection-road::before {
    content:'';
    position:absolute;
    left:0; right:0; top:54%;
    height:4px;
    transform:translateY(-50%);
    background:repeating-linear-gradient(90deg,#f8fafc 0 40px,transparent 40px 68px);
    opacity:.92;
}

.collection-road::after {
    content:'→  เส้นทางการจัดเก็บขยะ  →';
    position:absolute;
    left:50%; bottom:8px;
    transform:translateX(-50%);
    color:rgba(255,255,255,.78);
    font-size:11px;
    font-weight:600;
    white-space:nowrap;
}

.collection-truck {
    position:absolute;
    top:24px; left:1.5%;
    font-size:36px;
    z-index:5;
    filter:drop-shadow(0 4px 3px rgba(0,0,0,.28));
    animation:collectionDriveOneWay 10s linear infinite;
}

@keyframes collectionDriveOneWay {
    0% { left:1.5%; transform:translateX(0); }
    100% { left:96%; transform:translateX(-100%); }
}

.collection-checkpoints {
    position:absolute;
    left:3%; right:3%; top:31px;
    height:45px;
    z-index:2;
    display:flex;
    align-items:center;
    justify-content:space-between;
}

.collection-checkpoint {
    position:relative;
    width:28px; height:28px;
    border-radius:50%;
    border:4px solid #fff;
    box-shadow:0 2px 7px rgba(0,0,0,.28);
}

.collection-checkpoint-label {
    position:absolute;
    top:31px; left:50%;
    transform:translateX(-50%);
    color:#fff;
    font-size:10px;
    font-weight:700;
    white-space:nowrap;
    text-shadow:0 1px 2px rgba(0,0,0,.65);
}

.collection-arrow {
    position:absolute;
    top:43px; left:0; right:0;
    text-align:center;
    color:#fff;
    font-size:20px;
    opacity:.88;
}

.collection-stops {
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(205px,1fr));
    gap:10px;
}

.collection-stop {
    position:relative;
    background:#fff;
    border:1px solid #e2e8f0;
    border-radius:12px;
    padding:11px 12px;
    box-shadow:0 2px 8px rgba(15,23,42,.045);
}

.collection-rank {
    position:absolute;
    top:9px; right:10px;
    width:28px; height:28px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#fff;
    font-weight:700;
    font-size:12px;
}

.collection-camera {
    font-size:13px;
    font-weight:700;
    color:#1f2937;
    padding-right:34px;
}

.collection-war {
    font-size:19px;
    font-weight:700;
    color:#111827;
    margin-top:5px;
}

.collection-level {
    font-size:12px;
    color:#667085;
    margin-top:2px;
}

.collection-detail {
    font-size:11px;
    color:#7a8492;
    margin-top:6px;
    line-height:1.5;
}

.collection-note {
    margin-top:13px;
    text-align:center;
    font-size:11px;
    color:#7a8492;
}

@media (max-width:800px) {
    .block-container {
        padding-left:1rem !important;
        padding-right:1rem !important;
    }
    .collection-road {
        margin-left:0;
        margin-right:0;
    }
    .collection-checkpoint-label { font-size:9px; }
}

/* Modern dashboard header */
.app-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    min-height: 58px;
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
    font-size: 28px;
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

/* Soft interactive lift */
.collection-stop {
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.collection-stop:hover {
    transform: translateY(-2px);
    border-color: #cbd8e8;
    box-shadow: 0 8px 20px rgba(15,23,42,.08);
}

[data-testid="stMetric"] {
    transition: transform .18s ease, box-shadow .18s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(15,23,42,.07);
}

[data-testid="stPopover"] > div {
    border-radius: 12px !important;
}

/* Make the truck face right without reversing its travel animation */
.collection-truck span {
    display: inline-block;
    transform: scaleX(-1);
    transform-origin: center;
}

</style>
""",

unsafe_allow_html=True

)





# =====================================================
# SESSION
# =====================================================

if "camera_results" not in st.session_state:

    st.session_state.camera_results = {}



if "history" not in st.session_state:

    st.session_state.history = {}



if "selected_history" not in st.session_state:

    st.session_state.selected_history = None




for cam in CAMERA_CONFIG:

    if cam not in st.session_state.history:

        st.session_state.history[cam] = []



# =====================================================
# การตั้งค่า ROI และ Threshold จากหน้าเว็บ
# =====================================================

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# ค่าเริ่มต้นของ ROI และ Threshold จะอ่านจาก config.py โดยตรง
# ดังนั้นเมื่อเปิด session ใหม่ หน้าเว็บจะใช้ค่าที่กำหนดไว้ใน config.py เป็น default
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


if st.session_state.show_settings:
    st.markdown("### ⚙️ ตั้งค่า ROI และระดับความหนาแน่น")
    st.caption("แก้ค่าแยกตามกล้องได้จากหน้านี้ ค่าใหม่จะใช้กับการวิเคราะห์ครั้งถัดไป")

    setting_camera = st.selectbox("เลือกกล้อง", list(CAMERA_CONFIG.keys()), key="setting_camera")
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

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        new_x1 = st.number_input("X1", min_value=0, max_value=max(0, image_w - 1), value=min(max(0, int(current_roi[0])), max(0, image_w - 1)), step=1, key=f"roi_x1_{setting_camera}")
    with r2:
        new_y1 = st.number_input("Y1", min_value=0, max_value=max(0, image_h - 1), value=min(max(0, int(current_roi[1])), max(0, image_h - 1)), step=1, key=f"roi_y1_{setting_camera}")
    with r3:
        new_x2 = st.number_input("X2", min_value=1, max_value=max(1, image_w), value=min(max(1, int(current_roi[2])), max(1, image_w)), step=1, key=f"roi_x2_{setting_camera}")
    with r4:
        new_y2 = st.number_input("Y2", min_value=1, max_value=max(1, image_h), value=min(max(1, int(current_roi[3])), max(1, image_h)), step=1, key=f"roi_y2_{setting_camera}")

    st.markdown("**เกณฑ์ระดับความหนาแน่น (%)**")
    t1, t2, t3 = st.columns(3)
    with t1:
        new_low = st.number_input("Low ถึง", min_value=0.0, max_value=100.0, value=float(current_threshold["low"]), step=0.1, key=f"threshold_low_{setting_camera}")
    with t2:
        new_medium = st.number_input("Medium ถึง", min_value=0.0, max_value=100.0, value=float(current_threshold["medium"]), step=0.1, key=f"threshold_medium_{setting_camera}")
    with t3:
        new_high = st.number_input("High ถึง", min_value=0.0, max_value=100.0, value=float(current_threshold["high"]), step=0.1, key=f"threshold_high_{setting_camera}")


    apply_current = st.checkbox(
        "วิเคราะห์ภาพล่าสุดของกล้องนี้ใหม่ทันทีหลังบันทึก",
        value=False,
        key=f"reanalyze_{setting_camera}"
    )

    reset_roi_col, reset_threshold_col = st.columns(2)

    with reset_roi_col:
        if st.button(
            "↩️ ROI กลับค่าเริ่มต้น",
            use_container_width=True,
            key=f"reset_roi_{setting_camera}",
            help="คืนค่า ROI ของกล้องนี้ตาม config.py"
        ):
            restore_camera_default(
                setting_camera,
                restore_roi=True,
                restore_threshold=False
            )

            # คืนค่าของ number_input ใน session state ด้วย
            default_roi = st.session_state.default_camera_config[setting_camera]["roi"]

            st.session_state[f"roi_x1_{setting_camera}"] = int(default_roi[0])
            st.session_state[f"roi_y1_{setting_camera}"] = int(default_roi[1])
            st.session_state[f"roi_x2_{setting_camera}"] = int(default_roi[2])
            st.session_state[f"roi_y2_{setting_camera}"] = int(default_roi[3])

            st.rerun()

    with reset_threshold_col:
        if st.button(
            "↩️ Threshold กลับค่าเริ่มต้น",
            use_container_width=True,
            key=f"reset_threshold_{setting_camera}",
            help="คืนค่า Threshold ของกล้องนี้ตาม config.py"
        ):
            restore_camera_default(
                setting_camera,
                restore_roi=False,
                restore_threshold=True
            )

            default_threshold = st.session_state.default_camera_config[setting_camera]["threshold"]

            st.session_state[f"threshold_low_{setting_camera}"] = float(default_threshold["low"])
            st.session_state[f"threshold_medium_{setting_camera}"] = float(default_threshold["medium"])
            st.session_state[f"threshold_high_{setting_camera}"] = float(default_threshold["high"])

            st.rerun()

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
# =====================================================

header_left, header_settings, header_help = st.columns(
    [0.82, 0.09, 0.09],
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

with header_help:
    with st.popover("❔", use_container_width=False):
        st.markdown("### วิธีใช้งานระบบ")
        st.markdown(
            "**1. อัปโหลดภาพ**  \n"
            "เลือกภาพจากกล้อง CCTV ในแถบด้านซ้าย"
        )
        st.markdown(
            "**2. ตรวจผล AI**  \n"
            "ระบบจะแสดง ROI, Mask, WAR, ระดับขยะ และคำแนะนำ"
        )
        st.markdown(
            "**3. ดูประวัติ**  \n"
            "เปิดรายการ History เพื่อดูผลของแต่ละครั้ง"
        )
        st.markdown(
            "**4. ดูกราฟ WAR**  \n"
            "ใช้กราฟติดตามแนวโน้มของแต่ละกล้อง"
        )
        st.markdown(
            "**5. ตั้งค่า**  \n"
            "กด ⚙️ เพื่อปรับ ROI และ Threshold ได้ตามกล้อง"
        )
        st.caption("คำแนะนำ: ตั้ง ROI ให้ครอบคลุมเฉพาะพื้นที่ที่ต้องการวัด")

st.markdown(
    '<div class="header-divider"></div>',
    unsafe_allow_html=True
)
# =====================================================
# UPLOAD CCTV IMAGE
# =====================================================

st.sidebar.header(
    "📷 อัปโหลดภาพจากกล้อง CCTV"
)



for cam in CAMERA_CONFIG:


    uploaded_file = st.sidebar.file_uploader(

        cam,

        type=[

            "jpg",
            "jpeg",
            "png"

        ],

        key=cam

    )



    if uploaded_file is not None:


        file_id = (

            uploaded_file.name,

            uploaded_file.size

        )



        old_file = (

            st.session_state.camera_results

            .get(cam, {})

            .get("file_id")

        )



        if file_id != old_file:



            bytes_data = np.asarray(

                bytearray(

                    uploaded_file.read()

                ),

                dtype=np.uint8

            )



            img = cv2.imdecode(

                bytes_data,

                cv2.IMREAD_COLOR

            )



            result = analyze_frame(

                img,

                cam

            )




            st.session_state.camera_results[cam] = {
                "file_id": file_id,
                "original": img,
                "result": result,
                "config_roi": tuple(CAMERA_CONFIG[cam].get("roi", (0, 0, 0, 0))),
                "config_threshold": dict(CAMERA_CONFIG[cam].get("threshold", {})),
            }




            history_id = len(

                st.session_state.history[cam]

            )




            st.session_state.history[cam].append({


                "ID":

                history_id,


                "เวลา":

                datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                ),


                "ภาพ":

                img.copy(),


                "ผล":

                result["image"].copy(),


                "WAR":

                result["WAR"],


                "เปลี่ยนแปลง":

                result["change"],


                "ระดับ":

                result["level"]

            })







# =====================================================
# DISPLAY CAMERA
# =====================================================

for cam, data in st.session_state.camera_results.items():


    result = data["result"]


    level = result["level"]


    info = LEVEL_INFO[level]



    st.divider()



    st.header(

        f"📷 {cam}"

    )





    # =========================
    # LEVEL
    # =========================

    st.markdown(
        f'<div style="background-color:{info["color"]}; padding:8px 12px; border-radius:8px; font-size:14px; font-weight:600; margin-bottom:6px;">'
        f'ระดับความหนาแน่นของขยะ<br>{info["name"]}'
        f'</div>',
        unsafe_allow_html=True
    )





    # =========================
    # ACTION
    # =========================

    st.markdown(

        f"""

        <div class="recommend">

        <b>คำแนะนำ:</b>

        {info['action']}

        </div>


        """,

        unsafe_allow_html=True

    )







    # =========================
    # IMAGE
    # =========================

    c1,c2 = st.columns(2)



    with c1:


        st.subheader(

            "ภาพจากกล้อง"

        )


        show_image_viewer(
            data["original"],
            title="ภาพจากกล้อง",
            display_width=400
        )





    with c2:


        st.subheader(

            "ผล Segmentation"

        )


        show_image_viewer(
            result["image"],
            title="ผล Segmentation",
            display_width=400
        )






    # =========================
    # CURRENT RESULT
    # =========================

    st.subheader(

        "📊 ผลการวิเคราะห์"

    )



    a,b,c = st.columns(3)



    a.metric(

        "WAR",

        f'{result["WAR"]}%'

    )


    b.metric(

        "เปลี่ยนแปลง",

        f'{result["change"]:+.2f}%'

    )


    c.metric(

        "ระดับ",

        info["name"]

    )






    # =========================
    # GRAPH
    # =========================

    war_title_col, war_info_col = st.columns(
        [0.94, 0.06],
        vertical_alignment="center"
    )

    with war_title_col:
        st.subheader(
            f"📈 แนวโน้ม WAR : {cam}"
        )

    with war_info_col:
        with st.popover("ⓘ"):
            st.markdown("### WAR คืออะไร?")
            st.write(
                "WAR (Waste Area Ratio) คือสัดส่วนพื้นที่พิกเซลขยะ "
                "ภายใน ROI เมื่อเทียบกับพื้นที่ ROI ทั้งหมด"
            )
            st.latex(
                r"WAR = \frac{\text{พิกเซลขยะใน ROI}}{\text{พื้นที่ ROI}} \times 100"
            )
            st.markdown(
                "**ตัวอย่าง** 25 px จาก ROI 100 px → WAR = 25%"
            )
            st.caption(
                "WAR ใช้เปรียบเทียบความหนาแน่นของขยะภายในพื้นที่ ROI ของแต่ละกล้อง"
            )



    if len(st.session_state.history[cam]) > 0:


        graph_data = pd.DataFrame(

            st.session_state.history[cam]

        )



        fig = px.line(

            graph_data,

            x="เวลา",

            y="WAR",

            markers=True,

            title=None

        )


        fig.update_layout(

            height=180,

            margin=dict(

                l=20,

                r=20,

                t=20,

                b=20

            )

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )
        # =========================
        # SELECTED GRAPH DATA
        # =========================

        if st.session_state.selected_history is not None:


            item = st.session_state.selected_history


            st.subheader(

                "🔎 ข้อมูลที่เลือกจากกราฟ"

            )



            x,y,z = st.columns(3)



            x.metric(

                "WAR",

                f'{item["WAR"]}%'

            )



            y.metric(

                "เปลี่ยนแปลง",

                f'{item["เปลี่ยนแปลง"]:+.2f}%'

            )



            selected_info = LEVEL_INFO[

                item["ระดับ"]

            ]



            z.metric(

                "ระดับ",

                selected_info["name"]

            )





            show_image_viewer(
                item["ผล"],
                title="ผล Segmentation จากข้อมูลที่เลือก",
                display_width=400
            )







    # =================================================
    # HISTORY
    # =================================================

    st.subheader(

        f"📋 ประวัติการตรวจสอบ {cam}"

    )



    histories = st.session_state.history[cam]



    if len(histories) == 0:
        pass

    else:


        for item in reversed(histories):


            history_info = LEVEL_INFO[

                item["ระดับ"]

            ]



            with st.expander(

                f'#{item["ID"]+1} | '

                f'{item["เวลา"]} | '

                f'{history_info["name"]}'

            ):



                # -------------------------
                # LEVEL
                # -------------------------

                st.markdown(
                    f'<div style="background-color:{history_info["color"]}; padding:8px 12px; border-radius:8px; font-size:14px; font-weight:600; margin-bottom:6px;">'
                    f'{history_info["name"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )





                # -------------------------
                # DATA
                # -------------------------

                a,b,c = st.columns(3)



                a.metric(

                    "WAR",

                    f'{item["WAR"]}%'

                )


                b.metric(

                    "เปลี่ยนแปลง",

                    f'{item["เปลี่ยนแปลง"]:+.2f}%'

                )


                c.metric(

                    "ระดับ",

                    history_info["name"]

                )







                # -------------------------
                # IMAGES
                # -------------------------

                h1,h2 = st.columns(2)



                with h1:


                    show_image_viewer(
                        item["ภาพ"],
                        title="ภาพต้นฉบับ",
                        display_width=330
                    )





                with h2:


                    show_image_viewer(
                        item["ผล"],
                        title="ผล Segmentation",
                        display_width=330
                    )

# =====================================================
# ลำดับการจัดเก็บขยะ
# =====================================================

LEVEL_ORDER = {
    "Normal": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4,
}

collection_priority = []
reference_roi_area = 0

for cam, data in st.session_state.camera_results.items():
    result = data.get("result", {})
    cfg = CAMERA_CONFIG.get(cam, {})
    roi = data.get("config_roi", cfg.get("roi", (0, 0, 0, 0)))

    try:
        x1, y1, x2, y2 = [int(v) for v in roi]
        roi_area = max(0, x2 - x1) * max(0, y2 - y1)
    except (TypeError, ValueError):
        roi_area = 0

    garbage_mask = result.get("mask")
    garbage_pixels = int(np.sum(np.asarray(garbage_mask) > 0)) if garbage_mask is not None else 0

    level = result.get("level", "Normal")
    war = float(result.get("WAR", 0))
    reference_roi_area = max(reference_roi_area, roi_area)

    collection_priority.append({
        "camera": cam,
        "WAR": war,
        "level": level,
        "level_rank": LEVEL_ORDER.get(level, 0),
        "roi_area": roi_area,
        "garbage_pixels": garbage_pixels,
    })

for item in collection_priority:
    if item["roi_area"] > 0 and reference_roi_area > 0:
        item["normalized_garbage_pixels"] = item["garbage_pixels"] * reference_roi_area / item["roi_area"]
    else:
        item["normalized_garbage_pixels"] = 0.0

collection_priority.sort(
    key=lambda item: (item["normalized_garbage_pixels"], item["level_rank"]),
    reverse=True
)

collection_title_col, collection_info_col = st.columns(
    [0.94, 0.06],
    vertical_alignment="center"
)

with collection_title_col:
    st.markdown(
        '<div class="collection-title">🚛 ลำดับการจัดเก็บขยะ</div>'
        '<div class="collection-subtitle">รถเก็บขยะเดินทางทางเดียวจากจุดที่ควรจัดเก็บก่อน → จุดที่ควรจัดเก็บภายหลัง</div>',
        unsafe_allow_html=True
    )

with collection_info_col:
    with st.popover("ⓘ"):
        st.markdown("### วิธีเรียงลำดับการจัดเก็บ")
        st.write(
            "ระบบใช้ **พื้นที่ขยะหลังปรับ ROI ให้เทียบกับพื้นที่อ้างอิง** "
            "เป็นตัวหลักในการจัดลำดับ"
        )

        st.markdown("**ลำดับการพิจารณา**")
        st.markdown(
            "1. หาพิกเซลขยะที่อยู่ใน ROI ของแต่ละกล้อง\n"
            "2. ปรับเทียบพื้นที่ ROI ให้มีขนาดอ้างอิงเดียวกัน\n"
            "3. เปรียบเทียบพื้นที่ขยะหลังปรับ — มากกว่าจัดเก็บก่อน\n"
            "4. หากพื้นที่ขยะใกล้เคียงกัน จึงใช้ระดับความหนาแน่นเป็นตัวช่วย"
        )

        st.markdown("**ตัวอย่างการปรับ ROI**")
        st.code(
            "กล้อง A : 5 / 50 → 5 / 50\n"
            "กล้อง B : 1 / 2  → 25 / 50\n"
            "ดังนั้น B มีพื้นที่ขยะเทียบเท่ามากกว่า → จัดเก็บก่อน",
            language="text"
        )

        st.caption(
            "รถเก็บขยะวิ่งตาม checkpoint จากอันดับ 1 → อันดับสุดท้าย"
        )

if len(collection_priority) == 0:
    st.info("ยังไม่มีข้อมูลจากกล้องสำหรับจัดลำดับการจัดเก็บขยะ")
else:
    checkpoint_html = []
    for rank, item in enumerate(collection_priority, start=1):
        info = LEVEL_INFO.get(item["level"], LEVEL_INFO["Normal"])
        checkpoint_html.append(
            f'<div class="collection-checkpoint" style="background:{info["color"]};">'
            f'<span class="collection-checkpoint-label">{rank}. {item["camera"]}</span>'
            f'</div>'
        )

    road_html = (
        '<div class="collection-road">'
        '<div class="collection-checkpoints">' + ''.join(checkpoint_html) + '</div>'
        '<div class="collection-arrow">→</div>'
        '<div class="collection-truck"><span>🚛</span></div>'
        '</div>'
    )
    st.markdown(road_html, unsafe_allow_html=True)

    cards = []
    for rank, item in enumerate(collection_priority, start=1):
        info = LEVEL_INFO.get(item["level"], LEVEL_INFO["Normal"])
        cards.append(
            f'<div class="collection-stop">'
            f'<div class="collection-rank" style="background:{info["color"]};">{rank}</div>'
            f'<div class="collection-camera">📷 {item["camera"]}</div>'
            f'<div class="collection-war">WAR {item["WAR"]:.2f}%</div>'
            f'<div class="collection-level">{info["name"]}</div>'
            f'<div class="collection-detail">ขยะจริง: {item["garbage_pixels"]:,} px<br>ROI: {item["roi_area"]:,} px<br>ขยะเทียบ ROI อ้างอิง: {item["normalized_garbage_pixels"]:,.1f} px</div>'
            f'</div>'
        )

    st.markdown('<div class="collection-stops">' + ''.join(cards) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="collection-note">อันดับ 1 คือ checkpoint แรกของเส้นทาง และรถจะวิ่งต่อไปตามลำดับจนถึง checkpoint สุดท้าย</div>', unsafe_allow_html=True)


