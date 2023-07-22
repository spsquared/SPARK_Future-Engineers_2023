from IO import io
from Util import server
import traceback
import numpy
import cv2
import math
import time

# converts images into data usable for SLAM and driving

# colors
rm = redMin = (0, 80, 75)
rM = redMax = (55, 255, 255)
gm = greenMin = (30, 80, 30)
gM = greenMax = (110, 255, 255)

# camera constants
imageWidth = 544
imageHeight = 308
focalLength = 170 # 100 for zoomed out image
focalLength = 63.4046735159
focalLength = 100
wallHeight = 10
cameraOffsetX = 3
cameraOffsetY = 10

# distortion constants
K = numpy.array([[181.20784053368962, 0.0, 269.26274741570063], [0.0, 180.34861809531762, 164.95661764906816], [0.0, 0.0, 1.0]])
D = numpy.array([[0.08869574884019396], [-0.06559255628891703], [0.07411420387674333], [-0.03169574352239552]])
D2 = D * -1

# code constants
X = 0
Y = 1
DISTANCE = 2
ANGLE = 3
LEFT = 0
RIGHT = 1

# create blob detectors
__params = cv2.SimpleBlobDetector_Params()
__params.filterByArea = True
__params.minArea = 65
__params.maxArea = 128941274721
__params.filterByCircularity = True
__params.minCircularity = 0.3
__params.filterByConvexity = True
__params.minConvexity = 0.7
# __params.filterByInertia = True
# __params.minInertiaRatio = 0
# __params.maxInertiaRatio = 1
blobDetector = cv2.SimpleBlobDetector_create(__params)
blobSizeConstant = 0.6

def filter(imgIn: numpy.ndarray):
    try:
        global redMax, redMin, greenMax, greenMin
        # convert to HSV
        hsv = cv2.cvtColor(imgIn, cv2.COLOR_BGR2HSV)
        # red filter
        # red is at 0 and also 180, accounting for HSV wraparound
        rMask1 = cv2.inRange(hsv, redMin, redMax)
        redMinList = list(redMin)
        redMinList = [180 - redMax[0], redMinList[1], redMinList[2]]
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
        edgesImg = cv2.Canny(blurredImg, lower, upper, 3)
        # combine images
        return [edgesImg, blurredG, blurredR]
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))

# remapping for distortion correction
undistortCrop = 150
K2 = K.copy()
K2[1][2] -= undistortCrop
new_K = K2.copy()
new_K[0][0] *= 0.5
new_K[1][1] *= 0.5
remap, remapInterpolation = cv2.fisheye.initUndistortRectifyMap(K2, D, numpy.eye(3), new_K, (imageWidth, imageHeight), cv2.CV_16SC2)
def undistort(imgIn: numpy.ndarray):
    return cv2.remap(imgIn[undistortCrop:], remap, remapInterpolation, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

# distance scanner
wallStartLeft = 164
wallStartRight = 154
undistortedWallStartLeft = 159
undistortedWallStartRight = 154
wallEnd = imageHeight
wallStartBuffer = 5
distanceTable = [[], []]
halfWidth = round(imageWidth / 2)
def generateDistanceTable():
    # generate the mesh of undistorted points using an ungodly long line of numpy
    newMatrixEstimation = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (imageWidth, imageHeight), numpy.eye(3), K, balance=1)
    leftHeightRange = wallEnd - wallStartLeft + 1
    rightHeightRange = wallEnd - wallStartRight + 1
    leftPoints = []
    rightPoints = []
    for imgx in range(imageWidth):
        for height in range(leftHeightRange):
            leftPoints.append((imgx, wallStartLeft + height))
        for height in range(rightHeightRange):
            rightPoints.append((imgx, wallStartRight + height))
    leftPoints = numpy.apply_along_axis(lambda p: p[0], 1, cv2.fisheye.undistortPoints(numpy.array([leftPoints], dtype=numpy.float32), K, D, None, newMatrixEstimation, K, criteria=(cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 500, 1e-6)))
    rightPoints = numpy.apply_along_axis(lambda p: p[0], 1, cv2.fisheye.undistortPoints(numpy.array([rightPoints], dtype=numpy.float32), K, D, None, newMatrixEstimation, K, criteria=(cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 500, 1e-6)))
    print(leftPoints)
    # pre-calculate locations for x and height of walls
    for imgx in range(imageWidth):
        distanceTable[LEFT].append([])
        distanceTable[RIGHT].append([])
        distanceTable[LEFT][imgx].append((-1, -1, -1, -1))
        leftTopIndex = imgx * leftHeightRange
        rightTopIndex = imgx * rightHeightRange
        for height in range(1, leftHeightRange):
            dist = wallHeight * math.sqrt((focalLength ** 2) + ((leftPoints[leftTopIndex][X] - halfWidth) ** 2)) / (leftPoints[leftTopIndex + height][Y] - undistortedWallStartLeft)
            angle = math.atan2(halfWidth - leftPoints[leftTopIndex][X], focalLength) + (math.pi * 2 / 3)
            x = -cameraOffsetX + math.cos(angle) * dist
            y = cameraOffsetY + math.sin(angle) * dist
            cDist = math.sqrt((x ** 2) + (y ** 2))
            cAngle = (math.atan2(y, x) + math.pi / 2) % (math.pi * 2) - math.pi
            distanceTable[LEFT][imgx].append((x, y, cDist, cAngle))
        distanceTable[RIGHT][imgx].append((-1, -1, -1, -1))
        for height in range(1, rightHeightRange):
            dist = wallHeight * math.sqrt((focalLength ** 2) + ((rightPoints[rightTopIndex][X] - halfWidth) ** 2)) / (rightPoints[rightTopIndex + height][Y] - undistortedWallStartRight)
            angle = math.atan2(halfWidth - rightPoints[rightTopIndex][X], focalLength) + (math.pi / 3)
            x = cameraOffsetX + math.sin(angle) * dist
            y = cameraOffsetY + math.cos(angle) * dist
            cDist = math.sqrt((x ** 2) + (y ** 2))
            cAngle = (math.atan2(y, x) + math.pi / 2) % (math.pi * 2) - math.pi
            distanceTable[RIGHT][imgx].append((x, y, cDist, cAngle))
    distanceTable[LEFT] = numpy.array(distanceTable[LEFT])
    distanceTable[RIGHT] = numpy.array(distanceTable[RIGHT])
