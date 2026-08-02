from ultralytics import YOLO

import cv2
import numpy as np

from config import CAMERA_CONFIG



# =====================================================
# MODEL
# =====================================================

model = YOLO(
    "best.pt"
)





# =====================================================
# LETTERBOX
# =====================================================

def letterbox(
    img,
    new_shape=(1920,1080)
):

    target_w, target_h = new_shape


    h,w = img.shape[:2]


    ratio = min(
        target_w / w,
        target_h / h
    )


    new_w = int(w * ratio)
    new_h = int(h * ratio)



    resized = cv2.resize(

        img,

        (new_w,new_h),

        interpolation=cv2.INTER_LINEAR

    )



    canvas = np.zeros(

        (target_h,target_w,3),

        dtype=np.uint8

    )



    dx = (target_w-new_w)//2
    dy = (target_h-new_h)//2



    canvas[

        dy:dy+new_h,

        dx:dx+new_w

    ] = resized



    return canvas






# =====================================================
# LEVEL
# =====================================================


def density_level(
    WAR,
    threshold
):


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


    table={

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


    return table[level]







# =====================================================
# ANALYZE
# =====================================================


def analyze_frame(
    img,
    camera
):


    # ---------------------------------
    # Keep aspect ratio
    # ---------------------------------

    img = letterbox(
        img,
        (1920,1080)
    )


    h,w = img.shape[:2]





    # ---------------------------------
    # CAMERA ROI
    # ---------------------------------

    cfg = CAMERA_CONFIG[camera]


    x1,y1,x2,y2 = cfg["roi"]







    # ---------------------------------
    # YOLO
    # ---------------------------------


    result = model(

        img,

        imgsz=640,

        conf=0.25,

        retina_masks=True,

        verbose=False

    )[0]






    # ---------------------------------
    # MASK
    # ---------------------------------


    combined_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )




    if result.masks is not None:



        masks = result.masks.data.cpu().numpy()



        for mask in masks:


            combined_mask[

                mask > 0.5

            ] = 1







    # ---------------------------------
    # ROI MASK
    # ---------------------------------


    roi_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )


    roi_mask[

        y1:y2,

        x1:x2

    ] = 1






    # ---------------------------------
    # ROI GARBAGE
    # ---------------------------------


    roi_garbage = (

        combined_mask *

        roi_mask

    )






    # ---------------------------------
    # WAR
    # ---------------------------------


    garbage_pixels = np.sum(

        roi_garbage

    )


    roi_pixels = np.sum(

        roi_mask

    )



    if roi_pixels != 0:


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








    # ---------------------------------
    # DISPLAY MASK
    # ---------------------------------


    output = img.copy()



    overlay = img.copy()



    # สีแดงเข้ม


    overlay[

        roi_garbage == 1

    ] = (

        0,

        0,

        255

    )




    output = cv2.addWeighted(

        img,

        0.55,

        overlay,

        0.45,

        0

    )





    # ROI BOX


    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,255,0),

        4

    )





    # TEXT


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


        "original":

        img,


        "mask":

        roi_garbage,


        "WAR":

        WAR,


        "level":

        level,


        "action":

        recommendation(level)

    }
