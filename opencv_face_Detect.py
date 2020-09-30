import cv2
import time
IP_ADDRESS = "192.168.0.2"
PORT = "554"

MODE = str(0)
CHANNEL="1"
source=0
FPS = 15 if(MODE=="1") else 40
RESIZE = 1 if(MODE=="1") else 0.4
source=f"rtsp://admin:ragavan20@{IP_ADDRESS}:{PORT}/cam/realmonitor?channel={CHANNEL}&subtype={MODE}"

face = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

CAP = cv2.VideoCapture(source)
inpFrame = None
def frameSkipper(fps :int,sec:float)->None :
    #OpenCV implements buffer concept for cameras where frames from camera is storred and accessed
    #it is implemented in Queue datatype which is not ideal to always get the latest frame 
    #so through frame skipped we attempt to clear the queue of a few frames to get the latest frame
    global CAP,inpFrame
    while True :
        for i in range(int(fps*sec)):
            _,inpFrame=CAP.read()
            if(not _): # No frame received so calling camera checker
                #checkAndRepairCameraConnection()
                break
        else: 
            #IF Frames succefully skipped exit the loop
            break
    print("=")


for i in range(5*15):
    CAP.read()
delay=0.5
while CAP.isOpened():
    frameSkipper(FPS,delay*1.5)
    s = time.time()
    out = cv2.resize(
            cv2.cvtColor(inpFrame,cv2.COLOR_BGR2GRAY),
            (
                int(inpFrame.shape[1]*RESIZE),
                int(inpFrame.shape[0]*RESIZE)
            )
    )
    faces = face.detectMultiScale(out,1.1,4)
    for(x,y,w,h) in faces:
        cv2.rectangle(out,(x,y),(x+w,y+h),(255,0,0),2)
    cv2.imshow('Video',out)
    print("=")
    cv2.waitKey(2)
    delay = time.time()-s
