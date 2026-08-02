# ======================================================
# app.py
# Waste AI Dashboard
# YOLOv11-Seg + WAR
# ======================================================


import streamlit as st

import cv2
import numpy as np

import pandas as pd

from datetime import datetime


from inference import predict

from config import CAMERA_CONFIG




# ======================================================
# Page Setting
# ======================================================


st.set_page_config(

    page_title="Waste AI Dashboard",

    page_icon="🗑️",

    layout="wide"

)





# ======================================================
# Session Storage
# ======================================================


if "history" not in st.session_state:

    st.session_state.history=[]





# ======================================================
# Title
# ======================================================


st.title(
    "🗑️ AI Waste Density Monitoring"
)


st.write(
    "YOLOv11-Seg + Waste Area Ratio (WAR)"
)






# ======================================================
# Select Camera
# ======================================================


camera = st.selectbox(

    "เลือกกล้อง",

    list(CAMERA_CONFIG.keys())

)







# ======================================================
# Upload Image
# ======================================================


uploaded_file = st.file_uploader(

    "📷 Upload CCTV Image",

    type=[
        "jpg",
        "jpeg",
        "png"
    ]

)






if uploaded_file:



    # อ่านรูป


    file_bytes = np.asarray(

        bytearray(

            uploaded_file.read()

        ),

        dtype=np.uint8

    )



    img = cv2.imdecode(

        file_bytes,

        cv2.IMREAD_COLOR

    )



    if img is None:


        st.error(
            "อ่านรูปไม่ได้"
        )

        st.stop()






    # ==========================
    # Run YOLO
    # ==========================


    with st.spinner(
        "กำลังประมวลผล YOLO..."
    ):


        result=predict(

            img,

            camera

        )







    # ==========================
    # Dashboard Card
    # ==========================


    st.divider()



    col1,col2,col3,col4 = st.columns(4)



    col1.metric(

        "WAR",

        f'{result["WAR"]}%'

    )


    col2.metric(

        "Density",

        result["level"]

    )


    col3.metric(

        "Camera",

        camera

    )


    col4.metric(

        "Action",

        result["recommendation"]

    )







    # ==========================
    # Alert
    # ==========================


    level=result["level"]



    if level=="Critical":


        st.error(
            "🚨 Critical : ต้องเก็บขยะทันที"
        )


    elif level=="High":


        st.warning(
            "⚠️ High : แจ้งเจ้าหน้าที่"
        )


    elif level=="Medium":


        st.info(
            "ℹ️ Medium : เตรียมจัดเก็บ"
        )


    elif level=="Low":


        st.success(
            "✅ Low : ติดตาม"
        )


    else:


        st.success(
            "✅ Normal : ไม่พบขยะ"
        )







    # ==========================
    # Display Image
    # ==========================


    st.subheader(
        "Segmentation Result"
    )



    output=cv2.cvtColor(

        result["image"],

        cv2.COLOR_BGR2RGB

    )



    st.image(

        output,

        use_container_width=True

    )







    # ==========================
    # Add History
    # ==========================



    st.session_state.history.append({


        "Time":

        datetime.now().strftime(
            "%H:%M:%S"
        ),



        "Camera":

        camera,



        "WAR":

        result["WAR"],



        "Level":

        result["level"]



    })



    st.success(
        "บันทึกข้อมูลแล้ว"
    )









# ======================================================
# Trend Graph
# ======================================================


st.divider()


st.subheader(
    "📈 WAR Trend"
)





if len(st.session_state.history)>0:



    df=pd.DataFrame(

        st.session_state.history

    )



    st.line_chart(

        df,

        x="Time",

        y="WAR"

    )



    st.subheader(
        "📋 Detection History"
    )



    st.dataframe(

        df,

        use_container_width=True

    )



else:


    st.info(

        "ยังไม่มีข้อมูล กรุณา Upload รูป"

    )







# ======================================================
# Clear Data
# ======================================================


st.divider()



if st.button(
    "🗑️ Clear History"
):


    st.session_state.history=[]


    st.success(
        "ล้างข้อมูลแล้ว"
    )


    st.rerun()
