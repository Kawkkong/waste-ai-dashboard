import streamlit as st

import cv2
import numpy as np

import pandas as pd

import tempfile

from datetime import datetime


from inference import analyze_frame, analyze_video


from config import CAMERA_CONFIG





st.set_page_config(

    page_title="Waste AI Dashboard",

    layout="wide"

)





st.title(
    "🗑️ Waste Density Monitoring Dashboard"
)






# ======================
# Session
# ======================


if "history" not in st.session_state:

    st.session_state.history=[]






# ======================
# Sidebar
# ======================


st.sidebar.header(
    "Camera Setting"
)



camera=st.sidebar.selectbox(

    "เลือกกล้อง",

    CAMERA_CONFIG.keys()

)







mode=st.sidebar.radio(

    "Input",

    [

        "Image",

        "Video"

    ]

)








# ======================
# Image Mode
# ======================


if mode=="Image":


    file=st.file_uploader(

        "Upload CCTV Image",

        type=["jpg","png","jpeg"]

    )



    if file:


        img=cv2.imdecode(

            np.frombuffer(

                file.read(),

                np.uint8

            ),

            cv2.IMREAD_COLOR

        )



        result=analyze_frame(

            img,

            camera

        )



        st.session_state.history.append({

            "time":

            datetime.now().strftime("%H:%M:%S"),


            "camera":

            camera,


            "WAR":

            result["WAR"],


            "level":

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




        col1,col2=st.columns(2)



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
                "Statistics"
            )


            df=pd.DataFrame(

                st.session_state.history

            )


            cam=df[df.camera==camera]



            st.metric(

                "Average WAR",

                f'{cam.WAR.mean():.2f}%'

            )


            st.metric(

                "Maximum WAR",

                f'{cam.WAR.max():.2f}%'

            )









# ======================
# Video Mode
# ======================


else:


    file=st.file_uploader(

        "Upload CCTV Video",

        type=["mp4"]

    )


    if file:



        temp=tempfile.NamedTemporaryFile(

            delete=False,

            suffix=".mp4"

        )


        temp.write(

            file.read()

        )


        temp.close()



        if st.button(
            "Analyze Video"
        ):



            results=analyze_video(

                temp.name,

                camera

            )



            df=pd.DataFrame(results)



            st.line_chart(

                df["WAR"]

            )



            st.dataframe(

                df

            )








# ======================
# Trend
# ======================


st.divider()


st.subheader(
    "📈 WAR Trend"
)



if len(st.session_state.history)>0:


    df=pd.DataFrame(

        st.session_state.history

    )


    df=df[df.camera==camera]



    st.line_chart(

        df,

        x="time",

        y="WAR"

    )





else:


    st.info(
        "ยังไม่มีข้อมูล"
    )
