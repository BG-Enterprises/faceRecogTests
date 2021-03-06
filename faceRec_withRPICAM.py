from socket import *
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import face_recognition
import cv2
import numpy as np
import os
from datetime import datetime
import traceback
import dlib
print("Starting")
# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
#video_capture = cv2.VideoCapture(0)
 
detector = dlib.get_frontal_face_detector()
faceImages = [
    "/home/pi/faceRecog/BG_APPA/1.jpeg",
    "/home/pi/faceRecog/BG_DM/1.jpeg",
    "/home/pi/faceRecog/BG_PGR/1.jpeg"
]

faceNames = [
    "GANAPATHY",
    "MURTHY",
    "RAGAVANDIR"
]

faceEncodings =[]
print("Compiling faces")
for i in faceImages :
    temp = face_recognition.load_image_file(i)
    faceEncodings.append(face_recognition.face_encodings(temp)[0])

# Create arrays of known face encodings and their names
known_face_encodings = faceEncodings
known_face_names = faceNames

IP_ADDRESS = "192.168.0.2"
PORT = "554"

MODE = str(-1)
faceCascade = cv2.CascadeClassifier('/home/pi/faceRecog/haarcascade_frontalface_default.xml')

def resizeFramePropotionally(frame,fraction):
    global MODE
    if (MODE=="1"):
        return frame.copy()
    else:
        return cv2.resize(
            frame,
            (
                int(frame.shape[1]*fraction),
                int(frame.shape[0]*fraction)
            )
        )

def giveNewName():
    path = "/home/pi/Desktop/FShots/"
    return path+str(datetime.now()).split(".")[0].replace(" ","_")+".jpg"

print("Accessing Camera")
inpFrame = None
"""
CAP  = cv2.VideoCapture(source)
COMPRESSION = 0.27
FPS = 15 if(MODE=="1" or MODE=="-1" ) else 40
"""
firstFrame = None 
initialized = False
fileOUT = open("/home/pi/Desktop/errorLogs","a+")
fileOUT.write("\n\n"+"="*20+giveNewName())

def checkAndRepairCameraConnection():
    global CAP,IP_ADDRESS,PORT

    CAMERA_CONNECTED = True
    s = socket(AF_INET,SOCK_STREAM)
    while(s.connect_ex((IP_ADDRESS,int(PORT)))!=0):
        CAMERA_CONNECTED = False
        print("Camera Not Available , waiting for camera ",CAP.isOpened())
        time.sleep(0.5)

    if(not(CAMERA_CONNECTED)): #If camera got disconnected in and reconnected
       CAP = cv2.VideoCapture(source)
    else:
        time.sleep(0.5) # Some times the error will be cause only due to the buffer getting empty , so just waits for 0.5 secs


def frameSkipper(fps :int,sec:float)->None :
    #OpenCV implements buffer concept for cameras where frames from camera is storred and accessed
    #it is implemented in Queue datatype which is not ideal to always get the latest frame 
    #so through frame skipped we attempt to clear the queue of a few frames to get the latest frame
    global CAP,inpFrame,stopped
    jump = fps*sec if(MODE=="-1") else fps*sec//2
    while True :
        for i in range(int(jump)):
            _,inpFrame=CAP.read()
            if(not _): # No frame received so calling camera checker
                checkAndRepairCameraConnection()
                break
        else: 
            #IF Frames succefully skipped exit the loop
            break
    print("=")

def getFaceLocations(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    #face_rects = detector(gray,0)
    faces = faceCascade.detectMultiScale(gray, 1.1, 4)

    out = []
    """
    for i,d in enumerate(face_rects):
        out.append(
                (d.top(),d.right(),d.bottom(),d.left())
                )
    """
    
    for(x,y,w,h) in faces :
        out.append(
                (y,x+w,y+h,x)
        )
    
    return out

#
# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

#frameSkipper(FPS,3)
diff = 1.5

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
COMPRESSION = 0.99

saveCurrentFrame = False
try:
  for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    inpFrame = frame.array
    #print("In Here")
    # Grab a single frame of video
    #frameSkipper(FPS,diff*1.5)
    frame = resizeFramePropotionally(inpFrame,COMPRESSION)
    rawCapture.truncate(0)
    #ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = frame

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    s = time.time()
    if True :
    #if process_this_frame:
        print("Running Recognition")
        # Find all the faces and face encodings in the current frame of video
        #face_locations = face_recognition.face_locations(rgb_small_frame)
        face_locations = getFaceLocations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        saveCurrentFrame = False
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                saveCurrentFrame = True
            print(name)
            face_names.append(name)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        #top *= 4
        #right *= 4
        #bottom *= 4
        #left *= 4
        left=int(left-20)
        top=int(top-30)
        bottom=int(bottom+30)
        right=int(right+20)

        # Draw a box around the face
        corner1 =(left,top)
        corner2 =(right,bottom)
        if name=="Unknown" :
            color = (0,0,255)
        else:
            color = (0,128,0) 
        cv2.rectangle(frame, corner1,corner2, 0.5)

        # Draw a label with a name below the face
        
        cv2.rectangle(frame, (left, bottom-20), (right, bottom+20),color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.35, (255, 255, 255), 1)
        cv2.putText(frame,str(datetime.now().date()),(left+6,bottom+14),font,0.35,(255,255,255),1)
    # Display the resulting image
    if(face_names!=[] and saveCurrentFrame): 
        cv2.imwrite(giveNewName(),frame)
    cv2.imshow('Video', frame)
    diff = time.time()-s
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
except Exception as e :
    exc = e
    traceBack = traceback.format_exception(etype=type(exc),value=exc,tb=exc.__traceback__)
    fileOUT.write("\n".join(traceBack))
    fileOUT.flush()
# Release handle to the webcam
#video_capture.release()
cv2.destroyAllWindows()
