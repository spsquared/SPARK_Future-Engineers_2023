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


def predict(leftImgIn: numpy.ndarray, rightImgIn: numpy.ndarray):
    try:
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

        # filter to colors and split
        edgesLeftImg, gLeftImg, rLeftImg = cv2.split(filter(leftImgIn, True))
        edgesRightImg, gRightImg, rRightImg = cv2.split(filter(rightImgIn, True))

        # crop for wall detection
        wallStart = 79
        wallEnd = 125
        croppedEdgesImg = numpy.concatenate((edgesLeftImg[wallStart:wallEnd], numpy.full((2, 272), 1, dtype=int)), axis=0)

        # flip wall
        croppedEdgesImg = numpy.swapaxes(croppedEdgesImg, 0, 1)

        # get wall heights by finding the bottom edge of the wall
        wallHeightsAll = (croppedEdgesImg!=0).argmax(axis=1)
    except Exception as err:
        print(err)
        io.error()

