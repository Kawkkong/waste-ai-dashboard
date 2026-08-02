# ======================================================
# inference.py
# YOLOv11-Seg + ROI + WAR
# Same pipeline as Colab
# ======================================================


from ultralytics import YOLO
import cv2
import numpy as np

from config import CAMERA_CONFIG



# ===============================
# Load Model
# ===============================


MODEL_PATH = "best.pt"


model = YOLO(MODEL_PATH)





# ===============================
# Density Level
# ===============================


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






def get_action(level):


    if level == "Normal":

        return "No action"


    elif level == "Low":

        return "Monitor"


    elif level == "Medium":

        return "Prepare collection"


    elif level == "High":

        return "Notify staff"


    else:

        return "Collect immediately"








# ===============================
# Image Analysis
# ===============================


def analyze_frame(img, camera):


    height, width = img.shape[:2]


    cfg = CAMERA_CONFIG[camera]



    x1,y1,x2,y2 = cfg["roi"]





    # ===========================
    # YOLO Segmentation
    # ===========================


    result = model(img)[0]



    combined_mask = np.zeros(

        (height,width),

        dtype=np.uint8

    )





    if result.masks is not None:


        masks = result.masks.data.cpu().numpy()



        for mask in masks:



            mask = cv2.resize(

                mask,

                (width,height)

            )



            combined_mask[

                mask > 0.5

            ] = 1





    # ===========================
    # Full Image WAR
    # ===========================


    full_pixels = height * width


    full_garbage = np.sum(

        combined_mask

    )


    WAR_full = (

        full_garbage /

        full_pixels

    ) * 100







    # ===========================
    # ROI Mask
    # ===========================


    roi_area = np.zeros(

        (height,width),

        dtype=np.uint8

    )


    roi_area[

        y1:y2,

        x1:x2

    ] = 1





    roi_garbage_mask = (

        combined_mask *

        roi_area

    )






    # ===========================
    # ROI WAR
    # ===========================


    garbage_pixels = np.sum(

        roi_garbage_mask

    )


    roi_pixels = np.sum(

        roi_area

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







    # ===========================
    # Visualization
    # ===========================


    output = img.copy()



    overlay = img.copy()



    overlay[

        roi_garbage_mask == 1

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

        3

    )






    return {


        "image":

        output,


        "WAR":

        WAR,


        "WAR_full":

        round(

            float(WAR_full),

            2

        ),


        "level":

        level,


        "recommendation":

        get_action(level)

    }








# ===============================
# Video Analysis
# ===============================


def analyze_video(path, camera, skip=10):


    cap=cv2.VideoCapture(path)



    results=[]


    frame_id=0





    while True:


        ret,frame = cap.read()



        if not ret:

            break





        frame_id += 1




        if frame_id % skip == 0:



            result = analyze_frame(

                frame,

                camera

            )




            results.append({


                "Frame":

                frame_id,


                "WAR":

                result["WAR"],


                "Level":

                result["level"]


            })






    cap.release()



    return results
