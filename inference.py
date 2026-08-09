from ultralytics import YOLO
import cv2
import numpy as np

from config import CAMERA_CONFIG


# ======================================
# LOAD MODEL
# ======================================

MODEL_PATH = "best.pt"

model = YOLO(MODEL_PATH)


# ======================================
# Store Previous WAR
# ======================================

previous_WAR = {}



# ======================================
# Density Level
# ======================================

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



# ======================================
# Recommendation
# ======================================

def recommendation(level):

    action = {

        "Normal":
        "No trash",

        "Low":
        "Monitor",

        "Medium":
        "Prepare collection",

        "High":
        "Notify staff",

        "Critical":
        "Collect immediately"

    }

    return action[level]



# ======================================
# ANALYZE FRAME
# ======================================

def analyze_frame(img, camera):

    global previous_WAR


    h, w = img.shape[:2]


    # ==================================
    # Camera ROI
    # ==================================

    cfg = CAMERA_CONFIG[camera]


    x1, y1, x2, y2 = cfg["roi"]



    # ==================================
    # YOLO SEGMENTATION
    # ==================================

    result = model(
        img,
        imgsz=1280,
        conf=0.30,
        retina_masks=True,
        verbose=False
    )[0]



    # ==================================
    # Create Full Mask
    # ==================================

    combined_mask = np.zeros(
        (h,w),
        dtype=np.uint8
    )


    detected = 0



    if result.masks is not None:


        masks = result.masks.data.cpu().numpy()


        detected = len(masks)



        for mask in masks:


            if mask.shape != (h,w):

                mask = cv2.resize(
                    mask,
                    (w,h),
                    interpolation=cv2.INTER_NEAREST
                )


            combined_mask[
                mask > 0.5
            ] = 1



    # ==================================
    # ROI Mask
    # ==================================

    roi_mask = np.zeros(
        (h,w),
        dtype=np.uint8
    )


    roi_mask[
        y1:y2,
        x1:x2
    ] = 1



    # ==================================
    # Garbage inside ROI
    # ==================================

    roi_garbage = (
        combined_mask *
        roi_mask
    )



    # ==================================
    # WAR Calculation
    # ==================================

    garbage_pixels = np.sum(
        roi_garbage
    )


    roi_pixels = np.sum(
        roi_mask
    )



    if roi_pixels > 0:

        WAR = (
            garbage_pixels /
            roi_pixels
        ) * 100

    else:

        WAR = 0



    WAR = round(
        float(WAR),
        2
    )



    # ==================================
    # WAR Change
    # ==================================

    change = 0



    if camera in previous_WAR:

        change = (
            WAR -
            previous_WAR[camera]
        )


    previous_WAR[camera] = WAR


    change = round(
        float(change),
        2
    )



    if change > 0:

        trend = f"Increase +{change}%"

    elif change < 0:

        trend = f"Decrease {change}%"

    else:

        trend = "No change"



    # ==================================
    # Density
    # ==================================

    level = density_level(
        WAR,
        cfg["threshold"]
    )



    # ==================================
    # Visualization
    # ==================================

    output = img.copy()


    overlay = img.copy()



    # ===============================
    # GREEN MASK
    # ===============================

    overlay[
        roi_garbage == 1
    ] = (
        0,
        255,
        0
    )



    # Blend image + mask

    output = cv2.addWeighted(
        img,
        0.5,
        overlay,
        0.5,
        0
    )



    # ===============================
    # ROI Rectangle (Yellow)
    # ===============================

    cv2.rectangle(
        output,
        (x1,y1),
        (x2,y2),
        (0,255,255),
        4
    )



    # ===============================
    # Text
    # ===============================

    cv2.putText(
        output,
        f"WAR {WAR}%",
        (40,60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (255,255,255),
        3
    )


    cv2.putText(
        output,
        level,
        (40,120),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0,255,255),
        3
    )



    return {


        "image":
        output,


        "mask":
        roi_garbage,


        "WAR":
        WAR,


        "change":
        change,


        "trend":
        trend,


        "level":
        level,


        "action":
        recommendation(level),


        "camera":
        camera,


        "detected":
        detected

    }
