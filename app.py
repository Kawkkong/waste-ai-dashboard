import streamlit as st

import cv2
import numpy as np

from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG


st.set_page_config(
    page_title="Waste AI Dashboard",
    layout="wide"
)


st.markdown(
'''
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
''',
unsafe_allow_html=True
)


if "camera_results" not in st.session_state:
    st.session_state.camera_results = {}

if "history" not in st.session_state:
    st.session_state.history = {}

for cam in CAMERA_CONFIG:
    if cam not in st.session_state.history:
        st.session_state.history[cam] = []


st.title("🗑 Waste AI Dashboard")
st.caption("YOLOv11-Seg + Waste Area Ratio (WAR)")


st.sidebar.header("📷 CCTV Upload")


for cam in CAMERA_CONFIG:

    uploaded_file = st.sidebar.file_uploader(
        cam,
        type=["jpg", "jpeg", "png"],
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
                    bytearray(uploaded_file.read()),
                    dtype=np.uint8
                ),
                cv2.IMREAD_COLOR
            )

            result = analyze_frame(img, cam)

            st.session_state.camera_results[cam] = {
                "file_id": file_id,
                "original": img,
                "result": result
            }

            st.session_state.history[cam].append({
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "WAR": result["WAR"],
                "Change": result["change"],
                "Level": result["level"],
                "Action": result["action"],
                "Original": img.copy(),
                "Segmentation": result["image"].copy()
            })


for cam, data in st.session_state.camera_results.items():

    st.divider()
    st.header(f"📷 {cam}")

    img = data["original"]
    result = data["result"]

    c1, c2 = st.columns(2)

    with c1:
        st.image(
            cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
            width=420,
            caption="Original CCTV"
        )

    with c2:
        st.image(
            cv2.cvtColor(result["image"], cv2.COLOR_BGR2RGB),
            width=420,
            caption="Segmentation"
        )

    a,b,c,d = st.columns(4)

    a.metric("WAR", f'{result["WAR"]}%')
    b.metric("Change", f'{result["change"]:+.2f}%')
    c.metric("Density", result["level"])
    d.metric("Action", result["action"])


    st.subheader(f"📋 History - {cam}")

    for item in reversed(st.session_state.history[cam]):

        with st.expander(
            f'{item["Time"]} | {item["Level"]}'
        ):

            h1,h2 = st.columns(2)

            with h1:
                st.image(
                    cv2.cvtColor(
                        item["Original"],
                        cv2.COLOR_BGR2RGB
                    ),
                    width=350,
                    caption="Original"
                )

            with h2:
                st.image(
                    cv2.cvtColor(
                        item["Segmentation"],
                        cv2.COLOR_BGR2RGB
                    ),
                    width=350,
                    caption="Segmentation"
                )

            x1,x2,x3,x4 = st.columns(4)

            x1.metric("WAR", f'{item["WAR"]}%')
            x2.metric("Change", f'{item["Change"]:+.2f}%')
            x3.metric("Level", item["Level"])
            x4.metric("Action", item["Action"])
