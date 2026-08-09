import streamlit as st
import cv2
import numpy as np

from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG



# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="ระบบตรวจสอบปริมาณขยะด้วย AI",
    layout="wide"
)



# ======================================================
# CSS
# ======================================================

st.markdown(
"""
<style>

.block-container {

    padding-top:1rem;

    padding-left:2rem;

    padding-right:2rem;

}


[data-testid="stMetric"]{

    background:#f5f5f5;

    padding:8px;

    border-radius:10px;

}


[data-testid="stMetricValue"]{

    font-size:18px;

}


[data-testid="stMetricLabel"]{

    font-size:12px;

}



.info-box{

    background:#eeeeee;

    padding:12px;

    border-radius:10px;

    font-size:14px;

    line-height:1.6;

}



.level-box{

    padding:10px;

    border-radius:10px;

    color:white;

    text-align:center;

    font-size:17px;

    font-weight:bold;

}


</style>
""",
unsafe_allow_html=True
)



# ======================================================
# TRANSLATION
# ======================================================

LEVEL_TRANSLATE = {

    "Normal":"ไม่มีขยะ",

    "Low":"ต่ำ",

    "Medium":"ปานกลาง",

    "High":"สูง",

    "Critical":"วิกฤต"

}



LEVEL_COLOR = {

    "Normal":"#4CAF50",

    "Low":"#2196F3",

    "Medium":"#FFC107",

    "High":"#FF9800",

    "Critical":"#F44336"

}



ACTION_TRANSLATE = {

    "No waste detected":
        "ไม่พบขยะ",

    "Monitor area":
        "เฝ้าระวังพื้นที่",

    "Prepare collection":
        "เตรียมวางแผนจัดเก็บขยะ",

    "Notify staff":
        "แจ้งเตือนเจ้าหน้าที่เพื่อดำเนินการจัดเก็บ",

    "Urgent collection":
        "ควรจัดเก็บและนำขยะออกจากพื้นที่ทันที"

}



# ======================================================
# ROI FUNCTION
# ======================================================

def draw_roi(image, roi):

    img = image.copy()


    # Dim background

    dim = cv2.addWeighted(

        img,

        0.35,

        np.zeros_like(img),

        0.65,

        0

    )


    x1,y1,x2,y2 = roi



    # คืนพื้นที่ ROI

    dim[y1:y2, x1:x2] = img[y1:y2, x1:x2]



    # กรอบ ROI สีแดง

    cv2.rectangle(

        dim,

        (x1,y1),

        (x2,y2),

        (0,0,255),

        6

    )


    return dim




# ======================================================
# SESSION
# ======================================================

if "camera_results" not in st.session_state:

    st.session_state.camera_results = {}



if "history" not in st.session_state:

    st.session_state.history = {}



for cam in CAMERA_CONFIG:

    if cam not in st.session_state.history:

        st.session_state.history[cam] = []




# ======================================================
# TITLE
# ======================================================

st.title(
    "🗑 ระบบตรวจสอบปริมาณขยะด้วย AI"
)


st.caption(
    "YOLOv11-Seg + Waste Area Ratio (WAR)"
)



# ======================================================
# UPLOAD
# ======================================================

st.sidebar.header(
    "📷 อัปโหลดภาพ CCTV"
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



            if len(st.session_state.history[cam]) > 20:

                st.session_state.history[cam].pop(0)





# ======================================================
# DASHBOARD
# ======================================================

for cam,data in st.session_state.camera_results.items():


    config = CAMERA_CONFIG[cam]


    st.divider()


    st.header(

        f"📷 {cam} : {config['name']}"

    )


    img = data["original"]

    result = data["result"]



    roi_img = draw_roi(

        img,

        config["roi"]

    )



    c1,c2 = st.columns(2)



    with c1:


        st.image(

            cv2.cvtColor(

                roi_img,

                cv2.COLOR_BGR2RGB

            ),

            width=420,

            caption="📷 ภาพ CCTV + ROI"

        )



    with c2:


        st.image(

            cv2.cvtColor(

                result["image"],

                cv2.COLOR_BGR2RGB

            ),

            width=420,

            caption="🤖 ผล Segmentation"

        )




    a,b,c = st.columns(3)



    with a:

        st.metric(

            "🗑 พื้นที่ขยะ (WAR)",

            f'{result["WAR"]:.2f}%'

        )



    with b:

        st.metric(

            "📈 การเปลี่ยนแปลง",

            f'{result["change"]:+.2f}%'

        )



    with c:


        level = result["level"]


        st.markdown(

        f"""

        <div class="level-box"

        style="background:{LEVEL_COLOR.get(level,"#777")}">

        📊 ระดับความหนาแน่น<br>

        {LEVEL_TRANSLATE.get(level,level)}

        </div>

        """,

        unsafe_allow_html=True

        )





    action = ACTION_TRANSLATE.get(

        result["action"],

        result["action"]

    )



    st.markdown(

    f"""

    <div class="info-box">

    <b>📌 คำแนะนำการจัดการขยะ</b><br><br>

    {action}

    </div>

    """,

    unsafe_allow_html=True

    )




    # ==================================================
    # HISTORY
    # ==================================================

    st.subheader(

        "📋 ประวัติการตรวจสอบ"

    )



    for item in reversed(

        st.session_state.history[cam][-5:]

    ):


        with st.expander(

            f'{item["Time"]} | {LEVEL_TRANSLATE.get(item["Level"],item["Level"])}'

        ):


            h1,h2 = st.columns(2)



            with h1:

                st.image(

                    cv2.cvtColor(

                        item["Original"],

                        cv2.COLOR_BGR2RGB

                    ),

                    width=300,

                    caption="ภาพต้นฉบับ"

                )



            with h2:

                st.image(

                    cv2.cvtColor(

                        item["Segmentation"],

                        cv2.COLOR_BGR2RGB

                    ),

                    width=300,

                    caption="ผล AI"

                )



            st.write(

                f"🗑 พื้นที่ขยะ : {item['WAR']:.2f}%"

            )


            st.write(

                f"📈 การเปลี่ยนแปลง : {item['Change']:+.2f}%"

            )


            st.write(

                f"📊 ระดับ : {LEVEL_TRANSLATE.get(item['Level'],item['Level'])}"

            )
