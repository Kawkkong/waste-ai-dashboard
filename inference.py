# ======================================================
# inference.py
# YOLOv11-Seg + ROI + WAR
# ======================================================


from ultralytics import YOLO

import cv2
import numpy as np

from config import CAMERA_CONFIG



MODEL_PATH = "best.pt"


model = YOLO(MODEL_PATH)




# ===============================
# Density Classification
# ===============================


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


    if level=="Normal":

        return "No action"


    elif level=="Low":

        return "Monitor"


    elif level=="Medium":

        return "Prepare collection"


    elif level=="High":

        return "Notify staff"


    else:

        return "Urgent collection"






# ===============================
# Main Prediction
# ===============================


def predict(image,camera):


    height,width=image.shape[:2]



    cam = CAMERA_CONFIG[camera]



    roi = cam["roi"]



    x1=roi["x1"]
    y1=roi["y1"]

    x2=roi["x2"]
    y2=roi["y2"]




    # ===============================
    # YOLO Segmentation
    # ===============================


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





    # ===============================
    # ROI Mask
    # ===============================


    roi_mask=np.zeros(
        (height,width),
        dtype=np.uint8
    )


    roi_mask[
        y1:y2,
        x1:x2
    ]=1




    garbage_mask=(

        combined_mask *
        roi_mask

    )





    # ===============================
    # WAR
    # ===============================


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





    # ===============================
    # Output Image
    # ===============================


    output=image.copy()



    output[
        garbage_mask==1
    ]=(0,0,255)



    output=cv2.addWeighted(

        image,

        0.7,

        output,

        0.3,

        0

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


        "mask":
        garbage_mask,


        "camera":
        cam["name"]

    }
