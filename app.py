for cam, data in st.session_state.camera_results.items():

    st.divider()

    st.header(f"📷 กล้อง {cam}")


    img = data["original"]

    result = data["result"]



    # =========================
    # IMAGE DISPLAY
    # =========================

    c1, c2 = st.columns(2)


    with c1:

        st.image(
            cv2.cvtColor(
                img,
                cv2.COLOR_BGR2RGB
            ),
            use_container_width=True,
            caption="📷 ภาพจากกล้อง CCTV"
        )


    with c2:

        st.image(
            cv2.cvtColor(
                result["image"],
                cv2.COLOR_BGR2RGB
            ),
            use_container_width=True,
            caption="🤖 ผลการแบ่งพื้นที่ขยะด้วย AI (Segmentation)"
        )



    # =========================
    # RESULT
    # =========================

    a,b,c,d = st.columns(4)


    a.metric(
        "🗑 อัตราส่วนพื้นที่ขยะ (WAR)",
        f'{result["WAR"]:.2f}%'
    )


    b.metric(
        "📈 การเปลี่ยนแปลง",
        f'{result["change"]:+.2f}%'
    )


    # แปลระดับขยะ

    level_translate = {

        "Normal": "ไม่มีขยะ",

        "Low": "ต่ำ",

        "Medium": "ปานกลาง",

        "High": "สูง",

        "Critical": "วิกฤต"

    }


    thai_level = level_translate.get(
        result["level"],
        result["level"]
    )


    c.metric(
        "📊 ระดับความหนาแน่น",
        thai_level
    )



    action_translate = {

        "No waste detected": 
        "ไม่พบขยะ",

        "Monitor area":
        "เฝ้าระวังพื้นที่",

        "Prepare collection":
        "เตรียมวางแผนเก็บขยะ",

        "Notify staff":
        "แจ้งเตือนเจ้าหน้าที่",

        "Urgent collection":
        "ดำเนินการเก็บขยะทันที"

    }


    thai_action = action_translate.get(
        result["action"],
        result["action"]
    )


    d.metric(
        "📌 คำแนะนำ",
        thai_action
    )



    # =========================
    # HISTORY
    # =========================

    st.subheader(
        f"📋 ประวัติการตรวจสอบ - {cam}"
    )


    for item in reversed(
        st.session_state.history[cam][-5:]
    ):


        history_level = level_translate.get(
            item["Level"],
            item["Level"]
        )


        with st.expander(
            f'{item["Time"]} | ระดับ: {history_level}'
        ):


            h1,h2 = st.columns(2)


            with h1:

                st.image(

                    cv2.cvtColor(
                        item["Original"],
                        cv2.COLOR_BGR2RGB
                    ),

                    use_container_width=True,

                    caption="ภาพต้นฉบับ"

                )


            with h2:

                st.image(

                    cv2.cvtColor(
                        item["Segmentation"],
                        cv2.COLOR_BGR2RGB
                    ),

                    use_container_width=True,

                    caption="ภาพผล AI"

                )



            x1,x2,x3,x4 = st.columns(4)



            x1.metric(
                "🗑 พื้นที่ขยะ",
                f'{item["WAR"]:.2f}%'
            )


            x2.metric(
                "📈 เปลี่ยนแปลง",
                f'{item["Change"]:+.2f}%'
            )


            x3.metric(
                "📊 ระดับ",
                history_level
            )


            x4.metric(
                "📌 การดำเนินการ",
                action_translate.get(
                    item["Action"],
                    item["Action"]
                )
            )
