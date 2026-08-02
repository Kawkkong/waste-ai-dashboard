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
# Density
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
# MAIN
# ======================================


def analyze_frame(img, camera):


    # -------------------------------
    # Image size
    # -------------------------------

    h,w = img.shape[:2]


    print("----------------")
    print("IMAGE:", w,h)
    print("CAMERA:", camera)





    # -------------------------------
    # Camera config
    # -------------------------------

    if camera not in CAMERA_CONFIG:

        raise ValueError(
            f"Camera {camera} not found in config"
        )


    cfg = CAMERA_CONFIG[camera]


    x1,y1,x2,y2 = cfg["roi"]


    print(
        "ROI:",
        x1,y1,x2,y2
    )





    # -------------------------------
    # YOLO
    # -------------------------------

    result = model(

        img,

        imgsz=640,

        conf=0.25,

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


            # resize เฉพาะ mask
            # ใช้ nearest กัน mask shift


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
    # ROI
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
    # Garbage inside ROI
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



    WAR = 0



    if roi_pixels > 0:

        WAR = (

            garbage_pixels /

            roi_pixels

        ) * 100




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



    # mask สีแดงเข้ม


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





    # ROI BOX


    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,255,0),

        4

    )





    # text


    cv2.putText(

        output,

        f"WAR {WAR}%",

        (30,60),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.5,

        (255,255,255),

        3

    )


    cv2.putText(

        output,

        level,

        (30,120),

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
