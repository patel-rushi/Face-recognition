import cv2
import dlib
import os
import sys
import math
import time
import sqlite3
from PIL import Image                                                           # pillow
import openface

cam = cv2.VideoCapture(1)
detector = dlib.get_frontal_face_detector()
date = time.strftime("%d.%m.%Y")
path = './pics_taken/' + date
dlibFacePredictor = 'shape_predictor_68_face_landmarks.dat'                     # Path to dlib's face predictor
align = openface.AlignDlib(dlibFacePredictor)
if not os.path.exists(path):
    os.makedirs(path)

def getProfile(id):
    connect = sqlite3.connect("Face-DataBase")
    cmd = "SELECT * FROM Students WHERE ID=" + str(id)
    cursor = connect.execute(cmd)
    profile = None
    for row in cursor:
        profile = row
    connect.close()
    return profile

rec = cv2.face.LBPHFaceRecognizer_create()                                            # Local Binary Patterns Histograms
rec.read('./recognizer/trainingData.yml')                                       # loading the trained data

#font = cv2.InitFont(cv2.cv.CV_FONT_HERSHEY_PLAIN, 2, 1, 0, 1)                # the font of text on face recognition

# make an array of all the students in the database initialied as zero

picNum = 2
img = cv2.imread('test5.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                                    # conveting the camera input into GrayScale
dets = detector(img, 1)
# folderName = path + '/pic' + str(picNum)
# if not os.path.exists(folderName):
#     os.makedirs(folderName)
totalConf = 0.0
faceRec = 0
for i, d in enumerate(dets):
    # picName = str(i + 1) + '.jpg'
    # picFolderName = folderName + '/' + picName
    img2 = img[d.top():d.bottom(), d.left():d.right()]
    rgbImg = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    bb = align.getLargestFaceBoundingBox(rgbImg)
    alignedFace = align.align(96, rgbImg, bb=None, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    alignedFace = cv2.cvtColor(alignedFace, cv2.COLOR_BGR2GRAY)                 # conveting the camera input into GrayScale
    id, conf = rec.predict(alignedFace)    # Comparing from the trained data
    if conf < 50:
        totalConf += conf
        faceRec += 1
        profile = getProfile(id)
        if profile != None:
            cv2.cv.putText(img,profile[1] + str("(%.2f)" % conf),(d.left(), d.bottom()),font,(0, 0, 0))                                      # Writing the name of the face recognized
    else :
        cv2.putText(img,"Unknown" + str(conf),(d.left(), d.bottom()),cv2.FONT_HERSHEY_SIMPLEX,1,color=(255,0,0),thickness=2)                                                # Writing the name of the face recognized
    # cv2.imwrite(picFolderName, img[d.top():d.bottom(), d.left():d.right()])
    cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (255, 255, 255), 2)
cv2.imshow('frame', img)                                                     # Showing each frame on the window
cv2.imwrite(path + '/pic' + str(picNum) + '.jpg', img)
detectPrint = 'Frame' + str(picNum) + ". %d face detected" % len(dets)
if faceRec != 0:
    print(detectPrint + " and ", faceRec, " face recognized with confidence %.2f"%(totalConf / faceRec))
else:
    print(detectPrint + " and 0 faces recognized")
cam.release()
cv2.destroyAllWindows()                                                         # Closing all the opened windows
