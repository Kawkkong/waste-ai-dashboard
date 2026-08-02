# ======================================================
# inference.py
# YOLOv11-Seg + ROI + WAR
# ใช้ Polygon Mask (ไม่เกิด mask เลื่อน)
# ======================================================


from ultralytics import YOLO
import cv2
import numpy as np

from config import CAMERA_CONFIG



# =========================
# Load Model
# =========================

MODEL_PATH = "best.pt"

model = YOLO(MODEL_PATH)





# =========================
# Density Classification
# =========================

def classify_density(WAR, threshold):


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


    if level == "Normal":

        return "ไม่ต้องเก็บ"


    elif level == "Low":

        return "ติดตามสถานการณ์"


    elif level == "Medium":

        return "เตรียมจัดเก็บ"


    elif level == "High":

        return "แจ้งเจ้าหน้าที่"


    else:

        return "เก็บทันที"






# =========================
# Main Prediction
# =========================


def predict(image, camera):


    config = CAMERA_CONFIG[camera]


    roi = config["roi"]


    x1 = roi["x1"]
    y1 = roi["y1"]

    x2 = roi["x2"]
    y2 = roi["y2"]



    height,width = image.shape[:2]



    # =====================
    # YOLO Segmentation
    # =====================


    result = model(image)[0]



    combined_mask = np.zeros(
        (height,width),
        dtype=np.uint8
    )



    if result.masks is not None:


        # ใช้ polygon mask
        # ไม่ resize tensor


        polygons = result.masks.xy



        for poly in polygons:


            poly = poly.astype(
                np.int32
            )


            cv2.fillPoly(
                combined_mask,
                [poly],
                1
            )




    # =====================
    # Full Image WAR
    # =====================


    full_garbage_pixels = np.sum(
        combined_mask
    )


    full_pixels = (
        height *
        width
    )


    WAR_full = (

        full_garbage_pixels /
        full_pixels

    ) * 100






    # =====================
    # ROI Mask
    # =====================


    roi_mask = np.zeros(
        (height,width),
        dtype=np.uint8
    )


    roi_mask[
        y1:y2,
        x1:x2
    ] = 1





    # เอาขยะเฉพาะ ROI


    garbage_mask = (

        combined_mask *
        roi_mask

    )





    # =====================
    # ROI WAR
    # =====================


    garbage_pixels = np.sum(
        garbage_mask
    )


    roi_pixels = np.sum(
        roi_mask
    )



    WAR = (

        garbage_pixels /
        roi_pixels

    ) * 100





    # =====================
    # Level
    # =====================


    level = classify_density(
        WAR,
        config["threshold"]
    )





    return {


        "WAR": round(WAR,2),


        "WAR_full":
        round(WAR_full,2),


        "level":
        level,


        "recommendation":
        recommendation(level),


        "mask":
        garbage_mask,


        "full_mask":
        combined_mask,


        "roi":
        roi

    }
