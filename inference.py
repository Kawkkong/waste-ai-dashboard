from ultralytics import YOLO
import cv2
import numpy as np
import streamlit as st

from config import CAMERA_CONFIG

MODEL_PATH = "best.pt"


@st.cache_resource(show_spinner=False)
def get_model():
    return YOLO(MODEL_PATH)


previous_WAR = {}


def density_level(WAR, threshold):
    if WAR == 0:
        return "Normal"
    elif WAR <= threshold["low"]:
        return "Low"
    elif WAR <= threshold["medium"]:
        return "Medium"
    elif WAR <= threshold["high"]:
        return "High"
    else:
        return "Critical"


def recommendation(level):
    action = {
        "Normal": "ไม่พบขยะในพื้นที่",
        "Low": "เฝ้าระวังพื้นที่ตามปกติ",
        "Medium": "เตรียมวางแผนจัดเก็บขยะ",
        "High": "แจ้งเตือนเจ้าหน้าที่เข้าตรวจสอบ",
        "Critical": "แจ้งเจ้าหน้าที่และดำเนินการเก็บขยะด่วน",
    }
    return action[level]


def analyze_frame(img, camera):
    global previous_WAR

    if img is None:
        raise ValueError("ไม่พบภาพสำหรับวิเคราะห์")

    if camera not in CAMERA_CONFIG:
        raise KeyError(f"ไม่พบ configuration ของ {camera}")

    h, w = img.shape[:2]
    cfg = CAMERA_CONFIG[camera]
    x1, y1, x2, y2 = cfg["roi"]

    x1 = max(0, min(int(x1), w))
    x2 = max(0, min(int(x2), w))
    y1 = max(0, min(int(y1), h))
    y2 = max(0, min(int(y2), h))

    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    # ปรับ imgsz=640 และ retina_masks=False เพื่อให้ประมวลผลบน CPU เร็วขึ้น 4 เท่า
    model = get_model()
    result = model(
        img,
        imgsz=640,
        conf=0.20,
        retina_masks=False,
        verbose=False,
    )[0]

    combined_mask = np.zeros((h, w), dtype=np.uint8)
    detected = 0

    if result.masks is not None:
        masks = result.masks.data.cpu().numpy()
        detected = len(masks)
        for mask in masks:
            if mask.shape != (h, w):
                mask = cv2.resize(
                    mask.astype(np.float32),
                    (w, h),
                    interpolation=cv2.INTER_LINEAR,
                )
            combined_mask[mask > 0.5] = 1

    roi_mask = np.zeros((h, w), dtype=np.uint8)
    if x2 > x1 and y2 > y1:
        roi_mask[y1:y2, x1:x2] = 1

    garbage_mask = combined_mask * roi_mask

    garbage_pixels = int(np.count_nonzero(garbage_mask))
    roi_pixels = int(np.count_nonzero(roi_mask))
    total_mask_pixels = int(np.count_nonzero(combined_mask))

    WAR = round(float((garbage_pixels / roi_pixels) * 100), 2) if roi_pixels > 0 else 0.0

    change = 0.0
    if camera in previous_WAR:
        change = round(float(WAR - previous_WAR[camera]), 2)
    previous_WAR[camera] = WAR

    level = density_level(WAR, cfg["threshold"])

    # วาดภาพ Overlay ความเร็วสูง
    output = cv2.convertScaleAbs(img, alpha=0.42, beta=0)
    mask_bool = garbage_mask == 1

    if np.any(mask_bool):
        fg = img[mask_bool].astype(np.float32)
        green = np.array([120.0, 255.0, 60.0], dtype=np.float32)  # BGR Neon Green/Cyan
        output[mask_bool] = np.clip(fg * 0.45 + green * 0.55, 0, 255).astype(np.uint8)

    if x2 > x1 and y2 > y1:
        cv2.rectangle(output, (x1, y1), (x2, y2), (255, 220, 0), 3)

    cv2.putText(
        output,
        f"WAR {WAR:.2f}%",
        (36, 56),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.3,
        (255, 255, 255),
        3,
    )
    cv2.putText(
        output,
        level.upper(),
        (36, 108),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 220, 0),
        3,
    )

    return {
        "image": output,
        "mask": garbage_mask,
        "WAR": WAR,
        "change": change,
        "level": level,
        "action": recommendation(level),
        "camera": camera,
        "detected": detected,
        "garbage_pixels": garbage_pixels,
        "roi_pixels": roi_pixels,
        "total_mask_pixels": total_mask_pixels,
        "roi": (x1, y1, x2, y2),
    }
