from ultralytics import YOLO
import cv2
import numpy as np
import streamlit as st

from config import CAMERA_CONFIG

MODEL_PATH = "best.pt"


@st.cache_resource(show_spinner=False)
def get_model():
    return YOLO(MODEL_PATH)


model = get_model()
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

    result = model(
        img,
        imgsz=1280,
        conf=0.20,
        retina_masks=True,
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

    if roi_pixels > 0:
        WAR = (garbage_pixels / roi_pixels) * 100
    else:
        WAR = 0

    WAR = round(float(WAR), 2)

    change = 0
    if camera in previous_WAR:
        change = WAR - previous_WAR[camera]
    previous_WAR[camera] = WAR
    change = round(float(change), 2)

    level = density_level(WAR, cfg["threshold"])

    dim_background = cv2.convertScaleAbs(img, alpha=0.45, beta=0)
    output = dim_background.copy()
    output[garbage_mask == 1] = img[garbage_mask == 1]

    green_overlay = np.zeros_like(img)
    green_overlay[garbage_mask == 1] = (0, 255, 0)

    output = np.where(
        garbage_mask[..., None] == 1,
        cv2.addWeighted(output, 0.35, green_overlay, 0.65, 0),
        output,
    )

    if x2 > x1 and y2 > y1:
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 255), 4)

    cv2.putText(
        output,
        f"WAR {WAR}%",
        (40, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (255, 255, 255),
        3,
    )
    cv2.putText(
        output,
        level,
        (40, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 255, 255),
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
  
