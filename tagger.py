import sys
import os
import numpy as np
import cv2
import time
import json
from pprint import pprint
import signal

videofile = sys.argv[1]
start = 0
if len(sys.argv) == 3:
    start = int(sys.argv[2])

PREVIEW = True
ratio = 1
timings = []
i = 0

face_cascade = cv2.CascadeClassifier('haars/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haars/haarcascade_eye_tree_eyeglasses.xml')
eye_pair_cascade = cv2.CascadeClassifier('haars/haarcascade_mcs_eyepair_big.xml')


def save_json(signal, frame):
    with open(os.path.basename(videofile) + '_' + str(time.time()) + '.json', 'w') as outfile:
        data = {'file': videofile, 'events': timings}
        json.dump(data, outfile)

    sys.exit(0)


signal.signal(signal.SIGINT, save_json)


vidcap = cv2.VideoCapture(videofile)
success,image = vidcap.read()

while success:
    ret, frame = vidcap.read()
    if type(frame) is type(None):
        break

    ms = vidcap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
    if ms < start:
        continue

    newx, newy = frame.shape[1]/ratio, frame.shape[0]/ratio
    img = cv2.resize(frame,(newx, newy))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    eye_pairs = []
    eyes = []

    for (x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(roi_gray)
        eye_pairs = eye_pair_cascade.detectMultiScale(roi_gray)

        if PREVIEW:
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(img,(ex+x,ey+y),(x+ex+ew,y+ey+eh),(0,255,0),2)

            for (ex,ey,ew,eh) in eye_pairs[0:1]:
                cv2.rectangle(img,(ex+x,ey+y),(x+ex+ew,y+ey+eh),(0,0,255),1)

    if PREVIEW:
        cv2.imshow('img',img)

    i += 1

    obj = { "time": ms, 'frame': i, 'eye_pairs': [], 'eyes': [], 'faces': [] }

    for f in eye_pairs:
        obj['eye_pairs'].append([int(i*ratio) for i in f])

    for f in eyes:
        obj['eyes'].append([int(i*ratio) for i in f])

    for f in faces:
        obj['faces'].append([int(i*ratio) for i in f])

    timings.append(obj)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


save_json('','')
