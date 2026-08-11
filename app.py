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

def show_image_viewer(img_bgr, title="", display_width=340, viewer_height=300):
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
                    "Prompt",
                    "Noto Sans Thai",
                    Tahoma,
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
        
/* Camera dropdown header */

div[data-testid="stButton"] > button[kind="secondary"] {{
    min-height: 46px !important;
    border: 1px solid #d9e2ec !important;
    border-radius: 13px !important;
    background: #ffffff !important;
    box-shadow: 0 4px 14px rgba(15,23,42,.05) !important;
    padding: 8px 13px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
}}

div[data-testid="stButton"] > button[kind="secondary"]:hover {{
    transform: translateY(-1px);
    border-color: #b9c9d9 !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.09) !important;
}}

div[data-testid="stButton"] > button[kind="secondary"] p {{
    margin: 0 !important;
    font-size: 13px !important;
    font-weight: 650 !important;
    color: #172033 !important;
    line-height: 1.45 !important;
    text-align: left !important;
}}

.camera-detail-card {{
    margin: -1px 0 14px;
    padding: 14px;
    border: 1px solid #e0e7ef;
    border-top: 0;
    border-radius: 0 0 15px 15px;
    background: #ffffff;
    box-shadow: 0 8px 22px rgba(15,23,42,.055);
}}

/* Camera result widgets */
[data-testid="stExpander"] {{
    border: 1px solid #d9e2ec !important;
    border-radius: 16px !important;
    background: #ffffff !important;
    box-shadow: 0 5px 18px rgba(15,23,42,.055) !important;
    overflow: hidden !important;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}}
