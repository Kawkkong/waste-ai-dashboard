# ======================================================
# app.py
# Waste AI Dashboard
# YOLOv11-Seg + WAR + Streamlit
# ======================================================


import streamlit as st

import cv2
import numpy as np

import pandas as pd

import os

from datetime import datetime


from inference import predict

from config import CAMERA_CONFIG





# ======================================================
# Page Config
# ======================================================


st.set_page_config(

    page_title="Waste AI Dashboard",

    page_icon="🗑️",

    layout="wide"

)





# ======================================================
# Title
# ======================================================


st.title(
    "🗑️ AI Waste Density Monitoring"
)


st.caption(
    "YOLOv11-Seg + Waste Area Ratio (WAR)"
)






# ======================================================
# Camera Select
# ======================================================


camera = st.selectbox(

    "เลือกกล้อง",

    list(CAMERA_CONFIG.keys())

)






# ======================================================
# Upload Image
# ======================================================


uploaded_file = st.file_uploader(

    "Upload CCTV Image",

    type=[
        "jpg",
        "jpeg",
        "png"
    ]

)






if uploaded_file:



    # อ่านภาพ


    bytes_data = uploaded_file.read()



    img = cv2.imdecode(

        np.frombuffer(

            bytes_data,

            np.uint8

        ),

        cv2.IMREAD_COLOR

    )



    if img is None:


        st.error(
            "ไม่สามารถอ่านรูปภาพได้"
        )


        st.stop()






    # ==============================
    # Run YOLO
    # ==============================


    with st.spinner(
        "กำลังวิเคราะห์..."
    ):


        result = predict(

            img,

            camera

        )







    # ==============================
    # Dashboard Cards
    # ==============================



    col1,col2,col3,col4 = st.columns(4)




    col1.metric(

        "Waste Area Ratio",

        f'{result["WAR"]}%'

    )



    col2.metric(

        "Density Level",

        result["level"]

    )



    col3.metric(

        "Camera",

        camera

    )



    col4.metric(

        "Recommendation",

        result["recommendation"]

    )






    # ==============================
    # Alert
    # ==============================


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
            "✅ Low : ติดตามสถานการณ์"
        )



    else:


        st.success(
            "✅ Normal : ไม่พบขยะ"
        )






    # ==============================
    # Image Result
    # ==============================


    st.subheader(
        "Segmentation Result"
    )



    result_img=cv2.cvtColor(

        result["image"],

        cv2.COLOR_BGR2RGB

    )



    st.image(

        result_img,

        use_container_width=True

    )






    # ==============================
    # Save History
    # ==============================


    history_row=pd.DataFrame([{


        "time":

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),



        "camera":

        camera,



        "WAR":

        result["WAR"],



        "level":

        result["level"]


    }])





    file_exists=os.path.exists(
        "history.csv"
    )



    history_row.to_csv(

        "history.csv",

        mode="a",

        header=not file_exists,

        index=False

    )



    st.success(
        "บันทึกผลเรียบร้อย"
    )







# ======================================================
# History Section
# ======================================================


st.divider()


st.subheader(
    "📈 WAR Trend"
)





if os.path.exists(
    "history.csv"
):



    try:


        df=pd.read_csv(

            "history.csv"

        )



        # ตรวจ column


        if "WAR" in df.columns:



            if len(df)>0:



                st.line_chart(

                    df["WAR"]

                )



                st.dataframe(

                    df,

                    use_container_width=True

                )



            else:


                st.info(
                    "ยังไม่มีข้อมูล"
                )



        else:


            st.warning(
                "history.csv ไม่มี column WAR"
            )



    except Exception as e:


        st.warning(
            f"อ่าน history ไม่สำเร็จ: {e}"
        )



else:


    st.info(
        "ยังไม่มีประวัติการตรวจจับ"
    )







# ======================================================
# Clear History
# ======================================================


st.divider()


if st.button(
    "🗑️ Clear History"
):


    if os.path.exists(
        "history.csv"
    ):


        os.remove(
            "history.csv"
        )


        st.success(
            "ลบประวัติแล้ว"
        )


        st.rerun()



    else:


        st.info(
            "ไม่มีไฟล์ history"
        )
