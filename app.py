# ======================================================
# app.py
# Waste AI Dashboard
# YOLOv11-Seg + WAR
# ======================================================


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





# ======================================================
# Page Config
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
# Header
# ======================================================


st.title(
    "🗑️ Waste Density Monitoring"
)


st.caption(
    "YOLOv11-Seg + Waste Area Ratio (WAR)"
)






# ======================================================
# Sidebar
# ======================================================


st.sidebar.header(
    "Camera Setting"
)



camera = st.sidebar.selectbox(

    "เลือกกล้อง",

    list(CAMERA_CONFIG.keys())

)





mode = st.sidebar.radio(

    "Input Type",

    [

        "Image",

        "Video"

    ]

)





st.sidebar.divider()



if st.sidebar.button(
    "Clear History"
):


    st.session_state.history=[]


    st.rerun()







# ======================================================
# IMAGE MODE
# ======================================================


if mode=="Image":



    uploaded = st.file_uploader(

        "Upload CCTV Image",

        type=[

            "jpg",

            "jpeg",

            "png"

        ]

    )



    if uploaded:



        file_bytes=np.asarray(

            bytearray(

                uploaded.read()

            ),

            dtype=np.uint8

        )



        img=cv2.imdecode(

            file_bytes,

            cv2.IMREAD_COLOR

        )



        if img is None:


            st.error(
                "ไม่สามารถอ่านภาพได้"
            )


            st.stop()






        with st.spinner(

            "กำลังประมวลผล..."

        ):


            result=analyze_frame(

                img,

                camera

            )








        # ==========================
        # Save History
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









        # ==========================
        # Metrics
        # ==========================


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

            camera

        )



        c4.metric(

            "Action",

            result["recommendation"]

        )







        # ==========================
        # Alert
        # ==========================


        if result["level"]=="Critical":


            st.error(

                "🚨 Critical : เก็บขยะทันที"

            )


        elif result["level"]=="High":


            st.warning(

                "⚠️ High : แจ้งเจ้าหน้าที่"

            )


        elif result["level"]=="Medium":


            st.info(

                "ℹ️ Medium : เตรียมจัดเก็บ"

            )


        elif result["level"]=="Low":


            st.success(

                "✅ Low : ติดตาม"

            )


        else:


            st.success(

                "✅ Normal : ไม่พบขยะ"

            )







        # ==========================
        # Layout
        # ==========================


        col_img,col_stat = st.columns(

            [2,1]

        )



        with col_img:



            st.subheader(

                "Segmentation"

            )


            st.image(

                cv2.cvtColor(

                    result["image"],

                    cv2.COLOR_BGR2RGB

                ),

                width=550

            )





        with col_stat:



            st.subheader(

                "Camera Statistics"

            )


            df=pd.DataFrame(

                st.session_state.history

            )



            cam_df=df[

                df["Camera"]

                ==

                camera

            ]




            st.metric(

                "Average WAR",

                f'{cam_df["WAR"].mean():.2f}%'

            )



            st.metric(

                "Maximum WAR",

                f'{cam_df["WAR"].max():.2f}%'

            )



            st.metric(

                "Samples",

                len(cam_df)

            )









# ======================================================
# VIDEO MODE
# ======================================================


else:



    uploaded=st.file_uploader(

        "Upload CCTV Video",

        type=["mp4"]

    )




    if uploaded:



        temp=tempfile.NamedTemporaryFile(

            delete=False,

            suffix=".mp4"

        )


        temp.write(

            uploaded.read()

        )


        temp.close()





        if st.button(

            "Analyze Video"

        ):



            with st.spinner(

                "กำลังวิเคราะห์ Video..."

            ):


                results=analyze_video(

                    temp.name,

                    camera

                )





            df=pd.DataFrame(

                results

            )




            df["WAR"]=df["WAR"].astype(float)



            st.subheader(

                "Video WAR Trend"

            )



            st.line_chart(

                df,

                x="Frame",

                y="WAR"

            )




            st.subheader(

                "Video Result"

            )


            st.dataframe(

                df,

                use_container_width=True

            )








# ======================================================
# Overall Trend
# ======================================================


st.divider()



st.subheader(

    "📈 Camera WAR Trend"

)





if len(st.session_state.history)>0:



    df=pd.DataFrame(

        st.session_state.history

    )



    camera_df=df[

        df["Camera"]

        ==

        camera

    ]



    st.line_chart(

        camera_df,

        x="Time",

        y="WAR"

    )




    with st.expander(

        "ดูข้อมูลทั้งหมด"

    ):


        st.dataframe(

            camera_df,

            use_container_width=True

        )




else:


    st.info(

        "ยังไม่มีข้อมูล"

    )