# generateDistanceTable()

leftImgSinAngles = []
leftImgCosAngles = []
rightImgSinAngles = []
rightImgCosAngles = []
# leftImageWidthRemapX = remap[wallStartLeft][round(imageWidth / 2)][0]
# rightImageWidthRemapX = remap[wallStartRight][round(imageWidth / 2)][0]
for i in range(imageWidth):
    # leftRemapXI = remap[wallStartLeft][i][0]
    # rightRemapXI = remap[wallStartRight][i][0]
    leftImgSinAngles.append(math.sin(math.atan2(halfWidth - i, focalLength) + math.pi * 2 / 3))
    leftImgCosAngles.append(math.cos(math.atan2(halfWidth - i, focalLength) + math.pi * 2 / 3))
    rightImgSinAngles.append(math.sin(math.atan2(halfWidth - i, focalLength) + math.pi / 3))
    rightImgCosAngles.append(math.cos(math.atan2(halfWidth - i, focalLength) + math.pi / 3))
leftImgSinAngles = numpy.array(leftImgSinAngles)
leftImgCosAngles = numpy.array(leftImgCosAngles)
rightImgSinAngles = numpy.array(rightImgSinAngles)
rightImgCosAngles = numpy.array(rightImgCosAngles)

def getRawHeights(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    global wallHeight, wallStartLeft, wallStartRight, wallEnd
    
    # crop and then flip
    croppedLeft = numpy.swapaxes(leftEdgesIn[wallStartLeft - undistortCrop + wallStartBuffer:wallEnd], 0, 1)
    croppedRight = numpy.swapaxes(rightEdgesIn[wallStartRight - undistortCrop + wallStartBuffer:wallEnd], 0, 1)

    # find the bottom edge of the wall
    rawHeightsLeft = numpy.array(numpy.argmax(croppedLeft, axis=1), dtype="int") + wallStartBuffer
    rawHeightsRight = numpy.array(numpy.argmax(croppedRight, axis=1), dtype="int") + wallStartBuffer

    return [rawHeightsLeft, rawHeightsRight]
def mergeHeights(rawHeightsLeft: numpy.ndarray, rawHeightsRight: numpy.ndarray):
    return 'oof'
def getDistances(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    raise NotImplementedError()
    global distanceTable
    
    # crop and then flip
    croppedLeft = numpy.swapaxes(leftEdgesIn[wallStartLeft + wallStartBuffer:wallEnd], 0, 1)
    croppedRight = numpy.swapaxes(rightEdgesIn[wallStartRight + wallStartBuffer:wallEnd], 0, 1)

    # find the bottom edge of the wall
    rawHeightsLeft = numpy.array(numpy.argmax(croppedLeft, axis=1), dtype="float") + wallStartBuffer
    rawHeightsRight = numpy.array(numpy.argmax(croppedRight, axis=1), dtype="float") + wallStartBuffer

    # convert heights to coordinates
    leftCoordinates = numpy.apply_along_axis(lambda a: distanceTable[0][int(a[1])][int(a[0])], 1, numpy.stack((rawHeightsLeft, range(imageWidth)), 1))
    rightCoordinates = numpy.apply_along_axis(lambda a: distanceTable[1][int(a[1])][int(a[0])], 1, numpy.stack((rawHeightsRight, range(imageWidth)), 1))

    return [leftCoordinates, rightCoordinates]
def mergeDistances(leftCoordinates: numpy.ndarray, rightCoordinates: numpy.ndarray):
    # merge
    coordinates = numpy.concatenate((leftCoordinates, rightCoordinates))

    # sort coordinates by angle
    dtype = [('x', coordinates.dtype), ('y', coordinates.dtype), ('dist', coordinates.dtype), ('theta', coordinates.dtype)]
    ref = coordinates.ravel().view(dtype)
    ref.sort(order=['theta', 'dist', 'x', 'y'])

    return coordinates
def getDistance(imgx: int, height: int, dir: int):
    raise NotImplementedError()
    global distanceTable
    return distanceTable[max(dir, 0)][imgx][int(height)]
def getRawDistance(imgx: int, height: int, dir: int):
    if height == 0:
        return (-1.0, -1.0, -1.0, -1.0)
    else:
        dist = wallHeight * math.sqrt(focalLength**2 + (imgx - imageWidth / 2)**2) / height
        if dir == -1:
            x = -1 * cameraOffsetX + leftImgCosAngles[imgx] * dist
            y = cameraOffsetY + leftImgSinAngles[imgx] * dist
        else:
            x = cameraOffsetX + rightImgCosAngles[imgx] * dist
            y = cameraOffsetY + rightImgSinAngles[imgx] * dist
        return (x, y, math.sqrt(x**2 + y**2), math.atan2(y, x))

def getWalls(heights: numpy.ndarray, rBlobs: list, gBlobs: list, dir: int):
    for blob in rBlobs + gBlobs:
        for i in range(blob[0] - blob[1], blob[0] + blob[1] + 1):
            if i >= 0 and i < imageWidth:
                heights[i] = 0
    
    img = numpy.uint8(numpy.zeros((wallEnd - wallStartLeft, imageWidth)))
    
    indices = numpy.dstack((heights, range(imageWidth)))

    img[tuple(numpy.transpose(indices))] = 255
  
    # Apply HoughLinesP method to 
    # to directly obtain line end points
    lines = cv2.HoughLinesP(
                img, # Input edge image
                1, # Distance resolution in pixels
                numpy.pi/180, # Angle resolution in radians
                threshold=20, # Min number of votes for valid line
                minLineLength=5, # Min allowed length of line
                maxLineGap=50 # Max allowed gap between line for joining them
                )
    def lineSort(line):
        return line[0][0]
    lines.sort(key=lineSort)
    return lines

def mergeWalls(lines):
    mapLines = []
    lastPoint = [None]
    points = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if y1 == 0 or y2 == 0:
            continue
        if lastPoint[0] != None:
            mapLines.append(getRawDistance(x1, y1, dir).append(True), getRawDistance(x2, y2, dir).append(True))
            if abs(lastPoint[X] - x1) <= 2:
                if abs(lastPoint[Y] - y1) <= 2:
                    points.append(getRawDistance(lastPoint[X], lastPoint[Y], dir))
                else:
                    if lastPoint[Y] > y1:
                        points.append(getRawDistance(lastPoint[X], lastPoint[Y], dir))
                    else:
                        points.append(getRawDistance(x1, y1, dir))
        else:
            mapLines.append(getRawDistance(x1, y1, dir).append(False), getRawDistance(x2, y2, dir).append(True))
        lastPoint = [x2, y2]
    if len(mapLines) > 0:
        mapLines[len(mapLines) - 1][1][4] = False
    return [points, mapLines]

def getBlobs(rLeftIn: numpy.ndarray, gLeftIn: numpy.ndarray, rRightIn: numpy.ndarray, gRightIn: numpy.ndarray):
    global wallStartLeft, wallStartRight, wallEnd
    try:
        # add borders to fix blob detection
        # blobStart = 79
        # blobEnd = 100 # fix???
        rLeft = cv2.copyMakeBorder(rLeftIn[wallStartLeft:wallEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        gLeft = cv2.copyMakeBorder(gLeftIn[wallStartLeft:wallEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        rRight = cv2.copyMakeBorder(rRightIn[wallStartRight:wallEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        gRight = cv2.copyMakeBorder(gRightIn[wallStartRight:wallEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])

        blobDetector.empty()
        rLeftBlobs = processBlobs(blobDetector.detect(255 - rLeft))
        blobDetector.empty()
        gLeftBlobs = processBlobs(blobDetector.detect(255 - gLeft))
        blobDetector.empty()
        rRightBlobs = processBlobs(blobDetector.detect(255 - rRight))
        blobDetector.empty()
        gRightBlobs = processBlobs(blobDetector.detect(255 - gRight))

        return [rLeftBlobs, gLeftBlobs, rRightBlobs, gRightBlobs]

    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))

def processBlobs(blobs: list):
    newBlobs = []
    for blob in blobs:
        newBlobs.append([math.floor(blob.pt[0]), math.ceil(blob.size * blobSizeConstant)])
    
    return newBlobs

def mergeBlobs(leftBlobs: list, rightBlobs: list):
    # keep angle and distance instead of x and size
    return []

def setColors(data: list, sendServer: bool):
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
            array.append(greenMax[math.ceil((i - 1) / 3)])
    for i in range(6):
        if i % 2 == 0:
            array.append(redMin[math.ceil(i / 3)])
        else:
            array.append(greenMin[math.ceil((i - 1) / 3)])
    return array
def setDefaultColors():
    global rM, rm, gM, gm
    print('-- New ----------')
    print(rM, rm)
    print(gM, gm)
    return [rM[2], gM[2], rM[1], gM[1], rM[0], gM[0], rm[2], gm[2], rm[1], gm[1], rm[0], gm[0]]