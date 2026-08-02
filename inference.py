from ultralytics import YOLO

import cv2
import numpy as np


from config import CAMERA_CONFIG



MODEL_PATH="best.pt"


model=YOLO(MODEL_PATH)





def get_level(WAR,threshold):


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







def analyze_frame(img,camera):


    h,w=img.shape[:2]


    cfg=CAMERA_CONFIG[camera]


    x1,y1,x2,y2=cfg["roi"]





    result=model(img)[0]



    mask=np.zeros(

        (h,w),

        dtype=np.uint8

    )




    if result.masks is not None:


        masks=result.masks.data.cpu().numpy()



        for m in masks:


            m=cv2.resize(

                m,

                (w,h)

            )


            mask[m>0.5]=1




    roi_mask=np.zeros(

        (h,w),

        dtype=np.uint8

    )



    roi_mask[y1:y2,x1:x2]=1





    garbage=mask*roi_mask




    garbage_pixel=np.sum(
        garbage
    )


    roi_pixel=np.sum(
        roi_mask
    )



    WAR=(

        garbage_pixel/

        roi_pixel

    )*100





    level=get_level(

        WAR,

        cfg["threshold"]

    )





    # overlay


    output=img.copy()



    red=np.zeros_like(img)


    red[garbage==1]=(0,0,255)



    output=cv2.addWeighted(

        img,

        0.7,

        red,

        0.3,

        0

    )



    cv2.rectangle(

        output,

        (x1,y1),

        (x2,y2),

        (0,255,0),

        3

    )



    return {


        "image":output,


        "WAR":round(WAR,2),


        "level":level


    }







def analyze_video(path,camera,skip=10):


    cap=cv2.VideoCapture(path)


    results=[]



    count=0



    while True:


        ret,frame=cap.read()


        if not ret:

            break



        count+=1



        if count%skip==0:


            r=analyze_frame(

                frame,

                camera

            )


            results.append(

                r

            )



    cap.release()


    return results
