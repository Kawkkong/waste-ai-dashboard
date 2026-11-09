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

from inference import analyze_frame, get_model
from config import CAMERA_CONFIG
from theme import inject_theme


st.set_page_config(
    page_title="AI Waste Vision · Liquid Glass HUD",
    page_icon="🗑️",
    layout="wide",
)

# โหลดโมเดลเข้าหน่วยความจำตั้งแต่เปิดระบบ
get_model()

LEVEL_INFO = {
    "Normal": {
        "name": "Normal (ปกติ)",
        "color": "#10b981",
        "action": "ไม่พบขยะในพื้นที่",
    },
    "Low": {
        "name": "Low (ต่ำ)",
        "color": "#3b82f6",
        "action": "เฝ้าระวังพื้นที่ตามปกติ",
    },
    "Medium": {
        "name": "Medium (ปานกลาง)",
        "color": "#f59e0b",
        "action": "เตรียมวางแผนจัดเก็บขยะ",
    },
    "High": {
        "name": "High (สูง)",
        "color": "#f97316",
        "action": "แจ้งเตือนเจ้าหน้าที่เข้าตรวจสอบ",
    },
    "Critical": {
        "name": "Critical (วิกฤต)",
        "color": "#ef4444",
        "action": "แจ้งเจ้าหน้าที่และดำเนินการเก็บขยะด่วน",
    },
}


