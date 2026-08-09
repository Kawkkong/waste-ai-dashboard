import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px

from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG



# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(

    page_title="ระบบตรวจสอบขยะด้วย AI",

    layout="wide"

)



# =====================================================
# LEVEL CONFIG
# =====================================================

LEVEL_INFO = {

    "Normal": {

        "name":"Normal (ไม่มีขยะ)",

        "color":"#4CAF50",

        "action":"ไม่พบขยะ"

    },


    "Low": {

        "name":"Low (ต่ำ)",

        "color":"#2196F3",

        "action":"เฝ้าระวังพื้นที่"

    },


    "Medium": {

        "name":"Medium (ปานกลาง)",

        "color":"#FFD600",

        "action":"เตรียมวางแผนเก็บขยะ"

    },


    "High": {

        "name":"High (สูง)",

        "color":"#FF9800",

        "action":"แจ้งเตือนเจ้าหน้าที่"

    },


    "Critical": {

        "name":"Critical (วิกฤต)",

        "color":"#F44336",

        "action":"แจ้งเตือนด่วนและดำเนินการเก็บขยะทันที"

    }

}





# =====================================================
# CSS SMALL UI
# =====================================================

st.markdown(

"""

<style>


h1{

font-size:28px !important;

}


h2{

font-size:20px !important;

}


h3{

font-size:16px !important;

}



.level-box{

padding:8px;

border-radius:8px;

font-size:14px;

font-weight:bold;

margin-bottom:5px;

}



.recommend{

background:#eeeeee;

padding:8px;

border-radius:8px;

font-size:13px;

}



[data-testid="stMetricValue"]{

font-size:20px;

}



[data-testid="stMetricLabel"]{

font-size:12px;

}


</style>


""",

unsafe_allow_html=True

)





# =====================================================
# SESSION
# =====================================================

if "camera_results" not in st.session_state:

    st.session_state.camera_results = {}



if "history" not in st.session_state:

    st.session_state.history = {}



if "selected_history" not in st.session_state:

    st.session_state.selected_history = None




for cam in CAMERA_CONFIG:

    if cam not in st.session_state.history:

        st.session_state.history[cam] = []





# =====================================================
# TITLE
# =====================================================

st.title(

"🗑 ระบบตรวจสอบปริมาณขยะด้วย AI"

)


st.caption(

"YOLOv11-Seg + Waste Area Ratio (WAR)"

)
# =====================================================
# UPLOAD CCTV IMAGE
# =====================================================

st.sidebar.header(
    "📷 อัปโหลดภาพจากกล้อง CCTV"
)



for cam in CAMERA_CONFIG:


    uploaded_file = st.sidebar.file_uploader(

        cam,

        type=[

            "jpg",
            "jpeg",
            "png"

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


                "original":

                img,


                "result":

                result


            }




            history_id = len(

                st.session_state.history[cam]

            )




            st.session_state.history[cam].append({


                "ID":

                history_id,


                "เวลา":

                datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                ),


                "ภาพ":

                img.copy(),


                "ผล":

                result["image"].copy(),


                "WAR":

                result["WAR"],


                "เปลี่ยนแปลง":

                result["change"],


                "ระดับ":

                result["level"]

            })







# =====================================================
# DISPLAY CAMERA
# =====================================================

