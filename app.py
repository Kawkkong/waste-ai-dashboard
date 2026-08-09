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

.block-container{

    padding-top:1rem;

    padding-left:1.5rem;

    padding-right:1.5rem;

}


.card{

    height:95px;

    padding:10px;

    border-radius:12px;

    background:#f3f3f3;

    text-align:center;

}


.card-title{

    font-size:13px;

    color:#555;

}


.card-value{

    margin-top:8px;

    font-size:22px;

    font-weight:bold;

}



.action-card{

    min-height:90px;

    padding:12px;

    border-radius:12px;

    background:#eeeeee;

    font-size:14px;

    line-height:1.6;

}



</style>
""",
unsafe_allow_html=True
)




# ======================================================
# TRANSLATE
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

    "Medium":"#FFD600",

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
# IMAGE PROCESS
# ======================================================


def create_ai_view(image, segmentation, roi):


    # ภาพ CCTV จริง

    base = image.copy()



    # dim ทั้งภาพ

    dim = cv2.addWeighted(

        base,

        0.3,

        np.zeros_like(base),

        0.7,

        0

    )



    # เอา segmentation มาทับ

    if segmentation is not None:


        mask = cv2.cvtColor(

            segmentation,

            cv2.COLOR_BGR2GRAY

        )


        _, mask = cv2.threshold(

            mask,

            10,

            255,

            cv2.THRESH_BINARY

        )



        # พื้นที่ที่ AI เจอ

        dim[mask > 0] = base[mask > 0]



        # overlay สีเขียว

        overlay = dim.copy()


        overlay[mask > 0] = (

            0,

            255,

            0

        )


        dim = cv2.addWeighted(

            dim,

            0.75,

            overlay,

            0.25,

            0

        )



    # ROI สีแดง

    x1,y1,x2,y2 = roi


    cv2.rectangle(

        dim,

        (x1,y1),

        (x2,y2),

        (0,0,255),

        5

    )


    return dim





# ======================================================
# SESSION
# ======================================================


if "camera_results" not in st.session_state:

    st.session_state.camera_results={}



if "history" not in st.session_state:

    st.session_state.history={}



for cam in CAMERA_CONFIG:

    if cam not in st.session_state.history:

        st.session_state.history[cam]=[]





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


    upload = st.sidebar.file_uploader(

        cam,

        type=["jpg","jpeg","png"],

        key=cam

    )



    if upload:


        file_id=(

            upload.name,

            upload.size

        )



        old_file=(

            st.session_state.camera_results

            .get(cam,{})

            .get("file_id")

        )



        if file_id != old_file:


            img=cv2.imdecode(

                np.asarray(

                    bytearray(

                        upload.read()

                    ),

                    dtype=np.uint8

                ),

                cv2.IMREAD_COLOR

            )



            result=analyze_frame(

                img,

                cam

            )



            st.session_state.camera_results[cam]={

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






# ======================================================
# DASHBOARD
# ======================================================


for cam,data in st.session_state.camera_results.items():


    config = CAMERA_CONFIG[cam]


    img = data["original"]

    result = data["result"]



    st.divider()



    st.header(

        f"📷 {cam} : {config['name']}"

    )



    ai_view=create_ai_view(

        img,

        result["image"],

        config["roi"]

    )



    c1,c2=st.columns(2)



    with c1:

        st.image(

            cv2.cvtColor(

                img,

                cv2.COLOR_BGR2RGB

            ),

            width=380,

            caption="📷 ภาพ CCTV"

        )



    with c2:

        st.image(

            cv2.cvtColor(

                ai_view,

                cv2.COLOR_BGR2RGB

            ),

            width=380,

            caption="🤖 AI Detection + ROI"

        )





    # =========================
    # STATUS CARD
    # =========================


    a,b,c=st.columns(3)



    with a:

        st.markdown(

        f"""

        <div class="card">

        <div class="card-title">
        🗑 พื้นที่ขยะ
        </div>

        <div class="card-value">

        {result["WAR"]:.2f}%

        </div>

        </div>

        """,

        unsafe_allow_html=True

        )



    raw_level=result["level"]



    if isinstance(raw_level,dict):

        raw_level=raw_level.get(
            "level",
            "Normal"
        )



    level=LEVEL_TRANSLATE.get(

        raw_level,

        raw_level

    )



    with b:

        st.markdown(

        f"""

        <div class="card"

        style="background:{LEVEL_COLOR.get(raw_level,'#777')}">

        <div class="card-title"
        style="color:white">

        📊 ระดับความหนาแน่น

        </div>


        <div class="card-value"
        style="color:white">

        {level}

        </div>

        </div>

        """,

        unsafe_allow_html=True

        )



    with c:

        st.markdown(

        f"""

        <div class="card">

        <div class="card-title">
        📈 การเปลี่ยนแปลง
        </div>


        <div class="card-value">

        {result["change"]:+.2f}%

        </div>

        </div>

        """,

        unsafe_allow_html=True

        )





    action=ACTION_TRANSLATE.get(

        result["action"],

        result["action"]

    )



    st.markdown(

    f"""

    <div class="action-card">

    <b>📌 คำแนะนำการจัดการขยะ</b>

    <br><br>

    {action}

    </div>

    """,

    unsafe_allow_html=True

    )