def show_image_viewer(img_bgr, title="", display_width=360):
    if img_bgr is None:
        return

    h, w = img_bgr.shape[:2]
    if w <= 0 or h <= 0:
        return

    max_preview_w = 720
    if w > max_preview_w:
        scale = max_preview_w / float(w)
        preview_img = cv2.resize(
            img_bgr,
            (max_preview_w, max(1, int(h * scale))),
            interpolation=cv2.INTER_AREA,
        )
    else:
        preview_img = img_bgr

    ok, encoded = cv2.imencode(".jpg", preview_img, [cv2.IMWRITE_JPEG_QUALITY, 82])
    if not ok:
        return

    image_b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")
    aspect_height = int(display_width * h / w)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            html, body {{
                width: 100%;
                background: transparent;
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Tahoma, sans-serif;
            }}
            .viewer {{
                position: relative;
                width: 100%;
                max-width: {display_width}px;
                aspect-ratio: {w} / {h};
                margin: 0 auto;
                overflow: hidden;
                border-radius: 14px;
                border: 1px solid rgba(148, 163, 184, 0.28);
                background: rgba(15, 23, 42, 0.25);
                cursor: zoom-in;
            }}
            .viewer img {{
                display: block;
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
            }}
            .viewer:hover img {{
                transform: scale(1.03);
            }}
            .zoom-btn {{
                position: absolute;
                top: 8px;
                right: 8px;
                z-index: 10;
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 999px;
                padding: 5px 12px;
                background: rgba(15, 23, 42, 0.65);
                backdrop-filter: blur(10px);
                color: #ffffff;
                font-size: 11px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.25s ease;
            }}
            .zoom-btn:hover {{
                background: rgba(0, 245, 212, 0.88);
                color: #030712;
                transform: translateY(-1px);
            }}
            .viewer:fullscreen {{
                width: 100vw;
                height: 100vh;
                max-width: none;
                border-radius: 0;
                background: #000;
                cursor: zoom-out;
            }}
            .viewer:fullscreen img {{
                width: 100vw;
                height: 100vh;
                object-fit: contain;
                transform: none;
            }}
        </style>
    </head>
    <body>
        <div class="viewer" id="viewer" title="ดับเบิลคลิกเพื่อขยายเต็มจอ">
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
                }} catch (e) {{}}
            }}
            zoom.addEventListener("click", (e) => {{
                e.stopPropagation();
                toggleFullscreen();
            }});
            viewer.addEventListener("dblclick", (e) => {{
                if (e.target !== zoom) toggleFullscreen();
            }});
            document.addEventListener("fullscreenchange", () => {{
                zoom.textContent = document.fullscreenElement ? "⛶ ออกจากเต็มจอ" : "⛶ ขยายภาพ";
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=aspect_height + 10, scrolling=False)


# =====================================================
# Session State Initialization
# =====================================================
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

if "default_camera_config" not in st.session_state:
    st.session_state.default_camera_config = copy.deepcopy(CAMERA_CONFIG)

if "runtime_camera_config" not in st.session_state:
    st.session_state.runtime_camera_config = copy.deepcopy(st.session_state.default_camera_config)
else:
    CAMERA_CONFIG.clear()
    CAMERA_CONFIG.update(copy.deepcopy(st.session_state.runtime_camera_config))

for cam in CAMERA_CONFIG:
    if cam not in st.session_state.history:
        st.session_state.history[cam] = []


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
    default_cfg = copy.deepcopy(st.session_state.default_camera_config[camera])
    new_config = copy.deepcopy(st.session_state.runtime_camera_config)
    if camera not in new_config:
        new_config[camera] = {}
    if restore_roi:
        new_config[camera]["roi"] = tuple(default_cfg["roi"])
    if restore_threshold:
        new_config[camera]["threshold"] = copy.deepcopy(default_cfg["threshold"])
    st.session_state.runtime_camera_config = new_config
    CAMERA_CONFIG.clear()
    CAMERA_CONFIG.update(copy.deepcopy(new_config))


def reset_roi_callback(camera):
    restore_camera_default(camera, restore_roi=True, restore_threshold=False)
    default_roi = st.session_state.default_camera_config[camera]["roi"]
    st.session_state[f"roi_x1_{camera}"] = int(default_roi[0])
    st.session_state[f"roi_y1_{camera}"] = int(default_roi[1])
    st.session_state[f"roi_x2_{camera}"] = int(default_roi[2])
    st.session_state[f"roi_y2_{camera}"] = int(default_roi[3])


def reset_threshold_callback(camera):
    restore_camera_default(camera, restore_roi=False, restore_threshold=True)
    default_thr = st.session_state.default_camera_config[camera]["threshold"]
    st.session_state[f"threshold_low_{camera}"] = float(default_thr["low"])
    st.session_state[f"threshold_medium_{camera}"] = float(default_thr["medium"])
    st.session_state[f"threshold_high_{camera}"] = float(default_thr["high"])


# ฉีดระบบธีมและ Client-Side Toggle Engine
inject_theme()


# =====================================================
# HEADER BAR (สลับโหมดมืด/สว่าง และสไลด์เปิด/ปิดตั้งค่าใน 0ms ด้วย JS ไม่ต้องรอโหลดหน้าเว็บใหม่!)
# =====================================================
header_html = """
<div class="wv-topbar">
    <div class="app-brand">
        <div class="app-brand-left">
            <div class="app-brand-icon">🗑️</div>
            <div>
                <div class="app-title">ระบบตรวจสอบปริมาณขยะด้วย AI</div>
                <div class="app-subtitle"><span class="live-dot"></span> YOLOv11-Seg · Real-Time WAR Analytics</div>
            </div>
        </div>
    </div>

    <div class="wv-actions">
        <button type="button" class="wv-btn" data-wv-action="toggle-drawer">
            <span class="wv-set-open-txt">⚙️ ตั้งค่า</span>
            <span class="wv-set-close-txt">✕ ปิดตั้งค่า</span>
        </button>

        <button type="button" class="wv-btn" data-wv-action="toggle-theme">
            <span class="wv-theme-light-txt">☀️ โหมดสว่าง</span>
            <span class="wv-theme-dark-txt">🌙 โหมดมืด</span>
        </button>

        <details class="wv-help-wrap">
            <summary class="wv-btn">❔ วิธีใช้</summary>
            <div class="wv-help-pop">
                <b style="font-size:14px;color:var(--accent);">วิธีใช้งานระบบ</b><br><br>
                <b>1. อัปโหลดภาพ:</b> เลือกไฟล์ภาพจากกล้อง CCTV<br>
                <b>2. ตรวจผล AI:</b> ดูภาพ Segmentation, ค่า WAR (%) และคำแนะนำ<br>
                <b>3. กราฟ & ประวัติ:</b> คลิกจุดบนกราฟเพื่อดูผลย้อนหลัง<br>
                <b>4. ตั้งค่า:</b> กดปุ่ม <b>⚙️ ตั้งค่า</b> เพื่อสไลด์เปิดแผงปรับ ROI และเกณฑ์วัด
            </div>
        </details>
    </div>
</div>
"""
st.html(header_html)


# =====================================================
# SMOOTH SLIDE-DOWN SETTINGS DRAWER (ซ่อนสนิทตั้งแต่เข้าเว็บ เลื่อนลงทันทีเมื่อกด ⚙️ ตั้งค่า)
# =====================================================
with st.container(key="settings_drawer"):
    st.markdown(
        '<div class="settings-title">⚙️ แผงควบคุมการตั้งค่ากล้อง (Camera ROI & Thresholds)</div>'
        '<div class="settings-subtitle">ปรับพิกัดกรอบตรวจจับ (ROI) และเกณฑ์ความหนาแน่นขยะแยกตามกล้อง</div>',
        unsafe_allow_html=True,
    )

    setting_camera = st.selectbox(
        "เลือกกล้องที่ต้องการตั้งค่า",
        list(CAMERA_CONFIG.keys()),
        key="setting_camera",
    )

    cfg = CAMERA_CONFIG[setting_camera]
    current_roi = cfg["roi"]
    current_threshold = cfg["threshold"]

    setting_img = st.session_state.camera_results.get(setting_camera, {}).get("original")
    if setting_img is not None:
        image_h, image_w = setting_img.shape[:2]
    else:
        image_w = max(int(current_roi[2]), 1920)
        image_h = max(int(current_roi[3]), 1080)

    st.markdown('<div class="settings-section-label">📐 พิกัดพื้นที่ตรวจจับ (ROI Coordinates)</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        new_x1 = st.number_input(
            "X1 (ซ้าย)",
            min_value=0,
            max_value=max(0, image_w - 1),
            value=min(max(0, int(current_roi[0])), max(0, image_w - 1)),
            step=1,
            key=f"roi_x1_{setting_camera}",
        )
    with r2:
        new_y1 = st.number_input(
            "Y1 (บน)",
            min_value=0,
            max_value=max(0, image_h - 1),
            value=min(max(0, int(current_roi[1])), max(0, image_h - 1)),
            step=1,
            key=f"roi_y1_{setting_camera}",
        )
    with r3:
        new_x2 = st.number_input(
            "X2 (ขวา)",
            min_value=1,
            max_value=max(1, image_w),
            value=min(max(1, int(current_roi[2])), max(1, image_w)),
            step=1,
            key=f"roi_x2_{setting_camera}",
        )
    with r4:
        new_y2 = st.number_input(
            "Y2 (ล่าง)",
            min_value=1,
            max_value=max(1, image_h),
            value=min(max(1, int(current_roi[3])), max(1, image_h)),
            step=1,
            key=f"roi_y2_{setting_camera}",
        )

    st.markdown('<div class="settings-section-label">📊 เกณฑ์ระดับความหนาแน่น WAR (%)</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    with t1:
        new_low = st.number_input(
            "Low (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(current_threshold["low"]),
            step=0.5,
            key=f"threshold_low_{setting_camera}",
        )
    with t2:
        new_medium = st.number_input(
            "Medium (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(current_threshold["medium"]),
            step=0.5,
            key=f"threshold_medium_{setting_camera}",
        )
    with t3:
        new_high = st.number_input(
            "High (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(current_threshold["high"]),
            step=0.5,
            key=f"threshold_high_{setting_camera}",
        )

    apply_current = st.checkbox(
        "วิเคราะห์ภาพล่าสุดของกล้องนี้ใหม่ทันทีหลังบันทึก",
        value=True,
        key=f"reanalyze_{setting_camera}",
    )

    act1, act2, act3, act4 = st.columns(4)
    with act1:
        st.button(
            "↩️ คืนค่า ROI",
            use_container_width=True,
            key=f"reset_roi_{setting_camera}",
            on_click=reset_roi_callback,
            args=(setting_camera,),
        )
    with act2:
        st.button(
            "↩️ คืนค่า Threshold",
            use_container_width=True,
            key=f"reset_threshold_{setting_camera}",
            on_click=reset_threshold_callback,
            args=(setting_camera,),
        )
    with act3:
        if st.button("💾 บันทึกการตั้งค่า", type="primary", use_container_width=True, key="save_camera_config"):
            if not (new_x1 < new_x2 and new_y1 < new_y2):
                st.error("ROI ไม่ถูกต้อง: ต้องกำหนดให้ X1 < X2 และ Y1 < Y2")
            elif not (new_low < new_medium < new_high):
                st.error("Threshold ไม่ถูกต้อง: ต้องกำหนดให้ Low < Medium < High")
            else:
                save_camera_config(
                    setting_camera,
                    (new_x1, new_y1, new_x2, new_y2),
                    {"low": new_low, "medium": new_medium, "high": new_high},
                )
                if apply_current and setting_camera in st.session_state.camera_results:
                    current_img = st.session_state.camera_results[setting_camera]["original"]
                    inference_module.previous_WAR.pop(setting_camera, None)
                    refreshed = analyze_frame(current_img, setting_camera)
                    st.session_state.camera_results[setting_camera]["result"] = refreshed
                    st.session_state.camera_results[setting_camera]["config_roi"] = tuple(
                        CAMERA_CONFIG[setting_camera].get("roi", (0, 0, 0, 0))
                    )
                    st.session_state.camera_results[setting_camera]["config_threshold"] = dict(
                        CAMERA_CONFIG[setting_camera].get("threshold", {})
                    )
                st.rerun()
    with act4:
        st.html(
            '<button type="button" class="wv-btn" style="width:100%;min-height:42px;" '
            'data-wv-action="close-drawer">✕ ซ่อนแผงตั้งค่า</button>'
        )


# =====================================================
# TECH SUMMARY HUD STRIP
# =====================================================
active_cams = len(st.session_state.camera_results)
total_cams = len(CAMERA_CONFIG)
avg_war = (
    np.mean([d["result"]["WAR"] for d in st.session_state.camera_results.values()])
    if active_cams > 0
    else 0.0
)
alert_cams = sum(
    1
    for d in st.session_state.camera_results.values()
    if d["result"]["level"] in {"High", "Critical"}
)

st.markdown(
    f"""
    <div class="tech-stat-row">
        <div class="tech-stat-card">
            <div>
                <div class="tech-stat-label">ACTIVE CAMERAS</div>
                <div class="tech-stat-val">{active_cams} / {total_cams}</div>
            </div>
            <span style="font-size:24px;">📷</span>
        </div>
        <div class="tech-stat-card">
            <div>
                <div class="tech-stat-label">AVERAGE WAR</div>
                <div class="tech-stat-val">{avg_war:.2f}%</div>
            </div>
            <span style="font-size:24px;">📊</span>
        </div>
        <div class="tech-stat-card">
            <div>
                <div class="tech-stat-label">HIGH / CRITICAL ALERTS</div>
                <div class="tech-stat-val" style="color:{'#ef4444' if alert_cams > 0 else 'var(--accent)'};">{alert_cams} จุด</div>
            </div>
            <span style="font-size:24px;">🚨</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# UPLOAD CCTV IMAGE
# =====================================================
with st.expander("📷 อัปโหลดภาพจากกล้อง CCTV", expanded=not bool(st.session_state.camera_results)):
    upload_columns = st.columns(len(CAMERA_CONFIG), gap="medium")

    for upload_col, cam in zip(upload_columns, CAMERA_CONFIG):
        cam_loc = CAMERA_CONFIG[cam].get("name", "")
        with upload_col:
            st.markdown(
                f'<div class="upload-camera-label">'
                f'<span>📷 {cam} ({cam_loc})</span>'
                f'<span style="font-size:11px;opacity:0.75;">JPG / PNG</span>'
                f"</div>"
                f'<div class="upload-hint">ลากไฟล์ภาพมาวาง หรือกด Browse files เพื่อวิเคราะห์ด้วย AI</div>',
                unsafe_allow_html=True,
            )

            uploaded_file = st.file_uploader(
                f"เลือกภาพสำหรับ {cam}",
                type=["jpg", "jpeg", "png"],
                key=cam,
                label_visibility="collapsed",
            )

            if uploaded_file is not None:
                file_id = (uploaded_file.name, uploaded_file.size)
                old_file = st.session_state.camera_results.get(cam, {}).get("file_id")

                if file_id != old_file:
                    bytes_data = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                    img = cv2.imdecode(bytes_data, cv2.IMREAD_COLOR)

                    if img is None:
                        st.error(f"ไม่สามารถอ่านไฟล์ภาพของ {cam} ได้ กรุณาเลือกไฟล์ใหม่")
                        continue

                    with st.spinner(f"⚡ AI กำลังประมวลผลภาพ {cam}..."):
                        result = analyze_frame(img, cam)

                    if result.get("level") in {"High", "Critical"}:
                        st.session_state.density_alert = {
                            "camera": cam,
                            "level": result["level"],
                            "war": float(result.get("WAR", 0)),
                            "created_at": time.monotonic(),
                        }

                    st.session_state.selected_history_by_camera.pop(cam, None)
                    st.session_state.selected_history_camera = cam

                    st.session_state.camera_results[cam] = {
                        "file_id": file_id,
                        "original": img,
                        "result": result,
                        "config_roi": tuple(CAMERA_CONFIG[cam].get("roi", (0, 0, 0, 0))),
                        "config_threshold": dict(CAMERA_CONFIG[cam].get("threshold", {})),
                    }

                    history_id = len(st.session_state.history[cam])
                    st.session_state.history[cam].append(
                        {
                            "ID": history_id,
                            "เวลา": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "ภาพ": img.copy(),
                            "ผล": result["image"].copy(),
                            "WAR": result["WAR"],
                            "เปลี่ยนแปลง": result["change"],
                            "ระดับ": result["level"],
                        }
                    )
                    st.rerun()


# =====================================================
# DENSITY ALERT TOAST
# =====================================================
alert = st.session_state.get("density_alert")
if alert is not None:
    elapsed = time.monotonic() - float(alert.get("created_at", 0))
    remaining = max(0.0, 10.0 - elapsed)

    if remaining <= 0:
        st.session_state.density_alert = None
    else:
        alert_camera = str(alert.get("camera", "Camera"))
        alert_level = str(alert.get("level", "High"))
        alert_war = float(alert.get("war", 0))

        if alert_level == "Critical":
            alert_color = "#ef4444"
            alert_icon = "🚨"
            alert_title = "แจ้งเตือนปริมาณขยะระดับวิกฤต!"
            alert_message = "ควรดำเนินการจัดเก็บขยะโดยด่วนที่สุด"
        else:
            alert_color = "#f97316"
            alert_icon = "⚠️"
            alert_title = "แจ้งเตือนปริมาณขยะระดับสูง"
            alert_message = "ควรวางแผนเข้าจัดเก็บขยะโดยเร็ว"

        alert_id = f"density-alert-{abs(hash((alert_camera, alert.get('created_at'))))}"
        alert_html = f"""
        <style>
        #{alert_id} {{
            position: fixed;
            right: 24px;
            bottom: 24px;
            z-index: 999999;
            width: min(390px, calc(100vw - 32px));
        }}
        #{alert_id} .alert-box {{
            position: relative;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 15px 40px 15px 15px;
            border: 1px solid var(--liquid-border);
            border-left: 5px solid {alert_color};
            border-radius: 18px;
            background: var(--popover-bg);
            backdrop-filter: blur(20px);
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
            color: var(--ink);
            font-family: "Prompt", "Noto Sans Thai", Tahoma, sans-serif;
            animation: densityAlertLife {remaining:.2f}s linear forwards;
        }}
        #{alert_id} .alert-icon {{
            flex: 0 0 38px;
            width: 38px;
            height: 38px;
            display: grid;
            place-items: center;
            border-radius: 11px;
            background: {alert_color};
            color: #fff;
            font-size: 20px;
        }}
        #{alert_id} .alert-title {{
            margin: 0 0 3px;
            font-size: 14px;
            font-weight: 700;
            color: {alert_color};
        }}
        #{alert_id} .alert-message {{
            margin: 0;
            font-size: 12px;
            line-height: 1.55;
            color: var(--ink-soft);
        }}
        #{alert_id} .alert-close {{
            position: absolute;
            top: 8px;
            right: 8px;
            width: 28px;
            height: 28px;
            border: 0;
            border-radius: 8px;
            background: transparent;
            color: var(--ink-soft);
            font-size: 18px;
            cursor: pointer;
        }}
        @keyframes densityAlertLife {{
            0% {{ opacity: 0; transform: translateY(14px); }}
            8% {{ opacity: 1; transform: translateY(0); }}
            90% {{ opacity: 1; transform: translateY(0); }}
            100% {{ opacity: 0; transform: translateY(8px); }}
        }}
        </style>
        <div id="{alert_id}">
            <div class="alert-box">
                <div class="alert-icon">{alert_icon}</div>
                <div>
                    <p class="alert-title">{alert_title}</p>
                    <p class="alert-message">
                        กล้อง <b>{alert_camera}</b> อยู่ในระดับ <b>{alert_level}</b> (WAR {alert_war:.2f}%)<br>
                        {alert_message}
                    </p>
                </div>
                <button type="button" class="alert-close" data-wv-action="dismiss" data-wv-target="#{alert_id}">×</button>
            </div>
        </div>
        """
        st.html(alert_html)


# =====================================================
# CAMERA DETAILS RENDERER
# =====================================================
def render_camera_details(cam, data):
    result = data["result"]
    level = result["level"]
    info = LEVEL_INFO[level]

    st.markdown(
        f'<div class="camera-detail-card">'
        f'<div class="camera-status-pill" style="background:{info["color"]};color:#ffffff;">'
        f'{info["name"]}'
        f"</div>"
        f'<div class="camera-action-card">'
        f'<span class="action-label">คำแนะนำ:</span>'
        f'<span class="action-text">{info["action"]}</span>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="camera-image-title">📸 ภาพต้นฉบับจากกล้อง</div>', unsafe_allow_html=True)
        show_image_viewer(data["original"], title="ภาพจากกล้อง", display_width=350)

    with c2:
        st.markdown('<div class="camera-image-title">🎯 ผลตรวจจับขยะ (AI Segmentation)</div>', unsafe_allow_html=True)
        show_image_viewer(result["image"], title="ผล Segmentation", display_width=350)

    st.markdown("#### 📊 สรุปผลการวิเคราะห์ล่าสุด")
    m1, m2, m3 = st.columns(3)
    m1.metric("สัดส่วนขยะ (WAR)", f'{result["WAR"]:.2f}%')
    m2.metric("การเปลี่ยนแปลง", f'{result["change"]:+.2f}%')
    m3.metric("ระดับความหนาแน่น", info["name"].split(" ")[0])

    war_title_col, war_info_col = st.columns([0.88, 0.12], vertical_alignment="center")
    with war_title_col:
        st.markdown(f"#### 📈 แนวโน้มค่า WAR : {cam}")
    with war_info_col:
        with st.popover("ℹ️", use_container_width=True):
            st.markdown("**WAR (Waste Area Ratio)**")
            st.markdown("`WAR = (พิกเซลขยะใน ROI ÷ พื้นที่ ROI) × 100`")
            st.caption("ใช้วัดสัดส่วนพื้นที่ขยะภายในกรอบ ROI ของแต่ละกล้อง")

    if len(st.session_state.history[cam]) > 0:
        graph_data = pd.DataFrame(st.session_state.history[cam]).reset_index(drop=True)
        graph_data["จุด"] = np.arange(1, len(graph_data) + 1)

        fig = px.line(
            graph_data,
            x="จุด",
            y="WAR",
            markers=True,
            custom_data=["เวลา", "ระดับ", "เปลี่ยนแปลง"],
        )
        fig.update_traces(
            line=dict(width=3, color="#14b8a6", shape="spline", smoothing=0.8),
            marker=dict(size=8, color="#ffffff", line=dict(width=2.5, color="#6366f1")),
            hovertemplate=(
                "<b>ครั้งที่ %{x}</b><br>"
                "WAR: <b>%{y:.2f}%</b><br>"
                "เวลา: %{customdata[0]}<br>"
                "ระดับ: %{customdata[1]}<br>"
                "เปลี่ยนแปลง: %{customdata[2]:+.2f}%<extra></extra>"
            ),
        )

        current_thr = CAMERA_CONFIG.get(cam, {}).get("threshold", {})
        for key, color, label in [
            ("low", "#10b981", "Low"),
            ("medium", "#f59e0b", "Medium"),
            ("high", "#f97316", "High"),
        ]:
            if key in current_thr:
                try:
                    y_val = float(current_thr[key])
                    fig.add_hline(
                        y=y_val,
                        line_width=1,
                        line_dash="dot",
                        line_color=color,
                        annotation_text=f"{label} {y_val:g}%",
                        annotation_position="top left",
                    )
                except (TypeError, ValueError):
                    pass

        fig.update_layout(
            height=260,
            margin=dict(l=8, r=12, t=12, b=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
            font=dict(family="Prompt, sans-serif", size=11, color="#94a3b8"),
            showlegend=False,
            xaxis=dict(
                title="ครั้งที่บันทึก",
                tickmode="linear",
                dtick=1,
                showgrid=False,
                zeroline=False,
            ),
            yaxis=dict(
                title="WAR (%)",
                ticksuffix="%",
                showgrid=True,
                gridcolor="rgba(148, 163, 184, 0.16)",
                zeroline=False,
                rangemode="tozero",
            ),
        )

        st.markdown(
            '<div class="chart-tip">💡 คลิกจุดบนกราฟเพื่อดูภาพและข้อมูลย้อนหลังของรอบนั้น</div>',
            unsafe_allow_html=True,
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
                    point_index = first_point.get("point_index", first_point.get("pointNumber"))
                if point_index is not None:
                    point_index = int(point_index)
                    if 0 <= point_index < len(st.session_state.history[cam]):
                        st.session_state.selected_history_by_camera[cam] = (
                            st.session_state.history[cam][point_index]
                        )
                        st.session_state.selected_history_camera = cam
        except Exception:
            pass

        selected_history = st.session_state.selected_history_by_camera.get(cam)
        if selected_history is not None and st.session_state.selected_history_camera == cam:
            item = selected_history
            st.markdown("#### 🔎 ข้อมูลที่เลือกจากกราฟ")
            st.caption(f"ครั้งที่ #{int(item.get('ID', 0)) + 1} · {item['เวลา']}")
            sx, sy, sz = st.columns(3)
            sx.metric("WAR", f'{item["WAR"]:.2f}%')
            sy.metric("เปลี่ยนแปลง", f'{item["เปลี่ยนแปลง"]:+.2f}%')
            sz.metric("ระดับ", LEVEL_INFO[item["ระดับ"]]["name"].split(" ")[0])
            show_image_viewer(item["ผล"], title="ผล Segmentation จากจุดที่เลือก", display_width=350)

    st.markdown(f'<div class="history-title">🕒 ประวัติการตรวจสอบ ({cam})</div>', unsafe_allow_html=True)
    histories = st.session_state.history[cam]
    if len(histories) == 0:
        st.caption("ยังไม่มีประวัติการตรวจสอบ")
    else:
        for item in reversed(histories):
            history_info = LEVEL_INFO[item["ระดับ"]]
            history_color = {
                "Normal": "green",
                "Low": "blue",
                "Medium": "orange",
                "High": "orange",
                "Critical": "red",
            }.get(item["ระดับ"], "gray")

            with st.expander(
                f"📋 ครั้งที่ #{int(item['ID']) + 1} · {item['เวลา']} · :{history_color}[{history_info['name']}]",
                expanded=False,
            ):
                hx, hy, hz = st.columns(3)
                hx.metric("WAR", f'{item["WAR"]:.2f}%')
                hy.metric("เปลี่ยนแปลง", f'{item["เปลี่ยนแปลง"]:+.2f}%')
                hz.metric("ระดับ", history_info["name"].split(" ")[0])
                show_image_viewer(item["ผล"], title="ผล Segmentation", display_width=350)


# =====================================================
# CAMERA RESULTS SECTION
# =====================================================
camera_items = list(st.session_state.camera_results.items())
if camera_items:
    camera_cols = st.columns(len(camera_items), gap="medium")
    for camera_col, (cam, data) in zip(camera_cols, camera_items):
        result = data["result"]
        level = result["level"]
        info = LEVEL_INFO[level]
        cam_loc = CAMERA_CONFIG.get(cam, {}).get("name", "")
        level_color = {
            "Normal": "green",
            "Low": "blue",
            "Medium": "orange",
            "High": "orange",
            "Critical": "red",
        }.get(level, "gray")

        with camera_col:
            with st.expander(f"📷 {cam} ({cam_loc}) · :{level_color}[{info['name']}]", expanded=True):
                render_camera_details(cam, data)
else:
    st.info("💡 อัปโหลดภาพจากกล้อง CCTV ด้านบนเพื่อเริ่มการวิเคราะห์ด้วย AI")


# =====================================================
# COLLECTION PRIORITY ROUTE
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

    collection_priority.append(
        {
            "camera": cam,
            "WAR": war,
            "level": level,
            "level_rank": LEVEL_ORDER.get(level, 0),
            "roi_area": roi_area,
            "garbage_pixels": garbage_pixels,
        }
    )

for item in collection_priority:
    if item["roi_area"] > 0 and reference_roi_area > 0:
        item["normalized_garbage_pixels"] = (
            item["garbage_pixels"] * reference_roi_area / item["roi_area"]
        )
    else:
        item["normalized_garbage_pixels"] = 0.0

collection_priority.sort(
    key=lambda item: (item["normalized_garbage_pixels"], item["level_rank"]),
    reverse=True,
)

if len(collection_priority) == 0:
    st.markdown(
        '<section class="collection-section">'
        '<div class="collection-title">🚛 ลำดับการจัดเก็บขยะอัจฉริยะ (Smart Route Priority)</div>'
        '<div class="collection-subtitle">รอข้อมูลจากกล้องเพื่อจำลองเส้นทางการเดินรถจัดเก็บ</div>'
        '<div class="collection-empty">ยังไม่มีข้อมูลจากกล้องสำหรับจัดลำดับการจัดเก็บขยะ</div>'
        "</section>",
        unsafe_allow_html=True,
    )
else:
    checkpoint_html = []
    cards = []

    for rank, item in enumerate(collection_priority, start=1):
        info = LEVEL_INFO.get(item["level"], LEVEL_INFO["Normal"])
        checkpoint_html.append(
            f'<div class="collection-checkpoint-wrap">'
            f'<div class="collection-checkpoint" style="background:{info["color"]};"><span>{rank}</span></div>'
            f'<div class="collection-checkpoint-label">{item["camera"]}</div>'
            f"</div>"
        )
        cards.append(
            f'<div class="collection-stop">'
            f'<div class="collection-rank" style="background:{info["color"]};">{rank}</div>'
            f'<div class="collection-camera">📷 {item["camera"]}</div>'
            f'<div class="collection-war">WAR {item["WAR"]:.2f}%</div>'
            f'<div class="collection-level">{info["name"]}</div>'
            f'<div class="collection-detail">'
            f'ขยะใน ROI: {item["garbage_pixels"]:,} px<br>'
            f'พื้นที่ ROI: {item["roi_area"]:,} px<br>'
            f'พื้นที่ขยะเทียบอ้างอิง: {item["normalized_garbage_pixels"]:,.1f} px'
            f"</div>"
            f"</div>"
        )

    collection_html = (
        '<section class="collection-section">'
        '<div class="collection-head">'
        "<div>"
        '<div class="collection-title">🚛 ลำดับการจัดเก็บขยะอัจฉริยะ (Smart Route Priority)</div>'
        '<div class="collection-subtitle">รถเก็บขยะเดินทางจากจุดที่ควรจัดเก็บก่อน → จุดถัดไปตามลำดับความสำคัญ</div>'
        "</div>"
        "</div>"
        '<div class="collection-road">'
        '<div class="collection-lane"></div>'
        f'<div class="collection-checkpoints">{"".join(checkpoint_html)}</div>'
        '<div class="collection-truck">🚛</div>'
        '<div class="collection-road-arrow">→</div>'
        '<div class="collection-road-label">AI OPTIMIZED COLLECTION ROUTE</div>'
        "</div>"
        f'<div class="collection-stops">{"".join(cards)}</div>'
        '<div class="collection-note">อันดับ 1 คือจุดแรกของเส้นทาง และรถจะวิ่งต่อไปตามลำดับจนครบทุกจุด</div>'
        "</section>"
    )
    st.markdown(collection_html, unsafe_allow_html=True)
