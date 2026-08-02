from ultralytics import YOLO

import cv2
import numpy as np

from config import CAMERA_CONFIG



# =====================================================
# LOAD MODEL
# =====================================================

MODEL_PATH = "best.pt"

model = YOLO(MODEL_PATH)




# =====================================================
# RESIZE INPUT TO CCTV STANDARD
# =====================================================


def resize_to_cctv(img):

    TARGET_W = 1920
    TARGET_H = 1080


    h,w = img.shape[:2]


    if w == TARGET_W and h == TARGET_H:

        return img



    img = cv2.resize(

        img,

        (TARGET_W,TARGET_H),

        interpolation=cv2.INTER_LINEAR

    )


    return img





# =====================================================
# DENSITY CLASS
# =====================================================


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





# =====================================================
# ACTION
# =====================================================


def recommendation(level):


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






# =====================================================
# MAIN ANALYSIS
# =====================================================


def analyze_frame(img, camera):



    # -------------------------------------
    # Resize to CCTV resolution
    # -------------------------------------

    img = resize_to_cctv(img)



    h,w = img.shape[:2]




    # -------------------------------------
    # Camera Config
    # -------------------------------------


    cfg = CAMERA_CONFIG[camera]



    x1,y1,x2,y2 = cfg["roi"]





    # -------------------------------------
    # YOLO SEGMENTATION
    # -------------------------------------


    result = model(

        img,

        imgsz=640,

        conf=0.25,

        verbose=False

    )[0]





    combined_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )





    if result.masks is not None:



        masks = result.masks.data.cpu().numpy()



        for mask in masks:



            mask = cv2.resize(

                mask,

                (w,h)

            )



            combined_mask[

                mask > 0.5

            ] = 1




    # -------------------------------------
    # ROI MASK
    # -------------------------------------


    roi_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )


    roi_mask[

        y1:y2,

        x1:x2

    ] = 1




    # -------------------------------------
    # Garbage inside ROI
    # -------------------------------------


    roi_garbage = (

        combined_mask *

        roi_mask

    )






    # -------------------------------------
    # WAR
    # -------------------------------------


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






    # -------------------------------------
    # Visualization
    # -------------------------------------


    output = img.copy()



    overlay = img.copy()



    # สีแดง mask


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





    # Text


    cv2.putText(

        output,

        f"WAR: {WAR}%",

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


        "original":

        img,


        "mask":

        roi_garbage,


        "WAR":

        WAR,


        "level":

        level,


        "action":

        recommendation(level),


        "size":

        f"{w}x{h}"

    }
