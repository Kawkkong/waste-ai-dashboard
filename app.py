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


st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 13px;
}

h1 {
    font-size: 26px !important;
}

[data-testid="stMetricValue"] {
    font-size: 18px !important;
}

[data-testid="stImage"] img {
    max-height:420px;
    object-fit:contain;
}
</style>
""", unsafe_allow_html=True)



if "camera_results" not in st.session_state:
    st.session_state.camera_results = {}

if "history" not in st.session_state:
    st.session_state.history = {}


for cam in CAMERA_CONFIG:
    if cam not in st.session_state.history:
        st.session_state.history[cam] = []



st.title("🗑 ระบบตรวจสอบปริมาณขยะด้วย AI")
st.caption("YOLOv11-Seg + Waste Area Ratio (WAR)")


st.sidebar.header("📷 อัปโหลดภาพจากกล้อง CCTV")


for cam in CAMERA_CONFIG:

    uploaded_file = st.sidebar.file_uploader(
        cam,
        type=["jpg", "jpeg", "png"],
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

            img = cv2.imdecode(
                np.asarray(
                    bytearray(uploaded_file.read()),
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

                "เวลา":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "WAR":
                    result["WAR"],

                "การเปลี่ยนแปลง":
                    result["change"],

                "ระดับ":
                    result["level"],

                "การดำเนินการ":
                    result["action"],

                "ภาพต้นฉบับ":
                    img.copy(),

                "ภาพ Segmentation":
                    result["image"].copy()

            })




for cam, data in st.session_state.camera_results.items():

    st.divider()

    st.header(f"📷 {cam}")


    img = data["original"]
    result = data["result"]


    if result["level"] == "High":

        st.warning(
            f"🟧 แจ้งเตือนเจ้าหน้าที่\n\n"
            f"พบปริมาณขยะระดับสูงที่ {cam}\n"
            f"กรุณาตรวจสอบพื้นที่"
        )


    elif result["level"] == "Critical":

        st.error(
            f"🟥 แจ้งเตือนด่วน\n\n"
            f"พบปริมาณขยะระดับวิกฤตที่ {cam}\n"
            f"จำเป็นต้องดำเนินการเก็บขยะทันที"
        )



    col1, col2 = st.columns(2)


    with col1:

        st.subheader("ภาพจากกล้อง")

        st.image(
            cv2.cvtColor(
                img,
                cv2.COLOR_BGR2RGB
            ),
            width=420
        )


    with col2:

        st.subheader("ผลการแบ่งพื้นที่ขยะ")

        st.image(
            cv2.cvtColor(
                result["image"],
                cv2.COLOR_BGR2RGB
            ),
            width=420
        )



    a,b,c,d = st.columns(4)


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
        result["level"]
    )


    d.metric(
        "การดำเนินการ",
        result["action"]
    )



    st.subheader(
        f"📋 ประวัติการตรวจสอบ {cam}"
    )


    for item in reversed(
        st.session_state.history[cam]
    ):

        with st.expander(
            f'{item["เวลา"]} | {item["ระดับ"]}'
        ):

            h1,h2 = st.columns(2)


            with h1:

                st.write("ภาพต้นฉบับ")

                st.image(
                    cv2.cvtColor(
                        item["ภาพต้นฉบับ"],
                        cv2.COLOR_BGR2RGB
                    ),
                    width=350
                )


            with h2:

                st.write("ภาพ Segmentation")

                st.image(
                    cv2.cvtColor(
                        item["ภาพ Segmentation"],
                        cv2.COLOR_BGR2RGB
                    ),
                    width=350
                )


            x1,x2,x3,x4 = st.columns(4)


            x1.metric(
                "WAR",
                f'{item["WAR"]}%'
            )

            x2.metric(
                "เปลี่ยนแปลง",
                f'{item["การเปลี่ยนแปลง"]:+.2f}%'
            )

            x3.metric(
                "ระดับ",
                item["ระดับ"]
            )

            x4.metric(
                "การดำเนินการ",
                item["การดำเนินการ"]
            )
