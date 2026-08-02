import streamlit as st


import cv2

import numpy as np

import pandas as pd


from datetime import datetime



from inference import analyze_frame


from config import CAMERA_CONFIG






st.set_page_config(

    page_title="Waste AI Dashboard",

    layout="wide"

)






st.title(

"🗑 Dashboard ระบบตรวจจับและจำแนกระดับความหนาแน่นของกองขยะจากภาพ CCTV"

)



st.caption(

"YOLOv11-Seg + Waste Area Ratio (WAR)"

)








uploaded_files={}





st.sidebar.header(

"Upload Camera Image"

)



for cam in CAMERA_CONFIG:


    uploaded_files[cam]=st.sidebar.file_uploader(

        cam,

        type=[

            "jpg",

            "png",

            "jpeg"

        ],

        key=cam

    )







history=[]





# ==================================================
# CAMERA DISPLAY
# ==================================================


for cam,file in uploaded_files.items():



    if file is not None:



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

            cam

        )





        history.append({

            "Time":

            datetime.now().strftime("%H:%M:%S"),


            "Camera":

            cam,


            "WAR":

            result["WAR"],


            "Level":

            result["level"],


            "Action":

            result["action"]

        })







        st.divider()



        st.subheader(

            f"📷 {cam} : {CAMERA_CONFIG[cam]['name']}"

        )





        c1,c2=st.columns(2)





        with c1:


            st.write(

            "ภาพจากกล้อง CCTV"

            )


            st.image(

                cv2.cvtColor(

                    img,

                    cv2.COLOR_BGR2RGB

                ),

                width=500

            )






        with c2:


            st.write(

            "ผลการตรวจจับ Segmentation"

            )


            st.image(

                cv2.cvtColor(

                    result["image"],

                    cv2.COLOR_BGR2RGB

                ),

                width=500

            )






        # --------------------------

        # Summary

        # --------------------------


        a,b,c=st.columns(3)



        a.metric(

            "WAR",

            f"{result['WAR']}%"

        )



        b.metric(

            "Density",

            result["level"]

        )


        c.metric(

            "Recommendation",

            result["action"]

        )






# ==================================================
# HISTORY
# ==================================================


if history:



    df=pd.DataFrame(

        history

    )



    st.divider()



    st.subheader(

        "📈 WAR Trend Analysis"

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

    "กรุณา upload ภาพจากกล้อง"

    )
