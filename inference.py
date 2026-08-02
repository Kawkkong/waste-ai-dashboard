# ======================================================
# YOLOv11-Seg Waste Detection
# ROI + Waste Area Ratio
# ======================================================


from ultralytics import YOLO

import cv2
import numpy as np

from config import CAMERA_CONFIG



MODEL_PATH="best.pt"


model = YOLO(
    MODEL_PATH
)





# ==============================
# Level
# ==============================


def density_level(WAR,threshold):


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

        return "No trash"


    elif level=="Low":

        return "Monitor"


    elif level=="Medium":

        return "Prepare collection"


    elif level=="High":

        return "Notify staff"


    else:

        return "Collect immediately"








# ==============================
# Main inference
# ==============================


def analyze_frame(img,camera):


    height,width = img.shape[:2]


    cfg = CAMERA_CONFIG[camera]



    x1,y1,x2,y2 = cfg["roi"]





    # ------------------------------
    # YOLO
    # ------------------------------


    result = model(img)[0]



    combined_mask=np.zeros(

        (height,width),

        dtype=np.uint8

    )





    if result.masks is not None:



        masks=result.masks.data.cpu().numpy()



        for mask in masks:



            mask=cv2.resize(

                mask,

                (width,height)

            )



            combined_mask[

                mask>0.5

            ]=1






    # ------------------------------
    # ROI
    # ------------------------------


    roi_mask=np.zeros(

        (height,width),

        dtype=np.uint8

    )


    roi_mask[

        y1:y2,

        x1:x2

    ]=1





    roi_garbage = (

        combined_mask *

        roi_mask

    )






    # ------------------------------
    # WAR
    # ------------------------------


    garbage_pixels=np.sum(

        roi_garbage

    )


    roi_pixels=np.sum(

        roi_mask

    )



    if roi_pixels:


        WAR=(

            garbage_pixels/

            roi_pixels

        )*100


    else:


        WAR=0






    WAR=round(

        float(WAR),

        2

    )





    level=density_level(

        WAR,

        cfg["threshold"]

    )








    # ------------------------------
    # Visualization
    # ------------------------------


    output=img.copy()



    overlay=img.copy()



    # สีแดง mask ขยะ


    overlay[

        roi_garbage==1

    ]=(

        0,

        0,

        255

    )



    output=cv2.addWeighted(

        img,

        0.5,

        overlay,

        0.5,

        0

    )




    # ROI box


    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,255,0),

        3

    )





    cv2.putText(

        output,

        f"WAR {WAR}% {level}",

        (30,50),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.2,

        (255,255,255),

        3

    )






    return {


        "image":

        output,


        "WAR":

        WAR,


        "level":

        level,


        "recommendation":

        recommendation(level)

    }









# ==============================
# Video
# ==============================


def analyze_video(path,camera,skip=10):


    cap=cv2.VideoCapture(path)


    data=[]


    frame_id=0




    while True:


        ret,frame=cap.read()



        if not ret:

            break



        frame_id+=1





        if frame_id%skip==0:



            result=analyze_frame(

                frame,

                camera

            )



            data.append({

                "Frame":

                frame_id,


                "WAR":

                result["WAR"],


                "Level":

                result["level"]

            })






    cap.release()



    return data
