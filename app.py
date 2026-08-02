import streamlit as st

import cv2
import numpy as np

import pandas as pd

import os

from datetime import datetime


from inference import predict

from config import CAMERA_CONFIG



st.set_page_config(

    page_title="Waste AI",

    layout="wide"

)



st.title(
"🗑️ AI Waste Density Monitoring"
)



camera=st.selectbox(

    "เลือกกล้อง",

    list(CAMERA_CONFIG.keys())

)



file=st.file_uploader(

    "Upload CCTV Image",

    type=[
        "jpg",
        "png",
        "jpeg"
    ]

)



if file:



    bytes=file.read()



    img=cv2.imdecode(

        np.frombuffer(

            bytes,

            np.uint8

        ),

        cv2.IMREAD_COLOR

    )



    result=predict(

        img,

        camera

    )



    # ==================
    # Cards
    # ==================


    c1,c2,c3,c4=st.columns(4)



    c1.metric(

        "WAR",

        f'{result["WAR"]}%'

    )


    c2.metric(

        "Level",

        result["level"]

    )


    c3.metric(

        "Camera",

        result["camera"]

    )


    c4.metric(

        "Action",

        result["recommendation"]

    )




    # Alert


    if result["level"]=="Critical":

        st.error(
            "🚨 Critical ต้องเก็บทันที"
        )


    elif result["level"]=="High":

        st.warning(
            "⚠️ High แจ้งเจ้าหน้าที่"
        )


    elif result["level"]=="Medium":

        st.info(
            "ℹ️ Medium"
        )


    else:

        st.success(
            "Normal / Low"
        )





    st.image(

        cv2.cvtColor(

            result["image"],

            cv2.COLOR_BGR2RGB

        ),

        caption="YOLOv11 Segmentation"

    )






    # ==================
    # Save History
    # ==================


    row=pd.DataFrame([{


        "time":
        datetime.now(),


        "camera":
        camera,


        "WAR":
        result["WAR"],


        "level":
        result["level"]


    }])



    row.to_csv(

        "history.csv",

        mode="a",

        header=not os.path.exists(
            "history.csv"
        ),

        index=False

    )






# ==================
# Trend
# ==================


if os.path.exists(
    "history.csv"
):


    st.subheader(
        "📈 WAR Trend"
    )


    df=pd.read_csv(
        "history.csv"
    )


    st.line_chart(

        df["WAR"]

    )
