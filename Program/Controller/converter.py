from IO import io
from Util import server
import numpy
import cv2
import math

# converts images into data usable for SLAM and driving

# colors
rm = redMin = (0, 95, 75)
rM = redMax = (25, 255, 255)
gm = greenMin = (30, 20, 30)
gM = greenMax = (110, 255, 255)

# other constants
horizontalFov = 155
verticalFov = 115
imageWidth = 272
imageHeight = 154
focalLength = ((imageHeight / 2) / math.tan(math.pi * (verticalFov / 2) / 180))
wallHeight = 10
centerOffset = 10
cameraOffsetX = 3
cameraOffsetY = 10

# create blob detectors
params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.minArea = 65
params.filterByCircularity = True
params.minCircularity = 0.3
params.filterByConvexity = True
params.minConvexity = 0.7
params.filterByInertia = True
params.minInertiaRatio = 0
blobDetector = cv2.SimpleBlobDetector_create(params)

def filter(imgIn: numpy.ndarray):
    try:
        global redMax, redMin, greenMax, greenMin
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
        blurredImg = cv2.GaussianBlur(gray_image, (3, 3), 0)
        # edge detection
        edgesImage = cv2.Canny(blurredImg, 50, 125, 3)
        # combine images
        return cv2.merge((edgesImage, blurredG, blurredR))
    except Exception as err:
        io.error()
        print(err)

# distance scanner
imgSinAngles = []
imgCosAngles = []
for i in range(imageWidth):
    imgSinAngles.append(math.sin(60 - math.atan2((imageWidth / 2) - i, focalLength)))
    imgCosAngles.append(math.cos(60 - math.atan2((imageWidth / 2) - i, focalLength)))
imgSinAngles = numpy.array(imgSinAngles)
imgCosAngles = numpy.array(imgCosAngles)
def getDistances(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    global focalLength, wallHeight, imgAngles

    # crop for wall detection, then flip
    wallStart = 79
    wallEnd = 125
    croppedLeft = numpy.swapaxes(numpy.concatenate((leftEdgesIn[wallStart:wallEnd], numpy.full((2, imageWidth), 1, dtype=int)), axis=0), 0, 1)
    croppedRight = numpy.swapaxes(numpy.concatenate((rightEdgesIn[wallStart:wallEnd], numpy.full((2, imageWidth), 1, dtype=int)), axis=0), 0, 1)

    # get wall heights by finding the bottom edge of the wall
    rawHeightsLeft = (croppedLeft != 0).argmax(axis=1)
    rawHeightsRight = (croppedRight != 0).argmax(axis=1)

    def rawToCartesian(a, dir):
        #need   focal length  fix
        # dist = wallHeight * math.sqrt(focalLength**2 + (xcoordinate - center)**2) / a[0]
        # return (dir * (3 + a[1] * dist), (10 + a[2] * dist), dist)
        dist = wallHeight * focalLength / a[0]
        return (dir * (cameraOffsetX + a[1] * dist), (cameraOffsetY + a[2] * dist), dist)

    leftCoordinates = numpy.apply_along_axis(rawToCartesian, 1, numpy.stack((rawHeightsLeft, imgSinAngles, imgCosAngles)), -1)
    rightCoordinates = numpy.apply_along_axis(rawToCartesian, 1, numpy.stack((rawHeightsRight, imgSinAngles, imgCosAngles)), 1)

    return numpy.concatenate((leftCoordinates, rightCoordinates))
    
def getBlobs(rLeftIn: numpy.ndarray, gLeftIn: numpy.ndarray, rRightIn: numpy.ndarray, gRightIn: numpy.ndarray):
    try:
        # add borders to fix blob detection
        blobStart = 79
        blobEnd = 100 # fix???
        rLeft = cv2.copyMakeBorder(rLeftIn[blobStart:blobEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        gLeft = cv2.copyMakeBorder(gLeftIn[blobStart:blobEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        rRight = cv2.copyMakeBorder(rRightIn[blobStart:blobEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        gRight = cv2.copyMakeBorder(gRightIn[blobStart:blobEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])

        blobDetector.empty()
        rLeftBlobs = processBlobs(blobDetector.detect(255 - rLeft))
        blobDetector.empty()
        gLeftBlobs = processBlobs(blobDetector.detect(255 - gLeft))
        blobDetector.empty()
        rRightBlobs = processBlobs(blobDetector.detect(255 - rRight))
        blobDetector.empty()
        gRightBlobs = processBlobs(blobDetector.detect(255 - gRight))
    except Exception as err:
        io.error()
        print(err)

def processBlobs(blobs):
    for i in range(len(blobs)):
        blobs[i] = blobs[i].pt[0]
    
    return blobs

def getLandmarks(idk):
    return False

def setColors(data, sendServer: bool = False):
    global redMax, redMin, greenMax, greenMin
    redMax = (int(data[0]), int(data[2]), int(data[4]))
    greenMax = (int(data[1]), int(data[3]), int(data[5]))
    redMin = (int(data[6]), int(data[8]), int(data[10]))
    greenMin = (int(data[7]), int(data[9]), int(data[11]))
    print('-- New ​----------')
    print(redMax, redMin)
    print(greenMax, greenMin)
    if sendServer:
        server.emit('colors', getColors())
def getColors():
    global redMax, redMin, greenMax, greenMin
    array = []
    for i in range(6):
        if i % 2 == 0:
            array.append(redMax[math.ceil(i / 3)])
        else:
            array.append(greenMax[math.floor(i / 3) + 1])
    for i in range(6):
        if i % 2 == 0:
            array.append(redMin[math.ceil(i / 3)])
        else:
            array.append(greenMin[math.floor(i / 3) + 1])
    return array
def setDefaultColors():
    global rM, rm, gM, gm
    print('-- New ----------')
    print(rM, rm)
    print(gM, gm)
    return [rM[2], gM[2], rM[1], gM[1], rM[0], gM[0], rm[2], gm[2], rm[1], gm[1], rm[0], gm[0]]