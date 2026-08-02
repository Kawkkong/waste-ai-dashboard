from ultralytics import YOLO

import cv2
import numpy as np

from config import CAMERA_CONFIG



# ==========================================
# LOAD MODEL
# ==========================================

model = YOLO(
    "best.pt"
)





# ==========================================
# Density Level
# ==========================================


def get_level(WAR, threshold):


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







# ==========================================
# Recommendation
# ==========================================


def get_action(level):


    if level == "Normal":

        return "No trash"


    elif level == "Low":

        return "Monitor"


    elif level == "Medium":

        return "Prepare collection"


    elif level == "High":

        return "Notify staff"


    else:

        return "Collect immediately"








# ==========================================
# YOLO + WAR
# ==========================================


def analyze_frame(img, camera):


    h,w = img.shape[:2]



    cfg = CAMERA_CONFIG[camera]


    x1,y1,x2,y2 = cfg["roi"]





    # ======================================
    # YOLO SEGMENTATION
    # ======================================


    result = model(

        img,

        retina_masks=True,

        verbose=False

    )[0]





    combined_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )





    if result.masks is not None:



        masks = result.masks.data.cpu().numpy()




        for mask in masks:



            # ไม่ resize แล้ว

            combined_mask[

                mask > 0.5

            ] = 1





    # ======================================
    # ROI MASK
    # ======================================


    roi_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )


    roi_mask[

        y1:y2,

        x1:x2

    ] = 1






    # เฉพาะขยะใน ROI


    roi_garbage = (

        combined_mask *

        roi_mask

    )







    # ======================================
    # WAR
    # ======================================


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





    level = get_level(

        WAR,

        cfg["threshold"]

    )






    # ======================================
    # VISUALIZATION
    # ======================================


    output = img.copy()



    overlay = img.copy()





    # สีแดง mask ขยะ


    overlay[

        roi_garbage == 1

    ] = (

        0,

        0,

        255

    )






    output = cv2.addWeighted(

        img,

        0.5,

        overlay,

        0.5,

        0

    )






    # ROI


    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,255,0),

        3

    )






    # Text


    cv2.putText(

        output,

        f"WAR {WAR}% | {level}",

        (30,50),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.2,

        (255,255,255),

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

        get_action(level)

    }
