import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import base64

from datetime import datetime

from inference import analyze_frame
from config import CAMERA_CONFIG




# =====================================================
# FULLSCREEN IMAGE VIEWER
# =====================================================

def show_image_viewer(img_bgr, title="", display_width=400, viewer_height=330):
    """
    แสดงภาพขนาดพอดี และมีปุ่ม/คลิกเพื่อเปิดภาพเต็มหน้าจอจริง
    ใช้ Browser Fullscreen API ภายใน Streamlit component
    """
    if img_bgr is None:
        return

    ok, encoded = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 92])

    if not ok:
        st.error("ไม่สามารถแสดงภาพได้")
        return

    image_b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: "IBM Plex Sans Thai", "Noto Sans Thai", Arial, sans-serif;
                overflow: hidden;
            }}

            .viewer {{
                position: relative;
                width: min(100%, {display_width}px);
                height: {viewer_height}px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #111827;
                border-radius: 10px;
                overflow: hidden;
                cursor: zoom-in;
            }}

            .viewer img {{
                width: 100%;
                height: 100%;
                object-fit: contain;
                display: block;
            }}

            .zoom-btn {{
                position: absolute;
                right: 10px;
                top: 10px;
                z-index: 10;
                border: 0;
                border-radius: 8px;
                padding: 7px 10px;
                background: rgba(0,0,0,.65);
                color: white;
                font-size: 14px;
                cursor: pointer;
                backdrop-filter: blur(4px);
            }}

            .zoom-btn:hover {{
                background: rgba(0,0,0,.85);
            }}

            .viewer:fullscreen {{
                width: 100vw;
                height: 100vh;
                max-width: none;
                border-radius: 0;
                background: #000;
                cursor: zoom-out;
            }}

            .viewer:fullscreen img {{
                object-fit: contain;
                width: 100vw;
                height: 100vh;
            }}
        </style>
    </head>

    <body>
        <div class="viewer" id="viewer" title="คลิกเพื่อขยายเต็มหน้าจอ">
            <button class="zoom-btn" id="zoom">⛶ ขยายภาพ</button>
            <img src="data:image/jpeg;base64,{image_b64}" alt="{title}">
        </div>

        <script>
            const viewer = document.getElementById("viewer");
            const zoom = document.getElementById("zoom");

            async function toggleFullscreen() {{
                try {{
                    if (!document.fullscreenElement) {{
                        await viewer.requestFullscreen();
                    }} else {{
                        await document.exitFullscreen();
                    }}
                }} catch (e) {{
                    console.log("Fullscreen unavailable:", e);
                }}
            }}

            zoom.addEventListener("click", (e) => {{
                e.stopPropagation();
                toggleFullscreen();
            }});

            viewer.addEventListener("dblclick", (e) => {{
                if (e.target !== zoom) {{
                    toggleFullscreen();
                }}
            }});

            document.addEventListener("fullscreenchange", () => {{
                zoom.textContent = document.fullscreenElement
                    ? "⛶ ออกจากเต็มหน้าจอ"
                    : "⛶ ขยายภาพ";
            }});
        </script>
    </body>
    </html>
    """

    components.html(
        html,
        height=viewer_height + 8,
        scrolling=False
    )


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

@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"],
[data-testid="stHeader"], [data-testid="stSidebar"],
button, input, textarea, select {
    font-family: 'IBM Plex Sans Thai', 'Noto Sans Thai', Tahoma, sans-serif !important;
}

[data-testid="stAppViewContainer"] { font-size: 14px; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { line-height: 1.55; }
[data-testid="stMetricValue"] { font-family: 'IBM Plex Sans Thai', 'Noto Sans Thai', Tahoma, sans-serif !important; }
[data-testid="stMetricLabel"] { font-family: 'IBM Plex Sans Thai', 'Noto Sans Thai', Tahoma, sans-serif !important; }

 .collection-section {
    margin-top: 30px; padding: 22px 18px 26px; border-radius: 18px;
    background: linear-gradient(180deg,#f8fafc 0%,#eef2f7 100%);
    border: 1px solid #d9e1ea; overflow:hidden;
}
.collection-title { text-align:center; font-size:22px; font-weight:700; color:#26364a; margin-bottom:4px; }
.collection-subtitle { text-align:center; color:#667085; font-size:13px; margin-bottom:16px; }
.collection-road { position:relative; height:118px; margin:0 12px 18px; border-radius:20px; background:linear-gradient(180deg,#4b5563 0%,#374151 100%); box-shadow:inset 0 5px 12px rgba(0,0,0,.20); overflow:hidden; }
.collection-road::before { content:''; position:absolute; left:0; right:0; top:57%; height:5px; transform:translateY(-50%); background:repeating-linear-gradient(90deg,#f8fafc 0 42px,transparent 42px 72px); opacity:.9; }
.collection-road::after { content:'→  เส้นทางการจัดเก็บขยะ  →'; position:absolute; left:50%; bottom:9px; transform:translateX(-50%); color:rgba(255,255,255,.82); font-size:12px; font-weight:600; white-space:nowrap; }
.collection-truck { position:absolute; top:26px; left:1.5%; font-size:38px; z-index:5; filter:drop-shadow(0 4px 3px rgba(0,0,0,.28)); animation:collectionDriveOneWay 10s linear infinite; }
@keyframes collectionDriveOneWay { 0% { left:1.5%; transform:translateX(0); } 100% { left:96%; transform:translateX(-100%); } }
.collection-checkpoints { position:absolute; left:3%; right:3%; top:35px; height:45px; z-index:2; display:flex; align-items:center; justify-content:space-between; }
.collection-checkpoint { position:relative; width:28px; height:28px; border-radius:50%; border:4px solid #fff; box-shadow:0 2px 7px rgba(0,0,0,.28); }
.collection-checkpoint-label { position:absolute; top:32px; left:50%; transform:translateX(-50%); color:#fff; font-size:11px; font-weight:700; white-space:nowrap; text-shadow:0 1px 2px rgba(0,0,0,.65); }
.collection-arrow { position:absolute; top:47px; left:0; right:0; text-align:center; color:#fff; font-size:22px; opacity:.9; }
.collection-stops { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:10px; }
.collection-stop { position:relative; background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:11px 12px; box-shadow:0 2px 8px rgba(15,23,42,.05); }
.collection-rank { position:absolute; top:9px; right:10px; width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:12px; }
.collection-camera { font-size:14px; font-weight:700; color:#1f2937; padding-right:34px; }
.collection-war { font-size:20px; font-weight:700; color:#111827; margin-top:5px; }
.collection-level { font-size:12px; color:#667085; margin-top:2px; }
.collection-detail { font-size:11px; color:#7a8492; margin-top:6px; line-height:1.5; }
.collection-note { margin-top:14px; text-align:center; font-size:12px; color:#667085; }
.collection-rule { margin:10px auto 18px; max-width:720px; text-align:center; font-size:12px; color:#475467; background:#fff; border:1px solid #e4e7ec; border-radius:10px; padding:9px 12px; }
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


        show_image_viewer(
            data["original"],
            title="ภาพจากกล้อง",
            display_width=400,
            viewer_height=300
        )





    with c2:


        st.subheader(

            "ผล Segmentation"

        )


        show_image_viewer(
            result["image"],
            title="ผล Segmentation",
            display_width=400,
            viewer_height=300
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





            show_image_viewer(
                item["ผล"],
                title="ผล Segmentation จากข้อมูลที่เลือก",
                display_width=400,
                viewer_height=300
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


                    show_image_viewer(
                        item["ภาพ"],
                        title="ภาพต้นฉบับ",
                        display_width=330,
                        viewer_height=250
                    )





                with h2:


                    show_image_viewer(
                        item["ผล"],
                        title="ผล Segmentation",
                        display_width=330,
                        viewer_height=250
                    )

# =====================================================
# ลำดับการจัดเก็บขยะ
# =====================================================

st.divider()

LEVEL_ORDER = {
    "Normal": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4,
}

collection_priority = []
reference_roi_area = 0

for cam, data in st.session_state.camera_results.items():
    result = data.get("result", {})
    cfg = CAMERA_CONFIG.get(cam, {})
    roi = cfg.get("roi", (0, 0, 0, 0))

    try:
        x1, y1, x2, y2 = [int(v) for v in roi]
        roi_area = max(0, x2 - x1) * max(0, y2 - y1)
    except (TypeError, ValueError):
        roi_area = 0

    garbage_mask = result.get("mask")
    garbage_pixels = int(np.sum(np.asarray(garbage_mask) > 0)) if garbage_mask is not None else 0

    level = result.get("level", "Normal")
    war = float(result.get("WAR", 0))
    reference_roi_area = max(reference_roi_area, roi_area)

    collection_priority.append({
        "camera": cam,
        "WAR": war,
        "level": level,
        "level_rank": LEVEL_ORDER.get(level, 0),
        "roi_area": roi_area,
        "garbage_pixels": garbage_pixels,
    })

for item in collection_priority:
    if item["roi_area"] > 0 and reference_roi_area > 0:
        item["normalized_garbage_pixels"] = item["garbage_pixels"] * reference_roi_area / item["roi_area"]
    else:
        item["normalized_garbage_pixels"] = 0.0

collection_priority.sort(
    key=lambda item: (item["normalized_garbage_pixels"], item["level_rank"]),
    reverse=True
)

st.markdown(
    """
    <section class="collection-section">
        <div class="collection-title">🚛 ลำดับการจัดเก็บขยะ</div>
        <div class="collection-subtitle">รถเก็บขยะเดินทางทางเดียวจากจุดที่ควรจัดเก็บก่อน → จุดที่ควรจัดเก็บภายหลัง</div>
    """,
    unsafe_allow_html=True
)

if len(collection_priority) == 0:
    st.info("ยังไม่มีข้อมูลจากกล้องสำหรับจัดลำดับการจัดเก็บขยะ")
else:
    checkpoint_html = []
    for rank, item in enumerate(collection_priority, start=1):
        info = LEVEL_INFO.get(item["level"], LEVEL_INFO["Normal"])
        checkpoint_html.append(
            f'<div class="collection-checkpoint" style="background:{info["color"]};">'
            f'<span class="collection-checkpoint-label">{rank}. {item["camera"]}</span>'
            f'</div>'
        )

    road_html = (
        '<div class="collection-road">'
        '<div class="collection-checkpoints">' + ''.join(checkpoint_html) + '</div>'
        '<div class="collection-arrow">→</div>'
        '<div class="collection-truck">🚛</div>'
        '</div>'
    )
    st.markdown(road_html, unsafe_allow_html=True)

    st.markdown(
        f'<div class="collection-rule"><b>หลักการจัดลำดับ:</b> พื้นที่ขยะหลังปรับ ROI เป็นตัวหลัก → หากมีค่าใกล้เคียงกันจึงใช้ระดับความหนาแน่นเป็นตัวช่วยตัดสิน<br>พื้นที่ ROI อ้างอิง = <b>{reference_roi_area:,} px</b></div>',
        unsafe_allow_html=True
    )

    cards = []
    for rank, item in enumerate(collection_priority, start=1):
        info = LEVEL_INFO.get(item["level"], LEVEL_INFO["Normal"])
        cards.append(
            f'<div class="collection-stop">'
            f'<div class="collection-rank" style="background:{info["color"]};">{rank}</div>'
            f'<div class="collection-camera">📷 {item["camera"]}</div>'
            f'<div class="collection-war">WAR {item["WAR"]:.2f}%</div>'
            f'<div class="collection-level">{info["name"]}</div>'
            f'<div class="collection-detail">ขยะจริง: {item["garbage_pixels"]:,} px<br>ROI: {item["roi_area"]:,} px<br>ขยะเทียบ ROI อ้างอิง: {item["normalized_garbage_pixels"]:,.1f} px</div>'
            f'</div>'
        )

    st.markdown('<div class="collection-stops">' + ''.join(cards) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="collection-note">อันดับ 1 คือ checkpoint แรกของเส้นทาง และรถจะวิ่งต่อไปตามลำดับจนถึง checkpoint สุดท้าย</div>', unsafe_allow_html=True)

st.markdown('</section>', unsafe_allow_html=True)

