from __future__ import division
import cv2
import numpy as np


protoFile = "hand/pose_deploy.prototxt"
weightsFile = "hand/pose_iter_102000.caffemodel"
POSE_PAIRS = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8], [0, 9], [9, 10], [10, 11], [11, 12],
              [0, 13], [13, 14], [14, 15], [15, 16], [0, 17], [17, 18], [18, 19], [19, 20]]


def hand_estimation_function(image):
    nPoints = 22
    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

    frame = cv2.imread(image)
    frameCopy = np.copy(frame)
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    aspect_ratio = frameWidth/frameHeight

    threshold = 0.1

    inHeight = 368
    inWidth = int(((aspect_ratio*inHeight)*8)//8)
    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight), (0, 0, 0), swapRB=False, crop=False)

    net.setInput(inpBlob)

    output = net.forward()

    points = []

    for i in range(nPoints):
        probMap = output[0, i, :, :]
        probMap = cv2.resize(probMap, (frameWidth, frameHeight))

        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

        if prob > threshold :
            cv2.circle(frameCopy, (int(point[0]), int(point[1])), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frameCopy, "{}".format(i), (int(point[0]), int(point[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

            points.append((int(point[0]), int(point[1])))
        else :
            points.append(None)
    return points


def draw_skeleton(points, frame):
    for pair in POSE_PAIRS:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            cv2.line(frame, points[partA], points[partB], (0, 255, 255), 2)
            cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.circle(frame, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)


def calculate_wrist(pointA, pointB):
    c = []
    a = list(pointA)
    b = list(pointB) 

    c.append(b[0])  #x
    c.append(a[1])  #y
    
    wrist = 2 * abs(a[0] - c[0])
    wrist = round(wrist / 10)

    return wrist


def calculate_best_weight(wrist, age, height):
    if wrist < 15:
        coeff = 0.9
    elif wrist > 17 and wrist >= 15:
        coeff = 1
    else:
        coeff = 1.1

    best_weight = height-100 + (age/10)*0.9*coeff

    return best_weight


def calculate_cal_man(best_weight, age, height):
    return 10 * best_weight + 6.25 * height - 5 * age + 5


def calculate_cal_woman(best_weight, age, height):
    return 10 * best_weight + 6.25 * height - 5 * age - 161



