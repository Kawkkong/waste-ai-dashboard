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
# TITLE
# =====================================================


st.title(
    "🗑 Waste AI Dashboard"
)


st.caption(
    "YOLOv11-Seg + Waste Area Ratio (WAR) CCTV Monitoring"
)





# =====================================================
# HISTORY FILE
# =====================================================


HISTORY_FILE = "waste_history.csv"



try:

    history_df = pd.read_csv(
        HISTORY_FILE
    )


except:


    history_df = pd.DataFrame(

        columns=[

            "Time",
            "Camera",
            "WAR",
            "Level",
            "Action"

        ]

    )







# =====================================================
# SIDEBAR UPLOAD
# =====================================================


st.sidebar.header(
    "📷 Upload CCTV Media"
)



uploaded_files={}



for cam in CAMERA_CONFIG:


    uploaded_files[cam]=st.sidebar.file_uploader(

        cam,

        type=[

            "jpg",
            "jpeg",
            "png",
            "mp4"

        ],

        key=cam

    )








new_history=[]






# =====================================================
# PROCESS CAMERA
# =====================================================


for cam,file in uploaded_files.items():


    if file is None:

        continue




    st.divider()



    st.header(

        f"📷 {cam} : {CAMERA_CONFIG[cam]['name']}"

    )




    extension=file.name.split(".")[-1].lower()





    # =================================================
    # IMAGE
    # =================================================


    if extension in [


        "jpg",
        "jpeg",
        "png"


    ]:



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




        result=analyze_frame(

            img,

            cam

        )





        # ---------- display image ----------


        col1,col2=st.columns(2)



        with col1:


            st.subheader(

                "Original CCTV"

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

                "YOLO Segmentation"

            )


            st.image(

                cv2.cvtColor(

                    result["image"],

                    cv2.COLOR_BGR2RGB

                ),

                use_container_width=True

            )






        # ---------- result ----------


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

            "Action",

            result["action"]

        )





        new_history.append({


            "Time":

            datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            ),


            "Camera":

            cam,


            "WAR":

            result["WAR"],


            "Level":

            result["level"],


            "Action":

            result["action"]


        })








    # =================================================
    # VIDEO
    # =================================================


    elif extension=="mp4":



        st.info(

            "กำลังวิเคราะห์ Video..."

        )



        temp=tempfile.NamedTemporaryFile(

            delete=False,

            suffix=".mp4"

        )



        temp.write(

            file.read()

        )


        temp.close()





        cap=cv2.VideoCapture(

            temp.name

        )



        frame_id=0


        video_result=[]



        preview=None





        while True:


            ret,frame=cap.read()



            if not ret:

                break



            frame_id+=1




            # วิเคราะห์ทุก 10 frame

            if frame_id % 10 ==0:



                result=analyze_frame(

                    frame,

                    cam

                )



                video_result.append({


                    "Frame":

                    frame_id,


                    "WAR":

                    result["WAR"],


                    "Level":

                    result["level"]

                })



                preview=result["image"]





        cap.release()



        os.remove(

            temp.name

        )






        if preview is not None:


            st.subheader(

                "ตัวอย่างผล Segmentation"

            )


            st.image(

                cv2.cvtColor(

                    preview,

                    cv2.COLOR_BGR2RGB

                ),

                use_container_width=True

            )







        video_df=pd.DataFrame(

            video_result

        )



        if len(video_df)>0:



            st.subheader(

                "📈 Video WAR Trend"

            )



            st.line_chart(

                video_df,

                x="Frame",

                y="WAR"

            )



            st.dataframe(

                video_df,

                use_container_width=True

            )





            last=video_df.iloc[-1]



            new_history.append({


                "Time":

                datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                ),


                "Camera":

                cam,


                "WAR":

                last["WAR"],


                "Level":

                last["Level"],


                "Action":

                "-"


            })








# =====================================================
# SAVE HISTORY
# =====================================================



if len(new_history)>0:



    new_df=pd.DataFrame(

        new_history

    )


    history_df=pd.concat(

        [

            history_df,

            new_df

        ],

        ignore_index=True

    )



    history_df.to_csv(

        HISTORY_FILE,

        index=False

    )







# =====================================================
# TREND CAMERA SEPARATE
# =====================================================


st.divider()


st.header(

    "📈 WAR Trend Analysis"

)





for cam in CAMERA_CONFIG:


    st.subheader(

        cam

    )



    cam_df=history_df[

        history_df["Camera"]

        ==cam

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

            "No data"

        )







# =====================================================
# HISTORY TABLE
# =====================================================


st.divider()


st.header(

    "📋 Detection History"

)




if len(history_df)>0:



    st.dataframe(

        history_df.sort_values(

            "Time",

            ascending=False

        ),

        use_container_width=True

    )



    csv=history_df.to_csv(

        index=False

    )



    st.download_button(

        "⬇ Download CSV",

        csv,

        "waste_history.csv"

    )



else:


    st.info(

        "ยังไม่มีข้อมูล"

    )
