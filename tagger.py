import sys
import os
import numpy as np
import cv2
import time
import json
from pprint import pprint


face_cascade = cv2.CascadeClassifier('haars/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haars/haarcascade_eye_tree_eyeglasses.xml')
eye_pair_cascade = cv2.CascadeClassifier('haars/haarcascade_mcs_eyepair_big.xml')


def jsonfile(videofile):
    return os.path.basename(videofile) + '.json'


def save_json(videofile, timings):
    with open(jsonfile(videofile), 'w') as outfile:
        data = {'file': videofile, 'events': timings}
        json.dump(data, outfile)


def tag(videofile, PREVIEW=False, ratio=2, start=0):
    if os.path.exists(jsonfile(videofile)):
        return False

    print 'analyzing', videofile

    timings = []
    i = 0
    hit = False
    preveye = None
    prevframe = None
    eyeimg = None
    eyecoords = None

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

        faces = face_cascade.detectMultiScale(gray, 1.5, 3)
        eye_pairs = []
        eyes = []

        eye_diff_val = None 

        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            eye_pairs = eye_pair_cascade.detectMultiScale(roi_gray)

            if PREVIEW:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1)

                for (ex,ey,ew,eh) in eyes:
                    cv2.rectangle(img,(ex+x,ey+y),(x+ex+ew,y+ey+eh),(0,255,0),2)

                for (ex,ey,ew,eh) in eye_pairs[0:1]:
                    cv2.rectangle(img,(ex+x,ey+y),(x+ex+ew,y+ey+eh),(0,0,255),1)

        # if eyeimg is None and len(eye_pairs) > 0:
        if len(eye_pairs) > 0:
            ex, ey, ew, eh = eye_pairs[0]
            # eyeimg = frame[(ey+y)*ratio:(ey+y)*ratio+eh*ratio, (ex+x)*ratio:(ex+x)*ratio+ew*ratio]
            eyeimg = roi_gray[ey:ey+eh, ex:ex+ew]

            # if prevframe is not None and len(eye_pairs) > 0:
            # # if prevframe is not None and eyeimg is not None:
            #     ex, ey, ew, eh = eye_pairs[0]
            #     # ex, ey, ew, eh = eyecoords
            #     # diff = cv2.subtract(frame[y:y+h, x:x+w], prevframe[y:y+h, x:x+w])
            #     diff = cv2.absdiff(frame[(ey+y)*ratio:(ey+y)*ratio+eh*ratio, (ex+x)*ratio:(ex+x)*ratio+ew*ratio], prevframe[(ey+y)*ratio:(ey+y)*ratio+eh*ratio, (ex+x)*ratio:(ex+x)*ratio+ew*ratio])
            #     # diff = cv2.absdiff(eyeimg, prevframe[(ey+y)*ratio:(ey+y)*ratio+eh*ratio, (ex+x)*ratio:(ex+x)*ratio+ew*ratio])
            #     # diff = cv2.absdiff(gray[ey+y:ey+y+eh, ex+x:ex+x+ew], prevframe[ey+y:ey+y+eh, ex+x:ex+x+ew])
            #     # diff = cv2.absdiff(gray[ey:ey+eh, ex:ex+ew], prevframe[ey:ey+eh, ex:ex+ew])
            #     # if np.mean(diff) > 3.0:
            #     print np.mean(diff)
            #     if np.mean(diff) > 5.0:
            #         cv2.imshow('blink', img)
            #     cv2.imshow('diff', diff)


        if eyeimg is not None:
            w, h = eyeimg.shape[::-1]
            res = cv2.matchTemplate(gray, eyeimg, cv2.cv.CV_TM_SQDIFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            top_left = min_loc
            # top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(img,top_left, bottom_right, 255, 1)

            if preveye is not None:
                if preveye.shape != eyeimg.shape:
                    preveye = prevframe[top_left[1]:top_left[1]+h, top_left[0]:top_left[0]+w]
                diff = cv2.absdiff(eyeimg, preveye)

                eye_diff_val = np.mean(diff)

                if PREVIEW:
                    cv2.imshow('diff', diff)
                    if eye_diff_val > 8.5:
                        cv2.imshow('blink', img)

            preveye = gray[top_left[1]:top_left[1]+h, top_left[0]:top_left[0]+w]

        if PREVIEW:
            cv2.imshow('vid', img)

        i += 1

        obj = { "time": ms, 'frame': i, 'eye_pairs': [], 'eyes': [], 'faces': [], 'eyediff': eye_diff_val }

        for f in eye_pairs:
            obj['eye_pairs'].append([int(i*ratio) for i in f])

        for f in eyes:
            obj['eyes'].append([int(i*ratio) for i in f])

        for f in faces:
            obj['faces'].append([int(i*ratio) for i in f])

        timings.append(obj)

        prevframe = gray


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    save_json(videofile, timings)


if __name__ == '__main__':
    for f in sys.argv[1:]:
        tag(f)
