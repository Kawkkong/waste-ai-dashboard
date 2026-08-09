import streamlit as st
import cv2
import numpy as np
from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG


st.set_page_config(
    page_title="ระบบตรวจสอบขยะด้วย AI",
    layout="wide"
)


# =========================
# ตั้งค่าระดับขยะ
# =========================

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



# =========================
# CSS
# =========================

st.markdown(
"""
<style>

.level-box {

    padding:20px;
    border-radius:15px;
    font-size:20px;
    font-weight:bold;
    margin-bottom:20px;

}


.notice-high {

    background:#FF9800;
    color:black;
    padding:15px;
    border-radius:10px;
    font-size:18px;
    font-weight:bold;

}


.notice-critical {

    background:#F44336;
    color:white;
    padding:15px;
    border-radius:10px;
    font-size:18px;
    font-weight:bold;

}


</style>
""",
unsafe_allow_html=True
)



# =========================
# SESSION
# =========================


if "camera_results" not in st.session_state:

    st.session_state.camera_results = {}



if "history" not in st.session_state:

    st.session_state.history = {}



for cam in CAMERA_CONFIG:

    if cam not in st.session_state.history:

        st.session_state.history[cam] = []



# =========================
# TITLE
# =========================

st.title(
"🗑 ระบบตรวจสอบปริมาณขยะด้วย AI"
)


st.caption(
"YOLOv11-Seg + Waste Area Ratio (WAR)"
)



# =========================
# UPLOAD
# =========================

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


    if uploaded_file:


        file_id = (

            uploaded_file.name,

            uploaded_file.size

        )


        old_file = (

            st.session_state.camera_results
            .get(cam,{})
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

                "file_id":file_id,

                "original":img,

                "result":result

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

                "ระดับ":
                result["level"],

                "เปลี่ยนแปลง":
                result["change"]

            })
# =========================
# แสดงผลแต่ละกล้อง
# =========================

for cam, data in st.session_state.camera_results.items():

    result = data["result"]

    level = result["level"]

    info = LEVEL_INFO[level]


    st.divider()


    st.header(
        f"📷 {cam}"
    )



    # =========================
    # แถบระดับความหนาแน่น
    # =========================

    st.markdown(

        f"""
        <div class="level-box"
             style="background-color:{info['color']};">

            ระดับความหนาแน่นของขยะ<br>

            {info['name']}<br><br>

            คำแนะนำ:<br>

            {info['action']}

        </div>
        """,

        unsafe_allow_html=True

    )



    # =========================
    # การแจ้งเตือน
    # =========================

    if level == "High":

        st.markdown(

            f"""
            <div class="notice-high">

                🟧 แจ้งเตือนเจ้าหน้าที่<br><br>

                พบปริมาณขยะระดับสูง<br>

                กล้อง: {cam}<br><br>

                กรุณาตรวจสอบพื้นที่

            </div>
            """,

            unsafe_allow_html=True

        )


    elif level == "Critical":

        st.markdown(

            f"""
            <div class="notice-critical">

                🟥 แจ้งเตือนด่วน<br><br>

                พบปริมาณขยะระดับวิกฤต<br>

                กล้อง: {cam}<br><br>

                ต้องดำเนินการเก็บขยะทันที

            </div>
            """,

            unsafe_allow_html=True

        )



    # =========================
    # ภาพ
    # =========================

    col1, col2 = st.columns(
        2,
        gap="small"
    )



    with col1:

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



    with col2:

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



    # =========================
    # ข้อมูลการวิเคราะห์
    # =========================

    st.subheader(
        "📊 ผลการวิเคราะห์"
    )


    a, b, c, d = st.columns(
        4,
        gap="small"
    )



    a.metric(

        "พื้นที่ขยะ (WAR)",

        f'{result["WAR"]}%'

    )


    b.metric(

        "การเปลี่ยนแปลง",

        f'{result["change"]:+.2f}%'

    )


    c.metric(

        "ระดับขยะ",

        info["name"]

    )


    d.metric(

        "คำแนะนำ",

        info["action"]

    )



    # =========================
    # ประวัติของกล้อง
    # =========================

    st.subheader(

        f"📋 ประวัติการตรวจสอบ {cam}"

    )


    histories = st.session_state.history[cam]



    if len(histories) == 0:

        st.info(
            "ยังไม่มีประวัติการตรวจสอบ"
        )


    else:


        for item in reversed(histories):


            history_level = item["ระดับ"]

            history_info = LEVEL_INFO[history_level]



            with st.expander(

                f'{item["เวลา"]} | '
                f'{history_info["name"]}'

            ):


                # -------------------------
                # แถบระดับของประวัติ
                # -------------------------

                st.markdown(

                    f"""
                    <div class="level-box"
                         style="
                         background-color:
                         {history_info['color']};
                         font-size:16px;
                         ">

                        {history_info["name"]}<br>

                        คำแนะนำ:
                        {history_info["action"]}

                    </div>
                    """,

                    unsafe_allow_html=True

                )



                h1, h2 = st.columns(
                    2,
                    gap="small"
                )



                with h1:

                    st.write(
                        "ภาพต้นฉบับ"
                    )


                    st.image(

                        cv2.cvtColor(

                            item["ภาพ"],

                            cv2.COLOR_BGR2RGB

                        ),

                        width=350

                    )



                with h2:

                    st.write(
                        "ผลการแบ่งพื้นที่ขยะ"
                    )


                    st.image(

                        cv2.cvtColor(

                            item["ผล"],

                            cv2.COLOR_BGR2RGB

                        ),

                        width=350

                    )



                # -------------------------
                # ข้อมูลประวัติ
                # -------------------------

                x1, x2, x3 = st.columns(3)



                x1.metric(

                    "พื้นที่ขยะ (WAR)",

                    f'{item["WAR"]}%'

                )


                x2.metric(

                    "การเปลี่ยนแปลง",

                    f'{item["เปลี่ยนแปลง"]:+.2f}%'

                )


                x3.metric(

                    "ระดับ",

                    history_info["name"]

                )
