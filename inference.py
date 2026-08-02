from ultralytics import YOLO

import cv2
import numpy as np


from config import CAMERA_CONFIG



model = YOLO(
    "best.pt"
)





def get_level(WAR,threshold):


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


    if level=="Normal":

        return "ไม่พบขยะ"


    elif level=="Low":

        return "ติดตาม"


    elif level=="Medium":

        return "เตรียมจัดเก็บ"


    elif level=="High":

        return "แจ้งเจ้าหน้าที่"


    else:

        return "เก็บขยะทันที"








def analyze_frame(img,camera):


    h,w = img.shape[:2]


    cfg = CAMERA_CONFIG[camera]



    x1,y1,x2,y2 = cfg["roi"]






    # ===========================
    # YOLO Segmentation
    # ===========================


    result=model(img)[0]



    combined=np.zeros(

        (h,w),

        dtype=np.uint8

    )




    if result.masks is not None:


        masks=result.masks.data.cpu().numpy()



        for mask in masks:



            mask=cv2.resize(

                mask,

                (w,h)

            )



            combined[

                mask>0.5

            ]=1






    # ===========================
    # ROI
    # ===========================


    roi=np.zeros(

        (h,w),

        dtype=np.uint8

    )


    roi[y1:y2,x1:x2]=1





    garbage=combined*roi





    # ===========================
    # WAR
    # ===========================


    garbage_pixel=np.sum(

        garbage

    )


    roi_pixel=np.sum(

        roi

    )



    WAR=(

        garbage_pixel/

        roi_pixel

    )*100



    WAR=round(

        float(WAR),

        2

    )




    level=get_level(

        WAR,

        cfg["threshold"]

    )







    # ===========================
    # Visualization
    # ===========================


    output=img.copy()



    overlay=img.copy()



    # สีแดง mask


    overlay[

        garbage==1

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






    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,255,0),

        3

    )





    cv2.putText(

        output,

        f"WAR {WAR}%",

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


        "action":

        get_action(level)

    }
