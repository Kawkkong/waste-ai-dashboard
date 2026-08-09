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
# STORE PREVIOUS WAR
# ======================================

previous_WAR = {}



# ======================================
# LEVEL
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
# ACTION THAI
# ======================================

def recommendation(level):

    action = {

        "Normal":
        "ไม่พบขยะ",

        "Low":
        "เฝ้าระวังพื้นที่",

        "Medium":
        "เตรียมวางแผนเก็บขยะ",

        "High":
        "แจ้งเตือนเจ้าหน้าที่",

        "Critical":
        "แจ้งเตือนด่วนและดำเนินการเก็บขยะทันที"

    }

    return action[level]




# ======================================
# ANALYZE FRAME
# ======================================

def analyze_frame(img, camera):


    global previous_WAR



    h,w = img.shape[:2]



    cfg = CAMERA_CONFIG[camera]



    x1,y1,x2,y2 = cfg["roi"]




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
    # COMBINE MASK
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
    # ROI MASK
    # ==================================

    roi_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )


    roi_mask[

        y1:y2,

        x1:x2

    ] = 1




    garbage_mask = (

        combined_mask *

        roi_mask

    )





    # ==================================
    # WAR
    # ==================================

    garbage_pixels = np.sum(

        garbage_mask

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
    # CHANGE
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





    # ==================================
    # LEVEL
    # ==================================

    level = density_level(

        WAR,

        cfg["threshold"]

    )





    # ==================================
    # VISUALIZATION
    # ==================================

    # ทำภาพ dim

    dim = cv2.convertScaleAbs(

        img,

        alpha=0.55,

        beta=0

    )



    output = dim.copy()



    # layer mask สีเขียว

    mask_layer = img.copy()



    mask_layer[

        garbage_mask == 1

    ] = (

        0,

        255,

        0

    )



    # ผสมภาพ

    output = cv2.addWeighted(

        dim,

        0.65,

        mask_layer,

        0.35,

        0

    )





    # ==================================
    # ROI RED
    # ==================================

    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,0,255),

        4

    )





    # ==================================
    # TEXT
    # ==================================

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

        garbage_mask,


        "WAR":

        WAR,


        "change":

        change,


        "level":

        level,


        "action":

        recommendation(level),


        "camera":

        camera,


        "detected":

        detected

    }
