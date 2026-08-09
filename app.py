import streamlit as st
import cv2
import numpy as np

from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG



# ======================================================
# PAGE
# ======================================================

st.set_page_config(
    page_title="Waste AI Dashboard",
    layout="wide"
)



# ======================================================
# CSS
# ======================================================

st.markdown(
"""
<style>

.block-container{

    padding-top:0.8rem;

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

    line-height:1.5;

}



</style>
""",
unsafe_allow_html=True
)



# ======================================================
# TRANSLATE
# ======================================================

LEVEL_TRANSLATE={

    "Normal":"ไม่มีขยะ",

    "Low":"ต่ำ",

    "Medium":"ปานกลาง",

    "High":"สูง",

    "Critical":"วิกฤต"

}



LEVEL_COLOR={

    "Normal":"#4CAF50",

    "Low":"#2196F3",

    "Medium":"#FFD600",

    "High":"#FF9800",

    "Critical":"#F44336",

}



ACTION_TRANSLATE={

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
# FUNCTION
# ======================================================


def dim_mask(image, mask):

    """

    ทำให้พื้นที่ที่ไม่ใช่ขยะมืดลง

    """

    dark = np.zeros_like(image)

    dark[:] = (40,40,40)


    output=np.where(

        mask[:,:,None]>0,

        image,

        dark

    )


    return output.astype(np.uint8)





def draw_roi(image,roi):


    img=image.copy()


    x1,y1,x2,y2=roi


    cv2.rectangle(

        img,

        (x1,y1),

        (x2,y2),

        (0,0,255),

        5

    )


    return img




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


    upload=st.sidebar.file_uploader(

        cam,

        type=["jpg","jpeg","png"],

        key=cam

    )



    if upload:


        file_id=(

            upload.name,

            upload.size

        )



        old=(

            st.session_state.camera_results

            .get(cam,{})

            .get("file_id")

        )



        if file_id!=old:


            img=cv2.imdecode(

                np.asarray(

                    bytearray(upload.read()),

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


    config=CAMERA_CONFIG[cam]


    st.divider()


    st.header(

        f"📷 {cam} - {config['name']}"

    )



    img=data["original"]

    result=data["result"]



    # ROI

    roi_img=draw_roi(

        img,

        config["roi"]

    )



    # Mask dim

    if "mask" in result:

        mask_img=dim_mask(

            result["image"],

            result["mask"]

        )

    else:

        mask_img=result["image"]




    c1,c2=st.columns(2)



    with c1:


        st.image(

            cv2.cvtColor(

                roi_img,

                cv2.COLOR_BGR2RGB

            ),

            width=380,

            caption="📷 CCTV + ROI"

        )



    with c2:


        st.image(

            cv2.cvtColor(

                mask_img,

                cv2.COLOR_BGR2RGB

            ),

            width=380,

            caption="🤖 AI Detection"

        )





    # =========================
    # CARD
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




    level=LEVEL_TRANSLATE.get(

        result["level"],

        result["level"]

    )



    with b:

        st.markdown(

        f"""

        <div class="card"

        style="background:{LEVEL_COLOR.get(result['level'],'#777')}">

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





    # ACTION

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





    # HISTORY


    st.subheader(
        "📋 ประวัติ"
    )


    for item in reversed(

        st.session_state.history[cam][-5:]

    ):


        with st.expander(

            item["Time"]

        ):


            st.write(

                f"WAR : {item['WAR']:.2f}%"

            )


            st.write(

                f"ระดับ : {LEVEL_TRANSLATE.get(item['Level'],item['Level'])}"

            )
