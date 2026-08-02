import streamlit as st

import cv2
import numpy as np

import pandas as pd

import tempfile


from datetime import datetime


from inference import (

    analyze_frame,

    analyze_video

)


from config import CAMERA_CONFIG





st.set_page_config(

    page_title="Waste AI",

    layout="wide"

)





st.title(
    "🗑️ Waste Density Monitoring"
)



st.caption(
    "YOLOv11-Seg + WAR Dashboard"
)





# -------------------------
# Sidebar
# -------------------------


camera=st.sidebar.selectbox(

    "Select Camera",

    list(CAMERA_CONFIG.keys())

)


mode=st.sidebar.radio(

    "Input",

    [

        "Image",

        "Video"

    ]

)






# เก็บ history


if "history" not in st.session_state:


    st.session_state.history=[]







# =========================
# IMAGE
# =========================


if mode=="Image":



    file=st.file_uploader(

        "Upload Image",

        type=["jpg","png","jpeg"]

    )



    if file:



        bytes_data=np.asarray(

            bytearray(

                file.read()

            ),

            dtype=np.uint8

        )


        img=cv2.imdecode(

            bytes_data,

            1

        )




        result=analyze_frame(

            img,

            camera

        )




        st.session_state.history.append({

            "Time":

            datetime.now().strftime("%H:%M:%S"),


            "Camera":

            camera,


            "WAR":

            result["WAR"],


            "Level":

            result["level"]

        })







        c1,c2,c3=st.columns(3)



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

            camera

        )






        col1,col2=st.columns(

            [2,1]

        )



        with col1:


            st.image(

                cv2.cvtColor(

                    result["image"],

                    cv2.COLOR_BGR2RGB

                ),

                width=600

            )



        with col2:


            st.subheader(

                "Recommendation"

            )


            st.info(

                result["recommendation"]

            )







# =========================
# VIDEO
# =========================


else:



    video=st.file_uploader(

        "Upload Video",

        type=["mp4"]

    )



    if video:



        temp=tempfile.NamedTemporaryFile(

            delete=False,

            suffix=".mp4"

        )


        temp.write(

            video.read()

        )


        temp.close()



        if st.button(

            "Analyze"

        ):



            results=analyze_video(

                temp.name,

                camera

            )


            df=pd.DataFrame(results)



            st.line_chart(

                df,

                x="Frame",

                y="WAR"

            )


            st.dataframe(

                df,

                use_container_width=True

            )







# =========================
# Trend
# =========================


st.divider()


st.subheader(

    "📈 WAR Trend"

)



if len(st.session_state.history)>0:


    df=pd.DataFrame(

        st.session_state.history

    )



    df=df[

        df["Camera"]

        ==camera

    ]



    st.line_chart(

        df,

        x="Time",

        y="WAR"

    )


else:


    st.info(

        "No data"

    )
