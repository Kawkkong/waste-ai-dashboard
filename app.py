import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px

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

        "name":"Normal (ไม่มีขยะ)",

        "color":"#4CAF50",

        "action":"ไม่พบขยะ"

    },


    "Low": {

        "name":"Low (ต่ำ)",

        "color":"#2196F3",

        "action":"เฝ้าระวังพื้นที่"

    },


    "Medium": {

        "name":"Medium (ปานกลาง)",

        "color":"#FFD600",

        "action":"เตรียมวางแผนเก็บขยะ"

    },


    "High": {

        "name":"High (สูง)",

        "color":"#FF9800",

        "action":"แจ้งเตือนเจ้าหน้าที่"

    },


    "Critical": {

        "name":"Critical (วิกฤต)",

        "color":"#F44336",

        "action":"แจ้งเตือนด่วนและดำเนินการเก็บขยะทันที"

    }

}





# =====================================================
# CSS SMALL UI
# =====================================================

st.markdown(

"""

<style>


h1{

font-size:28px !important;

}


h2{

font-size:20px !important;

}


h3{

font-size:16px !important;

}



.level-box{

padding:8px;

border-radius:8px;

font-size:14px;

font-weight:bold;

margin-bottom:5px;

}



.recommend{

background:#eeeeee;

padding:8px;

border-radius:8px;

font-size:13px;

}



[data-testid="stMetricValue"]{

font-size:20px;

}



[data-testid="stMetricLabel"]{

font-size:12px;

}

@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"],
[data-testid="stHeader"], [data-testid="stSidebar"] {
    font-family: 'Noto Sans Thai', 'Sarabun', Tahoma, sans-serif !important;
}

[data-testid="stAppViewContainer"] { font-size: 14px; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { line-height: 1.55; }

.collection-section {
    margin-top: 28px; padding: 20px 18px 24px; border-radius: 18px;
    background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
    border: 1px solid #d9e1ea; overflow: hidden;
}
.collection-title { text-align:center; font-size:22px; font-weight:700; color:#26364a; margin-bottom:4px; }
.collection-subtitle { text-align:center; color:#667085; font-size:13px; margin-bottom:18px; }
.collection-road {
    position:relative; height:92px; margin:0 10px 18px; border-radius:18px;
    background:linear-gradient(180deg,#4b5563 0%,#374151 100%);
    box-shadow:inset 0 4px 10px rgba(0,0,0,.18); overflow:hidden;
}
.collection-road::before {
    content:''; position:absolute; left:0; right:0; top:50%; height:5px; transform:translateY(-50%);
    background:repeating-linear-gradient(90deg,#f8fafc 0 42px,transparent 42px 72px); opacity:.85;
}
.collection-truck {
    position:absolute; top:23px; left:2%; font-size:40px; z-index:3;
    filter:drop-shadow(0 4px 3px rgba(0,0,0,.25)); animation:collectionDrive 8s ease-in-out infinite;
}
@keyframes collectionDrive {
    0% { left:2%; transform:translateX(0); }
    45% { left:72%; transform:translateX(-50%); }
    55% { left:72%; transform:translateX(-50%); }
    100% { left:2%; transform:translateX(0); }
}
.collection-stops { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; }
.collection-stop { position:relative; background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:11px 12px; box-shadow:0 2px 8px rgba(15,23,42,.05); }
.collection-rank {
    position:absolute; top:9px; right:10px; width:26px; height:26px; border-radius:50%;
    display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:12px;
}
.collection-camera { font-size:14px; font-weight:700; color:#1f2937; padding-right:30px; }
.collection-war { font-size:20px; font-weight:700; color:#111827; margin-top:5px; }
.collection-level { font-size:12px; color:#667085; margin-top:2px; }
.collection-note { margin-top:14px; text-align:center; font-size:12px; color:#667085; }

</style>


""",

unsafe_allow_html=True

)





# =====================================================
# SESSION
# =====================================================

if "camera_results" not in st.session_state:

    st.session_state.camera_results = {}



if "history" not in st.session_state:

    st.session_state.history = {}