[data-testid="stExpander"]:hover {{
    transform: translateY(-1px);
    border-color: #c7d5e4 !important;
    box-shadow: 0 10px 26px rgba(15,23,42,.09) !important;
}}
[data-testid="stExpander"] summary {{
    min-height: 50px !important;
    padding: 9px 14px !important;
    background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%) !important;
}}
[data-testid="stExpander"] summary:hover {{
    background: #f7faff !important;
}}
[data-testid="stExpander"] summary p {{
    margin: 0 !important;
    font-size: 13px !important;
    font-weight: 650 !important;
    line-height: 1.45 !important;
    color: #172033 !important;
}}
.camera-status {{
    padding: 9px 12px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 650;
    margin: 2px 0 7px;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.18);
}}
.camera-action {{
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background: #f8fafc;
    color: #344054;
    font-size: 11px;
    line-height: 1.55;
    margin-bottom: 8px;
}}
.camera-action b {{ color: #172033; }}
.camera-image-title {{
    font-size: 13px;
    font-weight: 650;
    color: #172033;
    margin: 2px 0 3px;
}}
[data-testid="stExpander"] [data-testid="stHorizontalBlock"] {{
    gap: 0.7rem !important;
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

        "action":"แจ้งเจ้าหน้าที่และดำเนินการเก็บขยะด่วน"

    }

}




# =====================================================
# CSS SMALL UI
# =====================================================

st.markdown(

"""
<style>

@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');

/* Hide Streamlit top chrome / toolbar */
[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

#MainMenu {
    visibility: hidden !important;
}

footer {
    visibility: hidden !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

:root {
    --ink: #172033;
    --muted: #667085;
    --line: #e5eaf1;
    --accent: #315b8a;
    --accent-soft: #edf4fb;
}

@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
button, input, textarea, select,
[data-testid="stMarkdownContainer"],
[data-testid="stMetric"],
[data-testid="stExpander"] {
    font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
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
    padding-top: 1.2rem !important;
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
.stButton > button {
    white-space: nowrap !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
}


[data-testid="stImage"] img { border-radius: 9px; }

section[data-testid="stSidebar"] { border-right: 1px solid #e7ebf0; }

/* History density badge */
.history-density-badge {
    display:block;
    width:100%;
    padding:7px 10px;
    margin:0 0 10px;
    border-radius:9px;
    font-size:12px;
    font-weight:700;
    box-sizing:border-box;
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

div[data-testid="stNumberInput"] input {
    border-radius: 9px !important;
    border: 1px solid #dce3ec !important;
    background: #fff !important;
}

div[data-testid="stNumberInput"] label {
    font-size: 11px !important;
    color: #667085 !important;
}

/* Modern micro-interactions */
.stButton > button,
[data-testid="stFileUploader"],
[data-testid="stMetric"],
[data-testid="stExpander"],
.collection-stop {
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(49,91,138,.10);
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(15,23,42,.07);
}

[data-testid="stFileUploader"] {
    border: 1px solid #dfe6ee !important;
    border-radius: 14px !important;
    padding: 10px !important;
    background: #fbfcfe !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #b8c9dc !important;
    box-shadow: 0 7px 18px rgba(49,91,138,.08);
}

[data-testid="stFileUploaderDropzone"] {
    border-radius: 11px !important;
    background: linear-gradient(180deg,#ffffff 0%,#f7faff 100%) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
    border-radius: 14px !important;
    border: 1px solid #dfe6ee !important;
    background: #fbfcfe !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
    background: #f4f8fc !important;
}

.section-title {
    font-size:16px;
    font-weight:700;
    color:#172033;
    margin:3px 0 4px;
}

.upload-camera-label {
    display:flex; align-items:center; justify-content:space-between;
    gap:8px; margin:8px 0 6px; color:var(--ink);
    font-size:13px; font-weight:600;
}

.upload-hint {
    color:var(--muted); font-size:11px; line-height:1.5; margin:0 0 8px;
}

.upload-panel-title { font-size:16px; font-weight:700; color:var(--ink); margin-bottom:2px; }
.upload-panel-subtitle { color:var(--muted); font-size:11px; line-height:1.5; margin-bottom:10px; }

[data-testid="stExpander"] {
    border: 1px solid #dfe6ee !important;
    border-radius: 14px !important;
    background: #ffffff !important;
    box-shadow: 0 4px 14px rgba(15,23,42,.035);
    transition: box-shadow .18s ease, border-color .18s ease;
}

[data-testid="stExpander"]:hover {
    border-color: #cbd8e6 !important;
    box-shadow: 0 7px 18px rgba(49,91,138,.07);
}

[data-testid="stExpander"] summary {
    min-height: 42px !important;
    font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
    font-weight: 600 !important;
    color: #172033 !important;
}

[data-testid="stExpander"] summary:hover {
    background: #f7faff !important;
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
    list-style:none; cursor:pointer; width:34px; height:34px; display:grid; place-items:center;
    border:1px solid #d7dee8; border-radius:10px; color:#344054; background:#fff;
    transition:transform .18s ease, box-shadow .18s ease, background .18s ease;
}
.collection-info summary::-webkit-details-marker { display:none; }
.collection-info summary:hover { transform:translateY(-1px); background:#f7faff; box-shadow:0 5px 14px rgba(49,91,138,.10); }
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
}
.collection-stop:hover { transform:translateY(-3px); border-color:#c9d7e6; box-shadow:0 10px 22px rgba(15,23,42,.08); }
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
@media (max-width:700px) {
    .collection-section { padding:13px; }
    .collection-title { font-size:18px; }
    .collection-road { height:112px; }
    .collection-stops { grid-template-columns:1fr; }
}

/* Modern dashboard header */
.block-container {
    max-width: 1180px !important;
    padding-top: 1.15rem !important;
    padding-bottom: 1.8rem !important;
}

[data-testid="stVerticalBlock"] { gap: 0.5rem; }

h1, h2, h3, h4, p, label {
    font-family: 'Prompt', 'Noto Sans Thai', Tahoma, sans-serif !important;
}
h1 { font-size: 1.55rem !important; }
h2 { font-size: 1.28rem !important; }
h3 { font-size: 1.08rem !important; }

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
[data-testid="stPopover"] [data-testid="stMarkdownContainer"] {
    font-size: 12px !important;
    line-height: 1.5 !important;
}
[data-testid="stPopover"] h3,
[data-testid="stPopover"] h2 { font-size: 15px !important; }
[data-testid="stMetricValue"] { font-size: 1.35rem !important; }
[data-testid="stMetricLabel"] { font-size: 11px !important; }

/* Make the truck face right without reversing its travel animation */
.collection-truck span {
    display: inline-block;
    transform: scaleX(-1);
    transform-origin: center;
}

@media (max-width: 800px) {
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
    }

    [data-testid="stPopover"] button {
        min-width: 88px !important;
        padding: 0 8px !important;
    }
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

if "selected_history_camera" not in st.session_state:
    st.session_state.selected_history_camera = None




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
# =====================================================

header_left, header_actions = st.columns(
    [0.74, 0.26],
    vertical_alignment="center"
)

header_settings, header_help = header_actions.columns(
    [1, 1],
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
            "เปิดหัวข้อ 📷 อัปโหลดภาพ CCTV แล้วเลือกภาพของแต่ละกล้อง"
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
# UPLOAD PANEL
# =====================================================

with st.expander("📷  อัปโหลดภาพ CCTV", expanded=False):
    upload_columns = st.columns(len(CAMERA_CONFIG), gap="small")

    for upload_col, cam in zip(upload_columns, CAMERA_CONFIG):
        with upload_col:
            st.markdown(
                f'<div class="upload-camera-label"><span>📷 {cam}</span><span>JPG / PNG</span></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="upload-hint">ลากไฟล์มาวาง หรือกด Browse เพื่อเลือกภาพ</div>',
                unsafe_allow_html=True
            )

            uploaded_file = st.file_uploader(
                "เลือกภาพ",
                type=["jpg", "jpeg", "png"],
                key=cam,
                label_visibility="collapsed"
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




                    st.session_state.selected_history = None
                    st.session_state.selected_history_camera = cam

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
# UPLOAD CCTV IMAGE
# =====================================================


# =====================================================
# DISPLAY CAMERA
# =====================================================

for cam, data in st.session_state.camera_results.items():
    result = data["result"]
    level = result["level"]
    info = LEVEL_INFO[level]

    camera_open_key = f"camera_open_{cam}"
    if camera_open_key not in st.session_state:
        st.session_state[camera_open_key] = False

    arrow = "⌄" if st.session_state[camera_open_key] else "›"
    camera_summary = (
        f"{arrow}  📷  {cam}   ·   {info['name']}   ·   {info['action']}"
    )

    if st.button(
        camera_summary,
        key=f"camera_toggle_{cam}",
        use_container_width=True,
    ):
        st.session_state[camera_open_key] = not st.session_state[camera_open_key]
        st.rerun()

    if st.session_state[camera_open_key]:
            st.markdown('<div class="camera-detail-card">', unsafe_allow_html=True)

            st.markdown(
                f'<div class="camera-status" style="background:{info["color"]};'
                f'color:{"#172033" if level == "Medium" else "#ffffff"};">'
                f'ระดับความหนาแน่น: {info["name"]}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="camera-action"><b>คำแนะนำ:</b> {info["action"]}</div>',
                unsafe_allow_html=True
            )

            # =========================
            # IMAGE
            # =========================

            c1,c2 = st.columns(2)



            with c1:


                st.markdown(
                    '<div class="camera-image-title">ภาพจากกล้อง</div>',
                    unsafe_allow_html=True
                )


                show_image_viewer(
                    data["original"],
                    title="ภาพจากกล้อง",
                    display_width=340
                )





            with c2:


                st.markdown(
                    '<div class="camera-image-title">ผล Segmentation</div>',
                    unsafe_allow_html=True
                )


                show_image_viewer(
                    result["image"],
                    title="ผล Segmentation",
                    display_width=340
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
                    st.markdown("**WAR = (พิกเซลขยะใน ROI ÷ พื้นที่ ROI) × 100**")
                    st.caption("ตัวอย่าง: ขยะ 25 px จาก ROI 100 px → WAR = 25%")
                    st.caption("ใช้วัดสัดส่วนพื้นที่ขยะภายใน ROI ของกล้องนั้น")

            if len(st.session_state.history[cam]) > 0:
                graph_data = pd.DataFrame(st.session_state.history[cam]).reset_index(drop=True)
                graph_data["จุด"] = np.arange(len(graph_data))

                fig = px.line(
                    graph_data,
                    x="จุด",
                    y="WAR",
                    markers=True,
                    custom_data=["เวลา", "ระดับ", "เปลี่ยนแปลง"],
                )
                fig.update_traces(
                    line=dict(width=3, color="#315b8a"),
                    marker=dict(size=8, color="#ffffff", line=dict(width=3, color="#315b8a")),
                    hovertemplate=(
                        "<b>จุดตรวจ %{x}</b><br>"
                        "WAR: <b>%{y:.2f}%</b><br>"
                        "เวลา: %{customdata[0]}<br>"
                        "ระดับ: %{customdata[1]}<br>"
                        "เปลี่ยนแปลง: %{customdata[2]:+.2f}%<extra></extra>"
                    ),
                )

                current_thr = CAMERA_CONFIG.get(cam, {}).get("threshold", {})
                for key, color, label in [
                    ("low", "#4CAF50", "Low"),
                    ("medium", "#FFD600", "Medium"),
                    ("high", "#FF9800", "High"),
                ]:
                    if key in current_thr:
                        try:
                            y_value = float(current_thr[key])
                            fig.add_hline(
                                y=y_value,
                                line_width=1,
                                line_dash="dot",
                                line_color=color,
                                annotation_text=f"{label} {y_value:g}%",
                                annotation_position="top left",
                            )
                        except (TypeError, ValueError):
                            pass

                fig.update_layout(
                    height=285,
                    margin=dict(l=8, r=12, t=12, b=8),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="#fbfcfe",
                    hovermode="x unified",
                    font=dict(family="Prompt, Noto Sans Thai, sans-serif", size=11, color="#172033"),
                    showlegend=False,
                    xaxis=dict(title="ลำดับการบันทึก", tickmode="linear", dtick=1, showgrid=False, zeroline=False),
                    yaxis=dict(title="WAR (%)", ticksuffix="%", showgrid=True, gridcolor="#e8edf3", zeroline=False, rangemode="tozero"),
                )

                st.markdown(
                    '<div class="chart-tip">💡 คลิกจุดบนกราฟเพื่อดูภาพและข้อมูลของการบันทึกครั้งนั้นด้านล่าง</div>',
                    unsafe_allow_html=True
                )

                chart_event = st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"war_chart_{cam}",
                    on_select="rerun",
                    selection_mode="points",
                )

                try:
                    selection = getattr(chart_event, "selection", None)
                    if selection is None and isinstance(chart_event, dict):
                        selection = chart_event.get("selection")
                    points = getattr(selection, "points", None) if selection is not None else None
                    if points is None and isinstance(selection, dict):
                        points = selection.get("points", [])

                    if points:
                        first_point = points[0]
                        point_index = getattr(first_point, "point_index", None)
                        if point_index is None and isinstance(first_point, dict):
                            point_index = first_point.get("point_index")
                        if point_index is None:
                            point_index = getattr(first_point, "pointNumber", None)
                        if point_index is None and isinstance(first_point, dict):
                            point_index = first_point.get("pointNumber")

                        if point_index is not None:
                            point_index = int(point_index)
                            if 0 <= point_index < len(st.session_state.history[cam]):
                                st.session_state.selected_history = st.session_state.history[cam][point_index]
                except Exception:
                    pass

                # =========================
                # SELECTED GRAPH DATA
                # =========================

                if st.session_state.selected_history is not None:


                    item = st.session_state.selected_history


                    st.subheader(

                        "🔎 ข้อมูลที่เลือกจากกราฟ"

                    )

                    st.caption(
                        f"จุดตรวจครั้งที่ #{int(item.get('ID', 0)) + 1}  ·  {item['เวลา']}"
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
                        display_width=340
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

                        history_color = history_info["color"]
                        history_text_color = "#172033" if item["ระดับ"] == "Medium" else "#ffffff"

                        st.markdown(
                            f'<div class="history-density-badge" '
                            f'style="background:{history_color};color:{history_text_color};">'
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
            st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# ลำดับการจัดเก็บขยะ
# =====================================================

LEVEL_ORDER = {"Normal": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}

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

if len(collection_priority) == 0:
    st.markdown(
        '''
        <section class="collection-section">
            <div class="collection-title">🚛 ลำดับการจัดเก็บขยะ</div>
            <div class="collection-subtitle">รอข้อมูลจากกล้องเพื่อสร้างเส้นทางการจัดเก็บ</div>
            <div class="collection-empty">ยังไม่มีข้อมูลจากกล้องสำหรับจัดลำดับการจัดเก็บขยะ</div>
        </section>
        ''',
        unsafe_allow_html=True
    )
else:
    checkpoint_html = []
    cards = []

    for rank, item in enumerate(collection_priority, start=1):
        info = LEVEL_INFO.get(item["level"], LEVEL_INFO["Normal"])
        checkpoint_html.append(
            f'''
            <div class="collection-checkpoint-wrap">
                <div class="collection-checkpoint" style="background:{info["color"]};">
                    <span>{rank}</span>
                </div>
                <div class="collection-checkpoint-label">{item["camera"]}</div>
            </div>
            '''
        )
        cards.append(
            f'''
            <div class="collection-stop">
                <div class="collection-rank" style="background:{info["color"]};">{rank}</div>
                <div class="collection-camera">📷 {item["camera"]}</div>
                <div class="collection-war">WAR {item["WAR"]:.2f}%</div>
                <div class="collection-level">{info["name"]}</div>
                <div class="collection-detail">
                    ขยะใน ROI: {item["garbage_pixels"]:,} px<br>
                    ROI: {item["roi_area"]:,} px<br>
                    พื้นที่ขยะเทียบ ROI อ้างอิง: {item["normalized_garbage_pixels"]:,.1f} px
                </div>
            </div>
            '''
        )

    collection_html = f'''
        <section class="collection-section">
            <div class="collection-head">
                <div>
                    <div class="collection-title">🚛 ลำดับการจัดเก็บขยะ</div>
                    <div class="collection-subtitle">รถเก็บขยะเดินทางทางเดียวจาก checkpoint ที่ควรจัดเก็บก่อน → จุดที่ควรจัดเก็บภายหลัง</div>
                </div>
                <details class="collection-info">
                    <summary>ⓘ</summary>
                    <div class="collection-info-pop">
                        <b>ระบบเรียงจากอะไร?</b>
                        <ol>
                            <li>หาพิกเซลขยะที่อยู่ใน ROI</li>
                            <li>ปรับพื้นที่ ROI ให้เทียบกับพื้นที่อ้างอิงเดียวกัน</li>
                            <li>เปรียบเทียบพื้นที่ขยะหลังปรับ — มากกว่าจัดเก็บก่อน</li>
                            <li>หากพื้นที่ขยะใกล้เคียงกัน จึงใช้ระดับความหนาแน่นเป็นตัวช่วย</li>
                        </ol>
                        <div class="collection-example">
                            A = 5/50<br>
                            B = 1/2 → ปรับเป็น 25/50<br>
                            <b>ดังนั้น B มีพื้นที่ขยะเทียบมากกว่า → มาก่อน</b>
                        </div>
                    </div>
                </details>
            </div>

            <div class="collection-road">
                <div class="collection-lane"></div>
                <div class="collection-checkpoints">{''.join(checkpoint_html)}</div>
                <div class="collection-truck">🚛</div>
                <div class="collection-road-arrow">→</div>
                <div class="collection-road-label">เส้นทางรถเก็บขยะ</div>
            </div>

            <div class="collection-stops">{''.join(cards)}</div>
            <div class="collection-note">อันดับ 1 คือ checkpoint แรกของเส้นทาง และรถจะวิ่งต่อไปตามลำดับจนถึง checkpoint สุดท้าย</div>
        </section>
        '''
    st.html(collection_html)
