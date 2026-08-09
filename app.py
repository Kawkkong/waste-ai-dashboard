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
# DASHBOARD DISPLAY
# =========================

st.divider()

for cam in CAMERA_CONFIG:

    st.subheader(f"📷 {cam}")

    if cam not in st.session_state.camera_results:
        st.info("กรุณาอัปโหลดภาพจากกล้อง")
        continue


    data = st.session_state.camera_results[cam]

    result = data["result"]


    level = result["level"]

    info = LEVEL_INFO[level]


    col1, col2, col3 = st.columns(3)


    # -------------------------
    # WAR
    # -------------------------

    with col1:

        st.metric(
            "🗑 Waste Area Ratio (WAR)",
            f'{result["WAR"]:.2f}%'
        )


    # -------------------------
    # Level
    # -------------------------

    with col2:

        st.markdown(
            f"""
            <div style="
            padding:15px;
            border-radius:10px;
            background:{info['color']};
            color:white;
            text-align:center;
            ">
            <h3>{info['name']}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )


    # -------------------------
    # Action
    # -------------------------

    with col3:

        st.info(
            f"📌 คำแนะนำ\n\n{info['action']}"
        )


    st.write("")


    # -------------------------
    # IMAGE
    # -------------------------

    img_col1, img_col2 = st.columns(2)


    with img_col1:

        st.image(
            cv2.cvtColor(
                data["original"],
                cv2.COLOR_BGR2RGB
            ),
            caption="ภาพจาก CCTV",
            use_container_width=True
        )


    with img_col2:

        st.image(
            cv2.cvtColor(
                result["image"],
                cv2.COLOR_BGR2RGB
            ),
            caption="ผลการ Segmentation ด้วย YOLOv11-Seg",
            use_container_width=True
        )



    # =========================
    # CHANGE / TREND
    # =========================

    st.subheader("📈 การเปลี่ยนแปลงของปริมาณขยะ")


    change = result["change"]


    if change > 20:

        st.warning(
            f"⚠️ ปริมาณขยะเพิ่มขึ้น {change:.2f}% "
            "ควรตรวจสอบพื้นที่"
        )

    elif change < -20:

        st.success(
            f"✅ ปริมาณขยะลดลง {abs(change):.2f}%"
        )

    else:

        st.info(
            f"แนวโน้มปกติ ({change:+.2f}%)"
        )



    # =========================
    # HISTORY
    # =========================

    st.divider()

    st.subheader("📊 ประวัติการตรวจสอบ")


    history = st.session_state.history[cam]


    if len(history) > 0:


        for item in reversed(history[-5:]):


            with st.expander(
                f"{item['เวลา']} | "
                f"{item['ระดับ']} | "
                f"WAR {item['WAR']:.2f}%"
            ):


                h1, h2 = st.columns(2)


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
                        caption="ผล AI",
                        use_container_width=True
                    )


                st.write(
                    f"ระดับขยะ : {item['ระดับ']}"
                )

                st.write(
                    f"WAR : {item['WAR']:.2f}%"
                )

                st.write(
                    f"การเปลี่ยนแปลง : {item['เปลี่ยนแปลง']:+.2f}%"
                )


    else:

        st.write(
            "ยังไม่มีข้อมูล"
        )
