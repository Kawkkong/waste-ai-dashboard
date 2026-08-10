import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import base64
import streamlit.components.v1 as components

from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG



# =====================================================
# IMAGE VIEWER
# =====================================================

def show_image_fullscreen(img_bgr, caption="", width=400, key="image"):
    """แสดงภาพขนาดเล็ก และคลิกปุ่ม/ภาพเพื่อขยายเต็มหน้าจอจริง"""

    ok, encoded = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not ok:
        st.error("ไม่สามารถแสดงภาพได้")
        return

    image_b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")
    h, w = img_bgr.shape[:2]
    ratio = h / w if w else 0.5625
    height = max(120, int(width * ratio))

    html = f"""
    <style>
        html, body {{ margin:0; padding:0; background:transparent; }}
        .viewer {{
            position:relative;
            width:{width}px;
            max-width:100%;
            margin:0 auto;
            border-radius:8px;
            overflow:hidden;
            background:#111;
            line-height:0;
        }}
        .viewer img {{
            display:block;
            width:100%;
            height:auto;
            cursor:zoom-in;
            object-fit:contain;
        }}
        .zoom-btn {{
            position:absolute;
            right:8px;
            top:8px;
            z-index:10;
            border:0;
            border-radius:6px;
            padding:5px 8px;
            background:rgba(0,0,0,.65);
            color:white;
            font-size:16px;
            cursor:pointer;
            line-height:1;
        }}
        :fullscreen {{
            background:#000 !important;
            width:100vw !important;
            height:100vh !important;
            display:flex !important;
            align-items:center !important;
            justify-content:center !important;
        }}
        :fullscreen .viewer {{
            width:100vw !important;
            height:100vh !important;
            max-width:none !important;
            max-height:none !important;
            display:flex !important;
            align-items:center !important;
            justify-content:center !important;
            border-radius:0 !important;
            background:#000 !important;
        }}
        :fullscreen .viewer img {{
            width:auto !important;
            max-width:100vw !important;
            max-height:100vh !important;
            height:auto !important;
            object-fit:contain !important;
            cursor:zoom-out;
        }}
        :fullscreen .zoom-btn {{
            right:18px;
            top:18px;
            font-size:20px;
        }}
    </style>
    <div class="viewer" id="viewer-{key}">
        <button class="zoom-btn" type="button" title="ขยายเต็มหน้าจอ" onclick="toggleFullscreen()">⛶</button>
        <img src="data:image/jpeg;base64,{image_b64}" alt="{caption}" onclick="toggleFullscreen()">
    </div>
    <script>
        const viewer = document.getElementById("viewer-{key}");
        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                if (viewer.requestFullscreen) {{
                    viewer.requestFullscreen();
                }} else if (document.documentElement.requestFullscreen) {{
                    document.documentElement.requestFullscreen();
                }}
            }} else {{
                document.exitFullscreen();
            }}
        }}
    </script>
    """

    components.html(html, height=height + 10, scrolling=False)

    if caption:
        st.caption(caption)


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


        show_image_fullscreen(
            data["original"],
            caption="",
            width=400,
            key=f"{cam}-current-original"
        )





    with c2:


        st.subheader(

            "ผล Segmentation"

        )


        show_image_fullscreen(
            result["image"],
            caption="",
            width=400,
            key=f"{cam}-current-seg"
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





            show_image_fullscreen(
                item["ผล"],
                caption="ผล Segmentation จากข้อมูลที่เลือก",
                width=400,
                key=f"{cam}-selected-seg"
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


                    show_image_fullscreen(
                        item["ภาพ"],
                        caption="ภาพต้นฉบับ",
                        width=320,
                        key=f"{cam}-history-{item['ID']}-original"
                    )





                with h2:


                    show_image_fullscreen(
                        item["ผล"],
                        caption="ผล Segmentation",
                        width=320,
                        key=f"{cam}-history-{item['ID']}-seg"
                    )
