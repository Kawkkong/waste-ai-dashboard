import streamlit as st

import cv2
import numpy as np
import pandas as pd

import tempfile
import os

from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG



# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Waste AI Dashboard",
    layout="wide"
)



# =====================================================
# CSS COMPACT UI
# =====================================================

st.markdown(
"""
<style>

html, body, [class*="css"] {
    font-size: 13px;
}


h1 {
    font-size: 26px !important;
}


h2 {
    font-size: 20px !important;
}


h3 {
    font-size: 16px !important;
}


[data-testid="stMetricValue"] {
    font-size: 18px !important;
}


[data-testid="stImage"] img {

    max-height:420px;

    object-fit:contain;

}


section[data-testid="stSidebar"] {

    width:260px !important;

}

</style>
""",
unsafe_allow_html=True
)



# =====================================================
# SESSION STATE
# =====================================================

if "camera_results" not in st.session_state:

    st.session_state.camera_results = {}


if "history" not in st.session_state:

    st.session_state.history = []



# =====================================================
# TITLE
# =====================================================

st.title(
    "🗑 Waste AI Dashboard"
)


st.caption(
    "YOLOv11-Seg + Waste Area Ratio (WAR)"
)



# =====================================================
# SIDEBAR UPLOAD
# =====================================================

st.sidebar.header(
    "📷 CCTV Upload"
)



for cam in CAMERA_CONFIG:


    uploaded_file = st.sidebar.file_uploader(

        cam,

        type=[
            "jpg",
            "jpeg",
            "png",
            "mp4"
        ],

        key=cam

    )



    if uploaded_file is not None:


        file_id = (

            uploaded_file.name,

            uploaded_file.size

        )



        old_file = (

            st.session_state.camera_results

            .get(cam, {})

            .get("file_id")

        )



        if file_id != old_file:



            ext = uploaded_file.name.split(".")[-1].lower()



            # =================================================
            # IMAGE
            # =================================================

            if ext in [
                "jpg",
                "jpeg",
                "png"
            ]:



                bytes_data = np.asarray(

                    bytearray(

                        uploaded_file.read()

                    ),

                    dtype=np.uint8

                )


                img = cv2.imdecode(

                    bytes_data,

                    cv2.IMREAD_COLOR

                )



                result = analyze_frame(

                    img,

                    cam

                )



                st.session_state.camera_results[cam] = {


                    "file_id":

                    file_id,


                    "type":

                    "image",


                    "original":

                    img,


                    "result":

                    result

                }



                # ==========================
                # SAVE HISTORY IMAGE
                # ==========================


                st.session_state.history.append({


                    "Time":

                    datetime.now().strftime(

                        "%Y-%m-%d %H:%M:%S"

                    ),


                    "Camera":

                    cam,


                    "WAR":

                    result["WAR"],


                    "Change":

                    result["change"],


                    "Level":

                    result["level"],


                    "Action":

                    result["action"],



                    "Original":

                    img.copy(),



                    "Segmentation":

                    result["image"].copy()

                })






# =====================================================
# DISPLAY CURRENT CAMERA
# =====================================================


for cam,data in st.session_state.camera_results.items():


    st.divider()


    st.header(

        f"📷 {cam}"

    )



    if data["type"] == "image":



        img = data["original"]

        result = data["result"]



        col1,col2 = st.columns(

            [1,1],

            gap="small"

        )



        with col1:


            st.subheader(

                "Original CCTV"

            )


            st.image(

                cv2.cvtColor(

                    img,

                    cv2.COLOR_BGR2RGB

                ),

                width=420

            )




        with col2:


            st.subheader(

                "Segmentation"

            )


            st.image(

                cv2.cvtColor(

                    result["image"],

                    cv2.COLOR_BGR2RGB

                ),

                width=420

            )



        a,b,c,d = st.columns(

            4,

            gap="small"

        )


        a.metric(

            "WAR",

            f'{result["WAR"]}%'

        )


        b.metric(

            "Change",

            f'{result["change"]:+.2f}%'

        )


        c.metric(

            "Density",

            result["level"]

        )


        d.metric(

            "Action",

            result["action"]

        )






# =====================================================
# HISTORY
# =====================================================


st.divider()


st.header(

    "📋 Detection History"

)



if len(st.session_state.history) > 0:



    for i,item in enumerate(

        reversed(st.session_state.history)

    ):



        with st.expander(

            f'{item["Time"]} | {item["Camera"]} | {item["Level"]}'

        ):



            col1,col2 = st.columns(

                [1,1],

                gap="small"

            )



            with col1:


                st.subheader(

                    "Original"

                )


                st.image(

                    cv2.cvtColor(

                        item["Original"],

                        cv2.COLOR_BGR2RGB

                    ),

                    width=350

                )




            with col2:


                st.subheader(

                    "Segmentation"

                )


                st.image(

                    cv2.cvtColor(

                        item["Segmentation"],

                        cv2.COLOR_BGR2RGB

                    ),

                    width=350

                )



            a,b,c,d = st.columns(4)



            a.metric(

                "WAR",

                f'{item["WAR"]}%'

            )


            b.metric(

                "Change",

                f'{item["Change"]:+.2f}%'

            )


            c.metric(

                "Level",

                item["Level"]

            )


            d.metric(

                "Action",

                item["Action"]

            )



else:


    st.info(

        "ยังไม่มีข้อมูล"

    )
