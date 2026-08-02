import streamlit as st
import cv2
import pandas as pd
from datetime import datetime

from inference import predict
from config import CAMERA_CONFIG



st.set_page_config(
    layout="wide"
)



st.title(
"🗑️ Smart Waste Monitoring Dashboard"
)



# ===================
# เลือกกล้อง
# ===================


camera=st.selectbox(

"เลือกกล้อง",

[
"camera1",
"camera2"
]

)



st.write(
"Camera:",
CAMERA_CONFIG[camera]["name"]
)




# ===================
# upload
# ===================


file=st.file_uploader(

"Upload CCTV Image",

type=[
"jpg",
"png",
"jpeg"
]

)



if file:


    bytes_data=file.read()


    img=cv2.imdecode(

        np.frombuffer(
            bytes_data,
            np.uint8
        ),

        cv2.IMREAD_COLOR

    )



    result=predict(
        img,
        camera
    )



    WAR=result["WAR"]

    level=result["level"]





    # ==================
    # top cards
    # ==================


    col1,col2,col3=st.columns(3)



    col1.metric(

        "Waste Area Ratio",

        f"{WAR}%"

    )



    col2.metric(

        "Density",

        level

    )



    col3.metric(

        "Action",

        result["recommendation"]

    )





    # ==================
    # mask overlay
    # ==================


    overlay=img.copy()



    overlay[
        result["mask"]==1
    ]=(0,0,255)



    output=cv2.addWeighted(

        img,
        0.7,

        overlay,
        0.3,

        0

    )



    st.image(

        cv2.cvtColor(
            output,
            cv2.COLOR_BGR2RGB
        ),

        caption="Segmentation Result"

    )





    # ==================
    # save history
    # ==================


    data={

    "time":
    datetime.now(),

    "camera":
    camera,

    "WAR":
    WAR,

    "level":
    level

    }



    df=pd.DataFrame([data])


    df.to_csv(

        "history.csv",

        mode="a",

        header=False,

        index=False

    )
