import streamlit as st
import cv2
import numpy as np

from inference import predict
from config import CAMERA_CONFIG



st.set_page_config(
    page_title="Waste AI Dashboard",
    layout="wide"
)



st.title(
"🗑️ AI Waste Density Monitoring"
)



camera_id = st.selectbox(
    "เลือกกล้อง",
    list(CAMERA_CONFIG.keys())
)



uploaded = st.file_uploader(
    "Upload CCTV Image",
    type=[
        "jpg",
        "png",
        "jpeg"
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
        camera_id
    )



    col1,col2,col3=st.columns(3)


    with col1:

        st.metric(
            "WAR",
            f'{result["WAR"]}%'
        )


    with col2:

        st.metric(
            "Density",
            result["level"]
        )


    with col3:

        st.metric(
            "Camera",
            result["camera"]
        )



    st.image(
        cv2.cvtColor(
            result["image"],
            cv2.COLOR_BGR2RGB
        ),
        caption="Segmentation Result"
    )