# ======================================================
# inference.py
# YOLOv11 Segmentation + WAR
# ======================================================


from ultralytics import YOLO

import cv2
import numpy as np

from config import CAMERA_CONFIG



MODEL_PATH="best.pt"


model=YOLO(MODEL_PATH)





# ==============================
# Density
# ==============================


def classify_density(WAR,threshold):


    if WAR==0:

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


    text={

        "Normal":
        "ไม่พบขยะ",


        "Low":
        "ติดตามสถานการณ์",


        "Medium":
        "เตรียมจัดเก็บ",


        "High":
        "แจ้งเจ้าหน้าที่",


        "Critical":
        "เก็บทันที"

    }


    return text[level]






# ==============================
# Visualization
# ==============================


def create_overlay(
        image,
        mask,
        roi):


    output=image.copy()



    # mask สีแดงสด


    color=np.zeros_like(
        image
    )


    color[mask==1]=(
        0,
        0,
        255
    )



    output=cv2.addWeighted(

        image,

        0.55,

        color,

        0.45,

        0

    )



    # contour สีเหลือง


    contours,_=cv2.findContours(

        mask,

        cv2.RETR_EXTERNAL,

        cv2.CHAIN_APPROX_SIMPLE

    )


    cv2.drawContours(

        output,

        contours,

        -1,

        (0,255,255),

        3

    )



    # ROI


    cv2.rectangle(

        output,

        (
        roi["x1"],
        roi["y1"]
        ),

        (
        roi["x2"],
        roi["y2"]
        ),

        (0,255,0),

        4

    )



    return output







# ==============================
# Main Predict
# ==============================


def predict(
        image,
        camera):



    height,width=image.shape[:2]



    cam=CAMERA_CONFIG[camera]

    roi=cam["roi"]




    # =========================
    # YOLO
    # =========================


    result=model(image)[0]



    combined_mask=np.zeros(

        (height,width),

        dtype=np.uint8

    )




    if result.masks is not None:



        polygons=result.masks.xy



        for poly in polygons:


            poly=poly.astype(
                np.int32
            )


            cv2.fillPoly(

                combined_mask,

                [poly],

                1

            )





    # =========================
    # ROI
    # =========================


    roi_mask=np.zeros(

        (height,width),

        dtype=np.uint8

    )


    roi_mask[

        roi["y1"]:roi["y2"],

        roi["x1"]:roi["x2"]

    ]=1




    garbage_mask=(

        combined_mask *

        roi_mask

    )





    # =========================
    # WAR
    # =========================


    garbage_pixels=np.sum(
        garbage_mask
    )


    roi_pixels=np.sum(
        roi_mask
    )


    WAR=(

        garbage_pixels /

        roi_pixels

    )*100






    level=classify_density(

        WAR,

        cam["threshold"]

    )





    output=create_overlay(

        image,

        garbage_mask,

        roi

    )




    return {


        "WAR":
        round(WAR,2),


        "level":
        level,


        "recommendation":
        recommendation(level),


        "image":
        output,


        "camera":
        cam["name"]

    }
