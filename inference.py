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
# Fixed CCTV Size
# ======================================

IMG_WIDTH = 1920
IMG_HEIGHT = 1080



# ======================================
# Store Previous WAR
# ======================================

previous_WAR = {}



# ======================================
# Density Level
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
# Analyze Frame
# ======================================

def analyze_frame(img, camera):


    global previous_WAR



    # ==================================
    # Check Image Size
    # ==================================

    h,w = img.shape[:2]


    if w != IMG_WIDTH or h != IMG_HEIGHT:

        raise ValueError(
            f"Image must be 1920x1080 but got {w}x{h}"
        )



    print("----------------")
    print("IMAGE:", w,h)
    print("CAMERA:", camera)




    # ==================================
    # Camera ROI
    # ==================================

    cfg = CAMERA_CONFIG[camera]


    x1,y1,x2,y2 = cfg["roi"]



    print(
        "ROI:",
        x1,y1,x2,y2
    )





    # ==================================
    # YOLO Segmentation
    # ==================================

    result = model(

        img,

        imgsz=1280,

        conf=0.50,

        retina_masks=True,

        verbose=False

    )[0]





    # ==================================
    # Create Full Mask
    # ==================================

    combined_mask = np.zeros(

        (IMG_HEIGHT, IMG_WIDTH),

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


            mask = cv2.resize(

                mask,

                (IMG_WIDTH, IMG_HEIGHT),

                interpolation=cv2.INTER_NEAREST

            )



            combined_mask[

                mask > 0.5

            ] = 1



    else:

        print(
            "No garbage detected"
        )






    # ==================================
    # ROI Mask
    # ==================================

    roi_mask = np.zeros(

        (IMG_HEIGHT, IMG_WIDTH),

        dtype=np.uint8

    )


    roi_mask[

        y1:y2,

        x1:x2

    ] = 1





    # ==================================
    # Garbage in ROI
    # ==================================

    roi_garbage = (

        combined_mask *

        roi_mask

    )





    # ==================================
    # WAR
    # ==================================

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





    # ==================================
    # Compare Previous Frame
    # ==================================

    change = 0



    if camera in previous_WAR:


        old_WAR = previous_WAR[camera]


        if old_WAR > 0:


            change = (

                (WAR - old_WAR)

                /

                old_WAR

            ) * 100



    previous_WAR[camera] = WAR



    change = round(

        float(change),

        2

    )





    # ==================================
    # Trend
    # ==================================

    if change > 0:

        trend = f"Increase +{change}%"

    elif change < 0:

        trend = f"Decrease {change}%"

    else:

        trend = "No change"






    # ==================================
    # Level
    # ==================================

    level = density_level(

        WAR,

        cfg["threshold"]

    )






    # ==================================
    # Visualization
    # ==================================

    output = img.copy()


    overlay = img.copy()



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





    # ROI Box

    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,255,0),

        4

    )





    # WAR

    cv2.putText(

        output,

        f"WAR {WAR}%",

        (40,60),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.5,

        (255,255,255),

        3

    )





    # Change

    cv2.putText(

        output,

        trend,

        (40,120),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.5,

        (0,255,255),

        3

    )





    # Level

    cv2.putText(

        output,

        level,

        (40,180),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.5,

        (0,255,0),

        3

    )






    return {


        "image":

        output,



        "mask":

        roi_garbage,



        "WAR":

        WAR,



        "change":

        change,



        "trend":

        trend,



        "level":

        level,



        "action":

        recommendation(level),



        "camera":

        camera,



        "detected":

        detected

    }