if "selected_history" not in st.session_state:

    st.session_state.selected_history = None




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
# UPLOAD CCTV IMAGE
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




            history_id = len(

                st.session_state.history[cam]

            )




            st.session_state.history[cam].append({


                "ID":

                history_id,


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
# DISPLAY CAMERA
# =====================================================

for cam, data in st.session_state.camera_results.items():


    result = data["result"]


    level = result["level"]


    info = LEVEL_INFO[level]



    st.divider()



    st.header(

        f"📷 {cam}"

    )





    # =========================
    # LEVEL
    # =========================

    st.markdown(
        f'<div style="background-color:{info["color"]}; padding:8px 12px; border-radius:8px; font-size:14px; font-weight:600; margin-bottom:6px;">'
        f'ระดับความหนาแน่นของขยะ<br>{info["name"]}'
        f'</div>',
        unsafe_allow_html=True
    )





    # =========================
    # ACTION
    # =========================

    st.markdown(

        f"""

        <div class="recommend">

        <b>คำแนะนำ:</b>

        {info['action']}

        </div>


        """,

        unsafe_allow_html=True

    )







    # =========================
    # IMAGE
    # =========================

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

            width=400

        )





    with c2:


        st.subheader(

            "ผล Segmentation"

        )


        st.image(

            cv2.cvtColor(

                result["image"],

                cv2.COLOR_BGR2RGB

            ),

            width=400

        )






    # =========================
    # CURRENT RESULT
    # =========================

    st.subheader(

        "📊 ผลการวิเคราะห์"

    )



    a,b,c = st.columns(3)



    a.metric(

        "WAR",

        f'{result["WAR"]}%'

    )


    b.metric(

        "เปลี่ยนแปลง",

        f'{result["change"]:+.2f}%'

    )


    c.metric(

        "ระดับ",

        info["name"]

    )






    # =========================
    # GRAPH
    # =========================

    st.subheader(

        f"📈 แนวโน้ม WAR : {cam}"

    )



    if len(st.session_state.history[cam]) > 0:


        graph_data = pd.DataFrame(

            st.session_state.history[cam]

        )



        fig = px.line(

            graph_data,

            x="เวลา",

            y="WAR",

            markers=True,

            title=None

        )


        fig.update_layout(

            height=180,

            margin=dict(

                l=20,

                r=20,

                t=20,

                b=20

            )

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )
        # =========================
        # SELECTED GRAPH DATA
        # =========================

        if st.session_state.selected_history is not None:


            item = st.session_state.selected_history


            st.subheader(

                "🔎 ข้อมูลที่เลือกจากกราฟ"

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



            selected_info = LEVEL_INFO[

                item["ระดับ"]

            ]



            z.metric(

                "ระดับ",

                selected_info["name"]

            )





            st.image(

                cv2.cvtColor(

                    item["ผล"],

                    cv2.COLOR_BGR2RGB

                ),

                caption="ผล Segmentation จากข้อมูลที่เลือก",

                width=400

            )







    # =================================================
    # HISTORY
    # =================================================

    st.subheader(

        f"📋 ประวัติการตรวจสอบ {cam}"

    )



    histories = st.session_state.history[cam]



    if len(histories) == 0:


        st.info(

            "ยังไม่มีประวัติ"

        )



    else:


        for item in reversed(histories):


            history_info = LEVEL_INFO[

                item["ระดับ"]

            ]



            with st.expander(

                f'#{item["ID"]+1} | '

                f'{item["เวลา"]} | '

                f'{history_info["name"]}'

            ):



                # -------------------------
                # LEVEL
                # -------------------------

                st.markdown(
                    f'<div style="background-color:{history_info["color"]}; padding:8px 12px; border-radius:8px; font-size:14px; font-weight:600; margin-bottom:6px;">'
                    f'{history_info["name"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )





                # -------------------------
                # DATA
                # -------------------------

                a,b,c = st.columns(3)



                a.metric(

                    "WAR",

                    f'{item["WAR"]}%'

                )


                b.metric(

                    "เปลี่ยนแปลง",

                    f'{item["เปลี่ยนแปลง"]:+.2f}%'

                )


                c.metric(

                    "ระดับ",

                    history_info["name"]

                )







                # -------------------------
                # IMAGES
                # -------------------------

                h1,h2 = st.columns(2)



                with h1:


                    st.image(

                        cv2.cvtColor(

                            item["ภาพ"],

                            cv2.COLOR_BGR2RGB

                        ),

                        caption="ภาพต้นฉบับ",

                        width=400

                    )





                with h2:


                    st.image(

                        cv2.cvtColor(

                            item["ผล"],

                            cv2.COLOR_BGR2RGB

                        ),

                        caption="ผล Segmentation",

                        width=400

                    )

# =====================================================
# ลำดับการจัดเก็บขยะ
# =====================================================

st.divider()

collection_priority = []

for cam, data in st.session_state.camera_results.items():
    result = data.get("result", {})
    if "WAR" in result:
        collection_priority.append({
            "camera": cam,
            "WAR": float(result.get("WAR", 0)),
            "level": result.get("level", "Normal")
        })

collection_priority.sort(key=lambda item: item["WAR"], reverse=True)

section_html = """
<section class="collection-section">
    <div class="collection-title">🚛 ลำดับการจัดเก็บขยะ</div>
    <div class="collection-subtitle">เรียงลำดับจากค่า WAR สูงที่สุด → ต่ำที่สุด เพื่อช่วยวางแผนเส้นทางการเก็บขยะ</div>
    <div class="collection-road"><div class="collection-truck">🚛</div></div>
</section>
"""

st.markdown(section_html, unsafe_allow_html=True)

if len(collection_priority) == 0:
    st.info("ยังไม่มีข้อมูลจากกล้องสำหรับจัดลำดับการจัดเก็บขยะ")
else:
    cards = []
    for rank, item in enumerate(collection_priority, start=1):
        info = LEVEL_INFO.get(item["level"], LEVEL_INFO["Normal"])
        cards.append(
            f'<div class="collection-stop">'
            f'<div class="collection-rank" style="background:{info["color"]};">{rank}</div>'
            f'<div class="collection-camera">📷 {item["camera"]}</div>'
            f'<div class="collection-war">{item["WAR"]:.2f}%</div>'
            f'<div class="collection-level">{info["name"]}</div>'
            f'</div>'
        )

    st.markdown(
        '<div class="collection-stops">' + ''.join(cards) + '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="collection-note">อันดับ 1 คือจุดที่มีพื้นที่ขยะสูงที่สุดและควรพิจารณาเข้าจัดเก็บก่อน</div>',
        unsafe_allow_html=True
    )

