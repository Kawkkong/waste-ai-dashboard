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

    data = {

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

    return data[level]





# ======================================
# ANALYZE FRAME
# ======================================

def analyze_frame(img, camera):


    # -------------------------------
    # Original image size
    # -------------------------------

    h,w = img.shape[:2]


    print("----------------")
    print("IMAGE:",w,h)
    print("CAMERA:",camera)




    # -------------------------------
    # Camera ROI
    # -------------------------------

    cfg = CAMERA_CONFIG[camera]


    x1,y1,x2,y2 = cfg["roi"]


    print(
        "ROI:",
        x1,y1,x2,y2
    )





    # -------------------------------
    # YOLO SEGMENTATION
    # -------------------------------

    result = model(

        img,

        imgsz=1280,

        conf=0.20,

        retina_masks=True,

        verbose=False

    )[0]





    # -------------------------------
    # Create mask
    # -------------------------------

    combined_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )


    detected = 0



    if result.masks is not None:


        masks = result.masks.data.cpu().numpy()


        detected = len(masks)



        print(
            "Detected masks:",
            detected
        )



        for mask in masks:


            # ถ้า mask size ไม่ตรงภาพ
            # ปรับกลับด้วย nearest


            if mask.shape != (h,w):


                mask = cv2.resize(

                    mask,

                    (w,h),

                    interpolation=cv2.INTER_NEAREST

                )



            combined_mask[

                mask > 0.5

            ] = 1



    else:


        print(
            "No garbage detected"
        )






    # -------------------------------
    # ROI MASK
    # -------------------------------

    roi_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )



    roi_mask[

        y1:y2,

        x1:x2

    ] = 1






    # -------------------------------
    # Garbage in ROI
    # -------------------------------

    roi_garbage = (

        combined_mask *

        roi_mask

    )







    # -------------------------------
    # WAR
    # -------------------------------

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





    level = density_level(

        WAR,

        cfg["threshold"]

    )






    # -------------------------------
    # Visualization
    # -------------------------------

    output = img.copy()


    overlay = img.copy()



    # red mask

    overlay[

        roi_garbage == 1

    ] = (

        0,

        0,

        255

    )



    output = cv2.addWeighted(

        img,

        0.6,

        overlay,

        0.4,

        0

    )





    # ROI rectangle

    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,255,0),

        4

    )





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


        "level":
        level,


        "action":
        recommendation(level),


        "camera":
        camera,


        "detected":
        detected

    }
