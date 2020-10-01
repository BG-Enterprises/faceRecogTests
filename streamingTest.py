import cv2

IP_ADDRESS = "192.168.0.2"
PORT = "554"

MODE = str(1)
CHANNEL="1"
source=0
#source=f"rtsp://admin:ragavan20@{IP_ADDRESS}:{PORT}/cam/realmonitor?channel={CHANNEL}&subtype={MODE}"


CAP = cv2.VideoCapture(source)
"""
for i in range(5*15):
    CAP.read()
"""
while CAP.isOpened():
    _,frame = CAP.read()
    out = cv2.resize(
            frame,
            (
                int(frame.shape[1]*0.2),
                int(frame.shape[0]*0.2)
            )
    )
    cv2.imshow('Video',out)
    print("=")
    cv2.waitKey(10)
