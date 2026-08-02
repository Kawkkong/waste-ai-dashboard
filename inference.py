# ======================================================
# inference.py
# YOLOv11-Seg + ROI + WAR
# ======================================================


from ultralytics import YOLO

import cv2
import numpy as np


from config import CAMERA_CONFIG




# ===============================
# Model
# ===============================


MODEL_PATH = "best.pt"


model = YOLO(
    MODEL_PATH
)






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









# ===============================
# Recommendation
# ===============================


def get_action(level):


    if level=="Normal":

        return "No action"



    elif level=="Low":

        return "Monitor"



    elif level=="Medium":

        return "Prepare collection"



    elif level=="High":

        return "Notify staff"



    else:

        return "Collect immediately"









# ===============================
# Analyze Image
# ===============================


def analyze_frame(img,camera):



    h,w = img.shape[:2]



    cfg = CAMERA_CONFIG[camera]



    x1,y1,x2,y2 = cfg["roi"]





    # ===========================
    # YOLO Segmentation
    # ===========================



    result = model.predict(

        img,

        imgsz=640,

        retina_masks=True,

        verbose=False

    )[0]






    # mask เต็มภาพ

    combined_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )






    if result.masks is not None:



        masks = result.masks.data.cpu().numpy()



        for m in masks:



            # retina_masks ทำให้ mask
            # มีขนาดตรงกับ original image


            combined_mask[

                m > 0.5

            ] = 1






    # ===========================
    # ROI Mask
    # ===========================



    roi_mask = np.zeros(

        (h,w),

        dtype=np.uint8

    )



    roi_mask[

        y1:y2,

        x1:x2

    ] = 1







    # เอาเฉพาะขยะใน ROI


    garbage_mask = (

        combined_mask *

        roi_mask

    )








    # ===========================
    # WAR
    # ===========================


    garbage_pixels = np.sum(

        garbage_mask

    )



    roi_pixels = np.sum(

        roi_mask

    )



    if roi_pixels == 0:


        WAR=0


    else:


        WAR = (

            garbage_pixels /

            roi_pixels

        ) * 100






    WAR = round(

        float(WAR),

        2

    )







    level = get_level(

        WAR,

        cfg["threshold"]

    )






    # ===========================
    # Overlay Mask
    # ===========================



    output = img.copy()



    overlay = img.copy()



    overlay[

        garbage_mask==1

    ] = (

        0,

        0,

        255

    )



    output=cv2.addWeighted(

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






    # ===========================
    # Return
    # ===========================


    return {


        "image":

        output,



        "WAR":

        WAR,



        "level":

        level,



        "recommendation":

        get_action(level)



    }









# ===============================
# Analyze Video
# ===============================


def analyze_video(

        path,

        camera,

        skip=10

):


    cap=cv2.VideoCapture(path)



    results=[]


    frame_id=0






    while True:



        ret,frame = cap.read()



        if not ret:


            break




        frame_id +=1






        if frame_id % skip == 0:



            r = analyze_frame(

                frame,

                camera

            )



            # ไม่เก็บ image
            # เพราะ dataframe พัง


            results.append({


                "Frame":

                frame_id,


                "WAR":

                r["WAR"],


                "Level":

                r["level"]



            })







    cap.release()



    return results
