import streamlit as st
import cv2
import numpy as np
from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG


# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="ระบบตรวจสอบขยะด้วย AI",
    layout="wide"
)


# ==========================
# LEVEL CONFIG
# ==========================

LEVEL_INFO = {

    "Normal": {
        "display": "Normal (ไม่มีขยะ)",
        "color": "#4CAF50",
        "action": "ไม่พบขยะ"
    },

    "Low": {
        "display": "Low (ต่ำ)",
        "color": "#42A5F5",
        "action": "เฝ้าระวังพื้นที่"
    },

    "Medium": {
        "display": "Medium (ปานกลาง)",
        "color": "#FFD54F",
        "action": "เตรียมวางแผนเก็บขยะ"
    },

    "High": {
        "display": "High (สูง)",
        "color": "#FF9800",
        "action": "แจ้งเตือนเจ้าหน้าที่"
    },

    "Critical": {
        "display": "Critical (วิกฤต)",
        "color": "#F44336",
        "action": "แจ้งเตือนด่วนและดำเนินการเก็บขยะทันที"
    }

}



# ==========================
# SESSION STATE
# ==========================

if "camera_results" not in st.session_state:

    st.session_state.camera_results = {}



if "history" not in st.session_state:

    st.session_state.history = {}



for cam in CAMERA_CONFIG:

    if cam not in st.session_state.history:

        st.session_state.history[cam] = []



# ==========================
# TITLE
# ==========================

st.title(
    "🗑 ระบบตรวจสอบปริมาณขยะด้วย AI"
)


st.caption(
    "YOLOv11-Seg + Waste Area Ratio (WAR)"
)



# ==========================
# SIDEBAR UPLOAD
# ==========================

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


                "file_id": file_id,


                "original": img,


                "result": result

            }



            st.session_state.history[cam].append({


                "time":

                datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                ),


                "original":

                img.copy(),


                "segmentation":

                result["image"].copy(),


                "WAR":

                result["WAR"],


                "level":

                result["level"],


                "change":

                result["change"]

            })





# ==========================
# DISPLAY CAMERA
# ==========================

for cam,data in st.session_state.camera_results.items():


    result = data["result"]


    level = result["level"]


    info = LEVEL_INFO[level]



    st.divider()


    st.header(

        f"📷 {cam}"

    )



    # --------------------------
    # Level Card
    # --------------------------

    st.markdown(

        f"""

        <div style="
        background:{info['color']};
        padding:15px;
        border-radius:10px;
        font-weight:bold;
        ">

        ระดับความหนาแน่นของขยะ:
        {info['display']}

        <br>

        คำแนะนำ:
        {info['action']}

        </div>

        """,

        unsafe_allow_html=True

    )



    # --------------------------
    # Notification
    # --------------------------

    if level == "High":

        st.warning(

            f"🟧 แจ้งเตือนเจ้าหน้าที่\n\n"
            f"พบขยะระดับสูงที่ {cam}"

        )



    elif level == "Critical":

        st.error(

            f"🟥 แจ้งเตือนด่วน\n\n"
            f"พบขยะระดับวิกฤตที่ {cam}\n"
            f"ต้องดำเนินการทันที"

        )




    # --------------------------
    # Images
    # --------------------------

    col1,col2 = st.columns(2)



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

            "ผล Segmentation"

        )


        st.image(

            cv2.cvtColor(

                result["image"],

                cv2.COLOR_BGR2RGB

            ),

            width=450

        )




    # --------------------------
    # Metrics
    # --------------------------

    a,b,c = st.columns(3)


    a.metric(

        "พื้นที่ขยะ (WAR)",

        f'{result["WAR"]}%'

    )


    b.metric(

        "การเปลี่ยนแปลง",

        f'{result["change"]:+.2f}%'

    )


    c.metric(

        "คำแนะนำ",

        info["action"]

    )




    # --------------------------
    # History
    # --------------------------

    st.subheader(

        f"📋 ประวัติการตรวจสอบ {cam}"

    )



    for item in reversed(

        st.session_state.history[cam]

    ):


        history_level = LEVEL_INFO[item["level"]]



        with st.expander(

            f'{item["time"]} | {history_level["display"]}'

        ):


            h1,h2 = st.columns(2)



            with h1:


                st.image(

                    cv2.cvtColor(

                        item["original"],

                        cv2.COLOR_BGR2RGB

                    ),

                    width=350,

                    caption="ภาพต้นฉบับ"

                )



            with h2:


                st.image(

                    cv2.cvtColor(

                        item["segmentation"],

                        cv2.COLOR_BGR2RGB

                    ),

                    width=350,

                    caption="Segmentation"

                )
