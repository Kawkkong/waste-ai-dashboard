from ultralytics import YOLO
import cv2
import numpy as np

from config import CAMERA_CONFIG



MODEL_PATH="best.pt"


model = YOLO(MODEL_PATH)



def density_level(WAR, threshold):


    if WAR == 0:

        return "No Garbage"


    elif WAR <= threshold["Low"]:

        return "Low"


    elif WAR <= threshold["Medium"]:

        return "Medium"


    elif WAR <= threshold["High"]:

        return "High"


    else:

        return "Critical"





def predict(image, camera_id):


    height,width=image.shape[:2]


    cam = CAMERA_CONFIG[camera_id]



    # =============================
    # YOLO Segmentation
    # =============================


    result=model(image)[0]


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



    # =============================
    # ROI
    # =============================


    roi=cam["roi"]


    roi_area=np.zeros(
        (height,width),
        dtype=np.uint8
    )


    roi_area[
        roi["y1"]:roi["y2"],
        roi["x1"]:roi["x2"]
    ]=1



    roi_mask = (
        combined_mask *
        roi_area
    )



    # =============================
    # WAR
    # =============================


    garbage_pixel=np.sum(
        roi_mask
    )


    roi_pixel=np.sum(
        roi_area
    )


    WAR=(
        garbage_pixel /
        roi_pixel
    )*100



    level=density_level(
        WAR,
        cam["threshold"]
    )



    # =============================
    # Visualization
    # =============================


    output=image.copy()


    output[
        roi_mask==1
    ]=(
        0,
        0,
        255
    )


    output=cv2.addWeighted(
        image,
        0.7,
        output,
        0.3,
        0
    )



    return {

        "WAR":round(WAR,2),

        "level":level,

        "image":output,

        "camera":cam["name"]

    }