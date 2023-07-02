from IO import io
import numpy
import cv2
import base64
import statistics
import math
import json

# preprocessing filter module with cv prediction

# colors
rm = redMin = (0, 95, 75)
rM = redMax = (25, 255, 255)
gm = greenMin = (30, 20, 30)
gM = greenMax = (110, 255, 255)

focalLength = 41.1573574682

# create blob detector
params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.minArea = 65
params.filterByCircularity = True
params.minCircularity = 0.3
params.filterByConvexity = True
params.minConvexity = 0.7
params.filterByInertia = True
params.minInertiaRatio = 0
blobs = cv2.SimpleBlobDetector_create(params)

def filter(imgIn: numpy.ndarray):
    global redMax, redMin, greenMax, greenMin
    try:
        # convert to HSV
        hsv = cv2.cvtColor(imgIn, cv2.COLOR_BGR2HSV)
        # red filter
        # red is at 0 and also 180, accounting for HSV wraparound
        rMask1 = cv2.inRange(hsv, redMin, redMax)
        redMaxH = redMax[0]
        redMinList = list(redMin)
        redMinList = [180 - redMaxH, redMinList[1], redMinList[2]]
        redMin2 = tuple(redMinList)
        redMaxList = list(redMax)
        redMaxList = [180, redMaxList[1], redMaxList[2]]
        redMax2 = tuple(redMaxList)
        rMask2 = cv2.inRange(hsv, redMin2, redMax2)
        rMask = cv2.bitwise_or(rMask1, rMask2)
        # green filter
        gMask = cv2.inRange(hsv, greenMin, greenMax)
        # blur images to remove noise
        blurredR = cv2.medianBlur(rMask, 5)
        blurredG = cv2.medianBlur(gMask, 5)
        gray_image = cv2.cvtColor(imgIn, cv2.COLOR_RGB2GRAY)
        blurredImg = cv2.GaussianBlur(gray_image, (3,3),0)
        # edge detection
        edgesImage = cv2.Canny(blurredImg, 50, 125, 3)
        # combine images
        return cv2.merge((edgesImage, blurredG, blurredR))
    except Exception as err:
        print(err)
        io.error()

def undistort(img: numpy.ndarray):
    return img
def getDistance(height: int):
    global focalLength
    if height == 0: return float('inf')
    return 10 * focalLength / height
def combine

def predict(leftImgIn: numpy.ndarray, rightImgIn: numpy.ndarray):
    try:
        # filter to colors and split
        edgesLeftImg, gLeftImg, rLeftImg = cv2.split(filter(leftImgIn, True))
        edgesRightImg, gRightImg, rRightImg = cv2.split(filter(rightImgIn, True))

        return "stop"
    except Exception as err:
        print(err)
        io.error()

def getBlobs(imgIn: numpy.ndarray):
    try:
        # filter to colors and split
        edgesImg, gImg, rImg = cv2.split(filter(imgIn, True))

        # crop for wall detection
        wallStart = 79
        wallEnd = 125
        croppedEdgesImg = numpy.concatenate((edgesImg[wallStart:wallEnd], numpy.full((2, 272), 1, dtype=int)), axis=0)

        # flip wall
        croppedEdgesImg = numpy.swapaxes(croppedEdgesImg, 0, 1)

        # get wall heights by finding the bottom edge of the wall
        wallHeights = (croppedEdgesImg!=0).argmax(axis=1)

        # get wall 

        # crop for blob detection
        blobStart = 79
        blobEnd = 100

        # add borders to fix blob detection
        rImg = cv2.copyMakeBorder(rImg[blobStart:blobEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        gImg = cv2.copyMakeBorder(gImg[blobStart:blobEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])

        # detect blobs
        blobs.empty()
        rBlobs = blobs.detect(255 - rImg)
        blobs.empty()
        gBlobs = blobs.detect(255 - gImg)
    except Exception as err:
        print(err)
        io.error()
        
def setColors(data, server = None):
    global redMax, redMin, greenMax, greenMin
    redMax = (int(data[0]), int(data[3]), int(data[6]))
    greenMax = (int(data[1]), int(data[4]), int(data[7]))
    redMin = (int(data[9]), int(data[12]), int(data[15]))
    greenMin = (int(data[10]), int(data[13]), int(data[16]))
    print('-- New ----------')
    print(redMax, redMin)
    print(greenMax, greenMin)
    if server != None:
        server.broadcast('colors', getColors())
def getColors():
    global redMax, redMin, greenMax, greenMin
    array = []
    for i in range(9):
        if i % 3 == 0:
            array.append(redMax[math.ceil(i/3)])
        elif i % 2 == 0:
            array.append(greenMax[math.floor(i/3)+1])
    for i in range(9):
        if i % 3 == 0:
            array.append(redMin[math.ceil(i/3)])
        elif i % 2 == 0:
            array.append(greenMin[math.floor(i/3)+1])
    return array
def setDefaultColors():
    global rM, rm, gM, gm
    print('-- New ----------')
    print(rM, rm)
    print(gM, gm)
    return [rM[2], gM[2], rM[1], gM[1], rM[0], gM[0], rm[2], gm[2], rm[1], gm[1], rm[0], gm[0]]