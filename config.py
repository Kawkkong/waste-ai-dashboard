# =========================================
# Camera Configuration
# =========================================


CAMERA_CONFIG = {


"camera1": {

    "name":"หน้าโรงเรียน",

    "roi":
    {
        "x1":1080,
        "y1":370,
        "x2":1920,
        "y2":1080
    },


    # WAR threshold
    "threshold":
    {
        "normal":0,
        "low":20,
        "medium":40,
        "high":60
    }

},



"camera2": {

    "name":"ข้างตึกอีพี",

    "roi":
    {
        "x1":0,
        "y1":300,
        "x2":550,
        "y2":800
    },


    "threshold":
    {
        "normal":0,
        "low":15,
        "medium":30,
        "high":50
    }

}


}
