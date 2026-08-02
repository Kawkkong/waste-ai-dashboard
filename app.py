import streamlit as st
import cv2
import numpy as np
import pandas as pd

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
# TITLE
# =====================================================

st.title(
    "🗑 Dashboard ระบบตรวจจับและจำแนกระดับความหนาแน่นของกองขยะจากภาพ CCTV"
)


st.caption(
    "YOLOv11-Seg + Waste Area Ratio (WAR)"
)



# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header(
    "📷 Upload CCTV Image"
)


uploaded_files={}



for cam in CAMERA_CONFIG:


    uploaded_files[cam] = st.sidebar.file_uploader(
        cam,
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key=cam
    )





# =====================================================
# LOAD HISTORY
# =====================================================

history_file="waste_history.csv"


try:

    old_df=pd.read_csv(
        history_file
    )

except:

    old_df=pd.DataFrame(
        columns=[
            "Time",
            "Camera",
            "WAR",
            "Level",
            "Action"
        ]
    )





new_data=[]





# =====================================================
# CAMERA PROCESS
# =====================================================


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
            cv2.IMREAD_COLOR
        )



        result = analyze_frame(
            img,
            cam
        )



        now=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )



        new_data.append({

            "Time":now,

            "Camera":cam,

            "WAR":result["WAR"],

            "Level":result["level"],

            "Action":result["action"]

        })




        # =============================================
        # DISPLAY CAMERA
        # =============================================


        st.divider()



        st.header(
            f"📷 {cam} : {CAMERA_CONFIG[cam]['name']}"
        )



        col1,col2=st.columns(2)



        with col1:


            st.subheader(
                "ภาพจากกล้อง CCTV"
            )


            st.image(

                cv2.cvtColor(
                    img,
                    cv2.COLOR_BGR2RGB
                ),

                use_container_width=True

            )




        with col2:


            st.subheader(
                "ผลการตรวจจับ Segmentation"
            )


            st.image(

                cv2.cvtColor(
                    result["image"],
                    cv2.COLOR_BGR2RGB
                ),

                use_container_width=True

            )





        # =============================================
        # RESULT CARD
        # =============================================


        a,b,c=st.columns(3)



        a.metric(

            "Waste Area Ratio",

            f"{result['WAR']}%"

        )



        b.metric(

            "Density Level",

            result["level"]

        )



        c.metric(

            "Recommendation",

            result["action"]

        )






        # ALERT


        if result["level"]=="Critical":


            st.error(
                "🚨 Critical : ต้องดำเนินการเก็บขยะทันที"
            )


        elif result["level"]=="High":


            st.warning(
                "⚠️ High : แจ้งเจ้าหน้าที่เข้าตรวจสอบ"
            )


        elif result["level"]=="Medium":


            st.info(
                "ℹ️ Medium : ควรเตรียมแผนจัดเก็บ"
            )


        elif result["level"]=="Low":


            st.success(
                "✅ Low : อยู่ในระดับปกติ"
            )


        else:


            st.success(
                "✅ Normal : ไม่พบขยะ"
            )







# =====================================================
# SAVE HISTORY
# =====================================================


if new_data:


    new_df=pd.DataFrame(
        new_data
    )


    df=pd.concat(
        [
            old_df,
            new_df
        ],
        ignore_index=True
    )



    df.to_csv(
        history_file,
        index=False
    )


else:


    df=old_df






# =====================================================
# TREND ANALYSIS
# =====================================================


st.divider()


st.header(
    "📈 WAR Trend Analysis"
)




for cam in CAMERA_CONFIG:


    st.subheader(

        f"📷 {cam} : {CAMERA_CONFIG[cam]['name']}"

    )



    cam_df=df[
        df["Camera"]==cam
    ]



    if len(cam_df)>0:


        cam_df=cam_df.copy()


        cam_df["Time"]=pd.to_datetime(
            cam_df["Time"]
        )



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
# HISTORY
# =====================================================


st.divider()


st.header(
    "📋 Detection History"
)



if len(df)>0:


    st.dataframe(

        df.sort_values(
            "Time",
            ascending=False
        ),

        use_container_width=True

    )



    csv=df.to_csv(
        index=False
    )


    st.download_button(

        "⬇ Download CSV",

        csv,

        "waste_history.csv"

    )



else:


    st.info(
        "ยังไม่มีประวัติ"
    )
