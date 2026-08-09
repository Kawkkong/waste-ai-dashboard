import streamlit as st

import cv2
import numpy as np

from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG



# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="ระบบตรวจสอบปริมาณขยะด้วย AI",
    layout="wide"
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
# TRANSLATION
# =========================

LEVEL_TRANSLATE = {

    "Normal": "ไม่มีขยะ",

    "Low": "ต่ำ",

    "Medium": "ปานกลาง",

    "High": "สูง",

    "Critical": "วิกฤต"

}



ACTION_TRANSLATE = {

    "No waste detected":
        "ไม่พบขยะ",

    "Monitor area":
        "เฝ้าระวังพื้นที่",

    "Prepare collection":
        "เตรียมวางแผนเก็บขยะ",

    "Notify staff":
        "แจ้งเตือนเจ้าหน้าที่",

    "Urgent collection":
        "เก็บขยะทันที"

}



# =========================
# TITLE
# =========================

st.title(
    "🗑 ระบบตรวจสอบปริมาณขยะด้วย AI"
)


st.caption(
    "YOLOv11-Seg + อัตราส่วนพื้นที่ขยะ (Waste Area Ratio: WAR)"
)



# =========================
# UPLOAD CCTV
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

            .get(cam, {})

            .get("file_id")

        )



        if file_id != old_file:



            img = cv2.imdecode(

                np.asarray(

                    bytearray(

                        uploaded_file.read()

                    ),

                    dtype=np.uint8

                ),

                cv2.IMREAD_COLOR

            )



            result = analyze_frame(

                img,

                cam

            )



            st.session_state.camera_results[cam] = {

                "file_id": file_id,

                "original": img,

                "result": result

            }



            st.session_state.history[cam].append({

                "Time":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),


                "WAR":
                    result["WAR"],


                "Change":
                    result["change"],


                "Level":
                    result["level"],


                "Action":
                    result["action"],


                "Original":
                    img.copy(),


                "Segmentation":
                    result["image"].copy()

            })


            # เก็บย้อนหลังสูงสุด 20 ภาพ

            if len(st.session_state.history[cam]) > 20:

                st.session_state.history[cam].pop(0)





# =========================
# DASHBOARD
# =========================


for cam, data in st.session_state.camera_results.items():


    st.divider()


    st.header(
        f"📷 กล้อง {cam}"
    )


    img = data["original"]

    result = data["result"]



    # -------------------------
    # IMAGE
    # -------------------------

    c1, c2 = st.columns(2)



    with c1:

        st.image(

            cv2.cvtColor(
                img,
                cv2.COLOR_BGR2RGB
            ),

            use_container_width=True,

            caption="📷 ภาพจากกล้อง CCTV"

        )



    with c2:

        st.image(

            cv2.cvtColor(
                result["image"],
                cv2.COLOR_BGR2RGB
            ),

            use_container_width=True,

            caption="🤖 ผลการแบ่งพื้นที่ขยะด้วย AI"

        )





    # -------------------------
    # RESULT
    # -------------------------

    a,b,c,d = st.columns(4)



    a.metric(

        "🗑 อัตราส่วนพื้นที่ขยะ (WAR)",

        f'{result["WAR"]:.2f}%'

    )



    b.metric(

        "📈 การเปลี่ยนแปลง",

        f'{result["change"]:+.2f}%'

    )



    c.metric(

        "📊 ระดับความหนาแน่น",

        LEVEL_TRANSLATE.get(

            result["level"],

            result["level"]

        )

    )



    d.metric(

        "📌 คำแนะนำ",

        ACTION_TRANSLATE.get(

            result["action"],

            result["action"]

        )

    )





    # -------------------------
    # HISTORY
    # -------------------------

    st.subheader(

        f"📋 ประวัติการตรวจสอบ - {cam}"

    )



    for item in reversed(

        st.session_state.history[cam][-5:]

    ):



        with st.expander(

            f'{item["Time"]} | '
            f'ระดับ {LEVEL_TRANSLATE.get(item["Level"], item["Level"])}'

        ):



            h1,h2 = st.columns(2)



            with h1:

                st.image(

                    cv2.cvtColor(

                        item["Original"],

                        cv2.COLOR_BGR2RGB

                    ),

                    use_container_width=True,

                    caption="ภาพต้นฉบับ"

                )



            with h2:

                st.image(

                    cv2.cvtColor(

                        item["Segmentation"],

                        cv2.COLOR_BGR2RGB

                    ),

                    use_container_width=True,

                    caption="ภาพผล AI"

                )





            x1,x2,x3,x4 = st.columns(4)



            x1.metric(

                "🗑 พื้นที่ขยะ",

                f'{item["WAR"]:.2f}%'

            )



            x2.metric(

                "📈 เปลี่ยนแปลง",

                f'{item["Change"]:+.2f}%'

            )



            x3.metric(

                "📊 ระดับ",

                LEVEL_TRANSLATE.get(

                    item["Level"],

                    item["Level"]

                )

            )



            x4.metric(

                "📌 การดำเนินการ",

                ACTION_TRANSLATE.get(

                    item["Action"],

                    item["Action"]

                )

            )
