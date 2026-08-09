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


/* metric */

[data-testid="stMetricValue"] {

    font-size: 18px;

}


/* image size */

[data-testid="stImage"] img {

    max-height: 420px;

    object-fit: contain;

}


/* dataframe */

.stDataFrame {

    font-size: 12px;

}


/* sidebar */

section[data-testid="stSidebar"] {

    width: 250px !important;

}


</style>
""",
unsafe_allow_html=True
)

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


/* title */

h1 {
    font-size: 26px !important;
}


h2 {
    font-size: 20px !important;
}


h3 {
    font-size: 16px !important;
}


/* metric */

[data-testid="stMetricValue"] {
    font-size: 18px;
}


[data-testid="stMetricLabel"] {
    font-size: 12px;
}


/* image */

[data-testid="stImage"] img {

    max-height: 420px;

    object-fit: contain;

}


/* sidebar */

section[data-testid="stSidebar"] {

    width: 260px !important;

}


/* dataframe */

.stDataFrame {

    font-size: 12px;

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
# SIDEBAR
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

            .get("file_id", None)

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

                    result["action"]

                })



            # =================================================
            # VIDEO
            # =================================================

            elif ext == "mp4":



                temp = tempfile.NamedTemporaryFile(

                    delete=False,

                    suffix=".mp4"

                )


                temp.write(

                    uploaded_file.read()

                )


                temp.close()



                cap = cv2.VideoCapture(

                    temp.name

                )



                frame_id = 0

                results = []

                preview = None



                while True:


                    ret, frame = cap.read()


                    if not ret:

                        break



                    frame_id += 1



                    # วิเคราะห์ทุก 10 frame

                    if frame_id % 10 == 0:



                        result = analyze_frame(

                            frame,

                            cam

                        )



                        results.append({


                            "Frame":

                            frame_id,


                            "WAR":

                            result["WAR"],


                            "Change":

                            result["change"],


                            "Level":

                            result["level"]

                        })


                        preview = result["image"]




                cap.release()



                os.remove(

                    temp.name

                )



                video_df = pd.DataFrame(

                    results

                )



                st.session_state.camera_results[cam] = {


                    "file_id":

                    file_id,


                    "type":

                    "video",


                    "video_data":

                    video_df,


                    "preview":

                    preview

                }



                if len(video_df) > 0:


                    last = video_df.iloc[-1]


                    st.session_state.history.append({


                        "Time":

                        datetime.now().strftime(

                            "%Y-%m-%d %H:%M:%S"

                        ),


                        "Camera":

                        cam,


                        "WAR":

                        last["WAR"],


                        "Change":

                        last["Change"],


                        "Level":

                        last["Level"],


                        "Action":

                        "-"

                    })




# =====================================================
# DISPLAY RESULT
# =====================================================


for cam, data in st.session_state.camera_results.items():


    st.divider()


    st.header(

        f"📷 {cam}"

    )



    # =================================================
    # IMAGE
    # =================================================

    if data["type"] == "image":



        img = data["original"]

        result = data["result"]



        col1, col2 = st.columns(

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

                width=450

            )



        with col2:


            st.subheader(

                "Segmentation Mask"

            )


            st.image(

                cv2.cvtColor(

                    result["image"],

                    cv2.COLOR_BGR2RGB

                ),

                width=450

            )




        # ==============================
        # METRICS
        # ==============================


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





    # =================================================
    # VIDEO
    # =================================================

    elif data["type"] == "video":



        st.subheader(

            "Video Preview"

        )



        if data["preview"] is not None:


            st.image(

                cv2.cvtColor(

                    data["preview"],

                    cv2.COLOR_BGR2RGB

                ),

                width=500

            )



        st.subheader(

            "WAR Trend"

        )


        st.line_chart(

            data["video_data"],

            x="Frame",

            y="WAR"

        )




# =====================================================
# HISTORY TREND
# =====================================================


st.divider()


st.header(

    "📈 WAR Trend Analysis"

)



if len(st.session_state.history) > 0:



    history_df = pd.DataFrame(

        st.session_state.history

    )


    for cam in CAMERA_CONFIG:


        st.subheader(cam)


        cam_df = history_df[

            history_df["Camera"] == cam

        ]



        if len(cam_df) > 0:



            st.line_chart(

                cam_df,

                x="Time",

                y="WAR"

            )


else:


    st.info(

        "ยังไม่มีข้อมูล"

    )



# =====================================================
# HISTORY TABLE
# =====================================================


st.divider()


st.header(

    "📋 Detection History"

)



if len(st.session_state.history) > 0:


    history_df = pd.DataFrame(

        st.session_state.history

    )


    st.dataframe(

        history_df.sort_values(

            "Time",

            ascending=False

        ),

        use_container_width=True

    )


else:


    st.info(

        "ยังไม่มีข้อมูล"

    )
