from IO import io
from Util import server
from Controller import slam
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
imageWidth = 544
imageHeight = 308
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
# params.filterByInertia = True
# params.minInertiaRatio = 0
# params.maxInertiaRatio = 1
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
        grayImage = cv2.cvtColor(imgIn, cv2.COLOR_RGB2GRAY)
        blurredImg = cv2.GaussianBlur(grayImage, (3, 3), 0)
        # edge detection
        lower = 50
        upper = 125
        edgesImage = cv2.Canny(blurredImg, lower, upper, 3)
        # combine images
        # return [grayImage, blurredR, blurredG]
        return cv2.merge((edgesImage, blurredG, blurredR))
    except Exception as err:
        io.error()
        print(err)

# distance scanner
leftImgSinAngles = []
leftImgCosAngles = []
rightImgSinAngles = []
rightImgCosAngles = []
for i in range(imageWidth):
    leftImgSinAngles.append(math.sin(math.atan2((imageWidth / 2) - i, focalLength) + math.pi * 2 / 3))
    leftImgCosAngles.append(math.cos(math.atan2((imageWidth / 2) - i, focalLength) + math.pi * 2 / 3))
    rightImgSinAngles.append(math.sin(math.atan2((imageWidth / 2) - i, focalLength) + math.pi / 3))
    rightImgCosAngles.append(math.cos(math.atan2((imageWidth / 2) - i, focalLength) + math.pi / 3))
leftImgSinAngles = numpy.array(leftImgSinAngles)
leftImgCosAngles = numpy.array(leftImgCosAngles)
rightImgSinAngles = numpy.array(rightImgSinAngles)
rightImgCosAngles = numpy.array(rightImgCosAngles)
def getDistances(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    global focalLength, wallHeight, imgSinAngles, imgCosAngles

    # crop for wall detection, then flip
    wallStart = 79
    wallEnd = 125
    croppedLeft = numpy.swapaxes(numpy.concatenate((leftEdgesIn[wallStart:wallEnd], numpy.full((2, imageWidth), 1, dtype=int)), axis=0), 0, 1)
    croppedRight = numpy.swapaxes(numpy.concatenate((rightEdgesIn[wallStart:wallEnd], numpy.full((2, imageWidth), 1, dtype=int)), axis=0), 0, 1)

    # get wall heights by finding the bottom edge of the wall
    rawHeightsLeft = (croppedLeft != 0).argmax(axis=1)
    rawHeightsRight = (croppedRight != 0).argmax(axis=1)
    
    def rawToCartesian(a, dir):
        if a[0] == 0:
            dist = 10000
        else:
            dist = wallHeight * focalLength / a[0]
        x = dir * (cameraOffsetX) + a[2] * dist
        y = (cameraOffsetY) + a[1] * dist
        # focal length fix for non-cylindrical projection
        # dist = wallHeight * math.sqrt(focalLength**2 + (xcoordinate - center)**2) / a[0]
        # return (dir * (3 + a[1] * dist), (10 + a[2] * dist), dist)
        return (x, y, dist, math.atan2(y, x))

    leftCoordinates = numpy.apply_along_axis(rawToCartesian, 1, numpy.stack((rawHeightsLeft, leftImgSinAngles, leftImgCosAngles), -1), -1)
    rightCoordinates = numpy.apply_along_axis(rawToCartesian, 1, numpy.stack((rawHeightsRight, rightImgSinAngles, rightImgCosAngles), -1), 1)

    coordinates = numpy.concatenate((leftCoordinates, rightCoordinates))

    dtype = [('x', coordinates.dtype), ('y', coordinates.dtype), ('dist', coordinates.dtype), ('theta', coordinates.dtype)]
    ref = coordinates.ravel().view(dtype)
    ref.sort(order=['theta', 'dist', 'x', 'y'])

    return [ref, croppedLeft, rawHeightsLeft]
    
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

        return [numpy.concatenate((rLeftBlobs, rRightBlobs), axis=None), numpy.concatenate((gLeftBlobs, gRightBlobs), axis=None)]
        # return [numpy.concatenate(numpy.array(rLeftBlobs), numpy.array(rRightBlobs)), numpy.concatenate(numpy.array(gLeftBlobs), numpy.array(gRightBlobs))]

    except Exception as err:
        io.error()
        print(err)

def processBlobs(blobs):
    newBlobs = []
    for blob in blobs:
        newBlobs.append(blob.pt[0])
        # newBlobs.append([0, 0])
    
    return newBlobs

def getLandmarks(distances, rBlobs, gBlobs):
    outerWallLandmarks = []
    innerWallLandmarks = []
    rBlobLandmarks = []
    gBlobLandmarks = []
    # x, y, distance, angle
    # all relative to car center

    # get outer and inner walls
    last = [None]
    angleAverage = None
    for point in list(distances):
        if last[0] != None:
            slope = (point[2] - last[2]) / (point[3] - last[3])
            angle = math.atan2(slope, 1)
            if angleAverage == None:
                angleAverage = angle
            else:
                if point[2] - last[2] > 20:
                    innerWallLandmarks.append(last)
                    angleAverage = None
                else:
                    angleDifference = angle - angleAverage
                    if slam.carDirection == slam.CLOCKWISE:
                        if angleDifference < -math.pi / 4:
                            outerWallLandmarks.append(last)
                    else:
                        if angleDifference > math.pi / 4:
                            outerWallLandmarks.append(last)
                    angleAverage = angle / 2 + angleAverage / 2
        last = point
    
    # get distance info for blobs
    for blob in rBlobs:
        rBlobLandmarks.append(distances[blob[0]])
    for blob in gBlobs:
        gBlobLandmarks.append(distances[blob[0]])

    return [outerWallLandmarks, innerWallLandmarks, rBlobLandmarks, gBlobLandmarks]

def setColors(data, sendServer: bool):
    global redMax, redMin, greenMax, greenMin
    redMax = (int(data[0]), int(data[2]), int(data[4]))
    greenMax = (int(data[1]), int(data[3]), int(data[5]))
    redMin = (int(data[6]), int(data[8]), int(data[10]))
    greenMin = (int(data[7]), int(data[9]), int(data[11]))
    print('-- New ----------')
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