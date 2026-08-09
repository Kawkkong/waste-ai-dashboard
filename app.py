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

    page_title="ระบบตรวจสอบขยะด้วย AI",

    layout="wide"

)



# =====================================================
# LEVEL CONFIG
# =====================================================

LEVEL_INFO = {


    "Normal": {

        "name": "Normal (ไม่มีขยะ)",

        "color": "#4CAF50",

        "action": "ไม่พบขยะ"

    },


    "Low": {

        "name": "Low (ต่ำ)",

        "color": "#2196F3",

        "action": "เฝ้าระวังพื้นที่"

    },


    "Medium": {

        "name": "Medium (ปานกลาง)",

        "color": "#FFD600",

        "action": "เตรียมวางแผนเก็บขยะ"

    },


    "High": {

        "name": "High (สูง)",

        "color": "#FF9800",

        "action": "แจ้งเตือนเจ้าหน้าที่"

    },


    "Critical": {

        "name": "Critical (วิกฤต)",

        "color": "#F44336",

        "action": "แจ้งเตือนด่วนและดำเนินการเก็บขยะทันที"

    }

}





# =====================================================
# CSS
# =====================================================

st.markdown(

"""

<style>


.level-box {

padding:12px;

border-radius:10px;

font-size:16px;

font-weight:bold;

margin-bottom:10px;

}


.notice-high {

background:#FF9800;

color:black;

padding:8px;

border-radius:8px;

font-size:14px;

font-weight:bold;

}


.notice-critical {

background:#F44336;

color:white;

padding:8px;

border-radius:8px;

font-size:14px;

font-weight:bold;

}


.recommend {

background:#eeeeee;

padding:12px;

border-radius:8px;

font-size:15px;

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

    st.session_state.history = {}



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
# UPLOAD
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





            st.session_state.history[cam].append({


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
# CAMERA DISPLAY
# =====================================================

for cam,data in st.session_state.camera_results.items():


    result = data["result"]


    level = result["level"]


    info = LEVEL_INFO[level]



    st.divider()



    st.header(

        f"📷 {cam}"

    )





    # -------------------------
    # LEVEL
    # -------------------------

    st.markdown(

        f"""

<div class="level-box"

style="background:{info['color']}">


ระดับความหนาแน่นของขยะ

<br>


{info['name']}


</div>

        """,

        unsafe_allow_html=True

    )





    st.markdown(

        f"""

<div class="recommend">

<b>คำแนะนำ:</b>

{info['action']}

</div>


        """,

        unsafe_allow_html=True

    )





    # -------------------------
    # ALERT
    # -------------------------

    if level == "High":


        st.markdown(

        f"""

<div class="notice-high">

🟧 แจ้งเตือนเจ้าหน้าที่ :

พบขยะระดับสูงที่ {cam}

</div>

        """,

        unsafe_allow_html=True

        )




    elif level == "Critical":


        st.markdown(

        f"""

<div class="notice-critical">

🟥 แจ้งเตือนด่วน :

พบขยะระดับวิกฤตที่ {cam}

</div>

        """,

        unsafe_allow_html=True

        )







    # -------------------------
    # IMAGE
    # -------------------------

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

            width=450

        )




    with c2:


        st.subheader(

            "ผลการแบ่งพื้นที่ขยะ"

        )


        st.image(

            cv2.cvtColor(

                result["image"],

                cv2.COLOR_BGR2RGB

            ),

            width=450

        )







    # -------------------------
    # CURRENT DATA
    # -------------------------

    a,b,c = st.columns(3)



    a.metric(

        "พื้นที่ขยะ (WAR)",

        f'{result["WAR"]}%'

    )


    b.metric(

        "เปลี่ยนแปลงจากครั้งก่อน",

        f'{result["change"]:+.2f}%'

    )


    c.metric(

        "ระดับ",

        info["name"]

    )







    # =================================================
    # GRAPH
    # =================================================

    st.subheader(

        f"📈 แนวโน้ม WAR ของ {cam}"

    )



    if len(st.session_state.history[cam]) > 1:


        chart = pd.DataFrame(

            st.session_state.history[cam]

        )


        st.line_chart(

            chart,

            x="เวลา",

            y="WAR"

        )


    else:

        st.info(

            "ต้องมีข้อมูลมากกว่า 1 ครั้งเพื่อสร้างกราฟ"

        )








    # =================================================
    # HISTORY
    # =================================================

    st.subheader(

        f"📋 ประวัติการตรวจสอบ {cam}"

    )




    for item in reversed(

        st.session_state.history[cam]

    ):



        history_info = LEVEL_INFO[item["ระดับ"]]



        with st.expander(

            f'{item["เวลา"]} | {history_info["name"]}'

        ):



            st.markdown(

            f"""

<div class="level-box"

style="background:{history_info['color']}">


{history_info['name']}


</div>

            """,

            unsafe_allow_html=True

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



            z.metric(

                "ระดับ",

                history_info["name"]

            )





            h1,h2 = st.columns(2)



            with h1:


                st.image(

                    cv2.cvtColor(

                        item["ภาพ"],

                        cv2.COLOR_BGR2RGB

                    ),

                    width=350,

                    caption="ภาพต้นฉบับ"

                )




            with h2:


                st.image(

                    cv2.cvtColor(

                        item["ผล"],

                        cv2.COLOR_BGR2RGB

                    ),

                    width=350,

                    caption="ผล Segmentation"

                )
