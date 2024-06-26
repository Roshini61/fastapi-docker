import cv2
import os
import face_recognition
import pickle


import sys
import face_recognition_models

print("Python Interpreter Path:", sys.executable)
print("face_recognition_models Path:", face_recognition_models.__file__)

folderModePath = 'Images'
modePathList = os.listdir(folderModePath)
imgList = []
studentIds=[]
for path in modePathList:
    imgList.append(cv2.imread(os.path.join(folderModePath, path)))
    studentIds.append(os.path.splitext(path)[0])

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")