for cam, data in st.session_state.camera_results.items():


    result = data["result"]


    level = result["level"]


    info = LEVEL_INFO[level]



    st.divider()



    st.header(

        f"📷 {cam}"

    )





    # =========================
    # LEVEL
    # =========================

    st.markdown(

        f"""

        <div class="level-box"

        style="background-color:{info['color']};">


        ระดับความหนาแน่นของขยะ<br>

        {info['name']}


        </div>


        """,

        unsafe_allow_html=True

    )





    # =========================
    # ACTION
    # =========================

    st.markdown(

        f"""

        <div class="recommend">

        <b>คำแนะนำ:</b>

        {info['action']}

        </div>


        """,

        unsafe_allow_html=True

    )







    # =========================
    # IMAGE
    # =========================

    c1,c2 = st.columns(2)



    with c1:


        st.subheader(

            "ภาพจากกล้อง"

        )


        st.image(

            cv2.cvtColor(

                data["original"],

                cv2.COLOR_BGR2RGB

            ),

            use_container_width=True

        )





    with c2:


        st.subheader(

            "ผล Segmentation"

        )


        st.image(

            cv2.cvtColor(

                result["image"],

                cv2.COLOR_BGR2RGB

            ),

            use_container_width=True

        )






    # =========================
    # CURRENT RESULT
    # =========================

    st.subheader(

        "📊 ผลการวิเคราะห์"

    )



    a,b,c = st.columns(3)



    a.metric(

        "WAR",

        f'{result["WAR"]}%'

    )


    b.metric(

        "เปลี่ยนแปลง",

        f'{result["change"]:+.2f}%'

    )


    c.metric(

        "ระดับ",

        info["name"]

    )






    # =========================
    # GRAPH
    # =========================

    st.subheader(

        f"📈 แนวโน้ม WAR : {cam}"

    )



    if len(st.session_state.history[cam]) > 0:


        graph_data = pd.DataFrame(

            st.session_state.history[cam]

        )



        fig = px.line(

            graph_data,

            x="เวลา",

            y="WAR",

            markers=True,

            title=None

        )


        fig.update_layout(

            height=250,

            margin=dict(

                l=20,

                r=20,

                t=20,

                b=20

            )

        )


        event = st.plotly_chart(

            fig,

            use_container_width=True,

            on_select="rerun",

            selection_mode="points"

        )



if event and event.selection:

    if "points" in event.selection:

        if len(event.selection["points"]) > 0:


            point = event.selection["points"][0]


            selected_time = point["x"]


            # แปลงเวลาให้ตรงกับ history

            selected_time = str(selected_time)



            for item in st.session_state.history[cam]:


                if item["เวลา"] in selected_time:


                    st.session_state.selected_history = item

                    break
        # =========================
        # SELECTED GRAPH DATA
        # =========================

        if st.session_state.selected_history is not None:


            item = st.session_state.selected_history


            st.subheader(

                "🔎 ข้อมูลที่เลือกจากกราฟ"

            )



            x,y,z = st.columns(3)



            x.metric(

                "WAR",

                f'{item["WAR"]}%'

            )



            y.metric(

                "เปลี่ยนแปลง",

                f'{item["เปลี่ยนแปลง"]:+.2f}%'

            )



            selected_info = LEVEL_INFO[

                item["ระดับ"]

            ]



            z.metric(

                "ระดับ",

                selected_info["name"]

            )





            st.image(

                cv2.cvtColor(

                    item["ผล"],

                    cv2.COLOR_BGR2RGB

                ),

                caption="ผล Segmentation จากข้อมูลที่เลือก",

                use_container_width=True

            )







    # =================================================
    # HISTORY
    # =================================================

    st.subheader(

        f"📋 ประวัติการตรวจสอบ {cam}"

    )



    histories = st.session_state.history[cam]



    if len(histories) == 0:


        st.info(

            "ยังไม่มีประวัติ"

        )



    else:


        for item in reversed(histories):


            history_info = LEVEL_INFO[

                item["ระดับ"]

            ]



            with st.expander(

                f'#{item["ID"]+1} | '

                f'{item["เวลา"]} | '

                f'{history_info["name"]}'

            ):



                # -------------------------
                # LEVEL
                # -------------------------

                st.markdown(

                    f"""

                    <div class="level-box"

                    style="background-color:{history_info['color']};">


                    {history_info['name']}


                    </div>


                    """,

                    unsafe_allow_html=True

                )





                # -------------------------
                # DATA
                # -------------------------

                a,b,c = st.columns(3)



                a.metric(

                    "WAR",

                    f'{item["WAR"]}%'

                )


                b.metric(

                    "เปลี่ยนแปลง",

                    f'{item["เปลี่ยนแปลง"]:+.2f}%'

                )


                c.metric(

                    "ระดับ",

                    history_info["name"]

                )







                # -------------------------
                # IMAGES
                # -------------------------

                h1,h2 = st.columns(2)



                with h1:


                    st.image(

                        cv2.cvtColor(

                            item["ภาพ"],

                            cv2.COLOR_BGR2RGB

                        ),

                        caption="ภาพต้นฉบับ",

                        use_container_width=True

                    )





                with h2:


                    st.image(

                        cv2.cvtColor(

                            item["ผล"],

                            cv2.COLOR_BGR2RGB

                        ),

                        caption="ผล Segmentation",

                        use_container_width=True

                    )
