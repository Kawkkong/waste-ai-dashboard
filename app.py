# ======================================================
# app.py
# Streamlit Dashboard
# ======================================================


import streamlit as st

import cv2
import numpy as np

import pandas as pd

from datetime import datetime


from inference import predict

from config import CAMERA_CONFIG




st.set_page_config(

    page_title="Waste AI Dashboard",

    layout="wide"

)




st.title(
"🗑️ Smart Waste Monitoring Dashboard"
)





# ===============================
# Select Camera
# ===============================


camera = st.selectbox(

    "Select Camera",

    list(
        CAMERA_CONFIG.keys()
    )

)




uploaded = st.file_uploader(

    "Upload CCTV Image",

    type=[
        "jpg",
        "jpeg",
        "png"
    ]

)





if uploaded:



    bytes_data=uploaded.read()



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




    col1,col2,col3=st.columns(3)



    col1.metric(

        "Waste Area Ratio",

        f'{result["WAR"]}%'

    )


    col2.metric(

        "Density Level",

        result["level"]

    )


    col3.metric(

        "Recommendation",

        result["recommendation"]

    )






    st.image(

        cv2.cvtColor(

            result["image"],

            cv2.COLOR_BGR2RGB

        ),

        caption="YOLOv11-Seg Result"

    )





    # ===============================
    # Save History
    # ===============================


    data=pd.DataFrame([{

        "time":
        datetime.now(),

        "camera":
        camera,

        "WAR":
        result["WAR"],

        "level":
        result["level"]

    }])



    data.to_csv(

        "history.csv",

        mode="a",

        header=False,

        index=False

    )
