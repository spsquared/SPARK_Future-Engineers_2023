from IO import io
from Util import server
import traceback
import numpy
import cv2
import math

# converts images into data usable for SLAM and driving

# colors
rm = redMin = (0, 90, 70)
rM = redMax = (20, 255, 255)
gm = greenMin = (50, 50, 50)
gM = greenMax = (105, 255, 255)

# camera constants
imageWidth = 544
imageHeight = 308
focalLength = 100
focalLength = 80
focalLength = 105
wallHeightOffset = 3
wallHeight = 9
cameraOffsetX = 3
cameraOffsetY = 10

# distortion constants
K = numpy.array([[181.20784053368962, 0.0, 269.26274741570063], [0.0, 180.34861809531762, 164.95661764906816], [0.0, 0.0, 1.0]])
D = numpy.array([[0.08869574884019396], [-0.06559255628891703], [0.07411420387674333], [-0.03169574352239552]])

# code constants
X = 0
Y = 1
DISTANCE = 2
ANGLE = 3
LEFT = 0
RIGHT = 1

# contour constants
contourSizeConstant = 0.6

minContourSize = 90
minContourSize = 0

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
        lower = 30
        upper = 90
        edgesImg = cv2.Canny(blurredImg, lower, upper, 3)
        # combine images
        return [edgesImg, blurredG, blurredR]
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))

# remapping for distortion correction
undistortCrop = 140
K2 = K.copy()
K2[1][2] -= undistortCrop
new_K = K2.copy()
new_K[0][0] *= 0.5
new_K[1][1] *= 0.5
remapX, remapY = cv2.fisheye.initUndistortRectifyMap(K2, D, numpy.eye(3), new_K, (imageWidth, imageHeight), cv2.CV_16SC2)
def undistort(imgIn: numpy.ndarray):
    return cv2.remap(imgIn[undistortCrop:], remapX, remapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

# distance scanner
wallStartLeft = 164
wallStartRight = 154
# undistortedWallStartLeft = [176, 174, 172, 169, 167, 165, 164, 164]
# undistortedWallStartRight = [158, 158, 159, 159, 159, 159, 159, 159]
undistortedWallStartLeft = [35, 33, 30, 29, 28, 27, 27, 27]
undistortedWallStartRight = [17, 19, 19, 20, 20, 20, 19, 18]

for i in range(8):
    undistortedWallStartLeft[i] += undistortCrop
    undistortedWallStartRight[i] += undistortCrop

maximumTopWallHeightLeft = 4 - 1
maximumTopWallHeightRight = 4 - 1

wallEnd = imageHeight + undistortCrop
contourStart = 160
distanceTable = [[], []]
halfWidth = int(imageWidth / 2)
quarterWidth = int(imageWidth / 4)
eighthWidth = int(imageWidth / 8)
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

cropEndArray = numpy.empty((imageWidth, 1))
cropEndArray[:] = 255
halfCropEndArray = numpy.empty((halfWidth, 1))
halfCropEndArray[:] = 255
quarterCropEndArray = numpy.empty((quarterWidth, 1))
quarterCropEndArray[:] = 255
eighthCropEndArray = numpy.empty((eighthWidth, 1))
eighthCropEndArray[:] = 255
def getRawHeights(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    global wallHeight, undistortedWallStartLeft, undistortedWallStartRight, wallEnd, eighthWidth, halfWidth, maximumTopWallHeightLeft, maximumTopWallHeightRight, eighthCropEndArray
    
    # crop and then flip

    # left camera is tilted, so 3 different start values are used for different x positions

    rawHeightsLeft = []
    wallStartsLeft = []

    for i in range(8):
        top = numpy.array(numpy.argmax(numpy.hstack((numpy.swapaxes(numpy.flip(leftEdgesIn[undistortedWallStartLeft[i] - undistortCrop - maximumTopWallHeightLeft:undistortedWallStartLeft[i] - undistortCrop,eighthWidth * i:eighthWidth * (i + 1)],0), 0, 1),eighthCropEndArray)), axis=1), dtype="int")
        rawHeightsLeft = numpy.append(rawHeightsLeft, numpy.array(numpy.argmax(numpy.hstack((numpy.swapaxes(leftEdgesIn[undistortedWallStartLeft[i] - undistortCrop:wallEnd - undistortCrop,eighthWidth * i:eighthWidth * (i + 1)], 0, 1),eighthCropEndArray)), axis=1), dtype="int") + top)
        wallStartsLeft = numpy.append(wallStartsLeft, undistortedWallStartLeft[i] - undistortCrop - top)

    rawHeightsRight = []
    wallStartsRight = []

    for i in range(8):
        top = numpy.array(numpy.argmax(numpy.hstack((numpy.swapaxes(numpy.flip(rightEdgesIn[undistortedWallStartRight[i] - undistortCrop - maximumTopWallHeightRight:undistortedWallStartRight[i] - undistortCrop,eighthWidth * i:eighthWidth * (i + 1)],0), 0, 1),eighthCropEndArray)), axis=1), dtype="int")
        rawHeightsRight = numpy.append(rawHeightsRight, numpy.array(numpy.argmax(numpy.hstack((numpy.swapaxes(rightEdgesIn[undistortedWallStartRight[i] - undistortCrop:wallEnd - undistortCrop,eighthWidth * i:eighthWidth * (i + 1)], 0, 1),eighthCropEndArray)), axis=1), dtype="int") + top)
        wallStartsRight = numpy.append(wallStartsRight, undistortedWallStartRight[i] - undistortCrop - top)


    return [numpy.array(rawHeightsLeft,dtype="int") + 1, numpy.array(rawHeightsRight,dtype="int") + 1, wallStartsLeft, wallStartsRight]
def getRawDistance(imgx: int, height: int, dir: int):
    if height == 0:
        return [-1.0, -1.0, -1.0, -1.0]
    else:
        dist = wallHeight * math.sqrt(focalLength**2 + (imgx - imageWidth / 2)**2) / height
        if dir == -1:
            x = -1 * cameraOffsetX + leftImgCosAngles[imgx] * dist
            y = cameraOffsetY + leftImgSinAngles[imgx] * dist
        else:
            x = cameraOffsetX + rightImgCosAngles[imgx] * dist
            y = cameraOffsetY + rightImgSinAngles[imgx] * dist
        return [x, y, math.sqrt(x**2 + y**2), math.atan2(y, x)]

def getWalls(heights: numpy.ndarray, rContours: list, gContours: list):
    for contour in rContours + gContours:
        for i in range(contour[0] - contour[1], contour[0] + contour[1] + 1):
            if i >= 0 and i < imageWidth:
                heights[i] = 0
    
    img = numpy.zeros((wallEnd - undistortCrop + 1, imageWidth), dtype="uint8")
    
    indices = numpy.dstack((heights, numpy.arange(imageWidth)))
    img[tuple(numpy.transpose(indices))] = 255

    # Apply HoughLinesP method to 
    # to directly obtain line end points
    lines = cv2.HoughLinesP(
                img, # Input edge image
                1, # Distance resolution in pixels
                numpy.pi/180, # Angle resolution in radians
                threshold=70, # Min number of votes for valid line
                minLineLength=10, # Min allowed length of line
                maxLineGap=4 # Max allowed gap between line for joining them
                )
    if lines is not None:
        lines = list(lines)
    else:
        lines = []

    def lineSort(line):
        return line[0][0]
    lines.sort(key=lineSort)
    newLines = []
    lastLine = [None]
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if y1 == 0 or y2 == 0:
            continue
        if lastLine[0] != None:
            lastSlope = (lastLine[3] - lastLine[1]) / (lastLine[2] - lastLine[0])
            slope = (y2 - y1) / (x2 - x1)
            newY = lastLine[3] + (x1 - lastLine[2]) * lastSlope
            if abs(x1 - lastLine[2]) < 100 and abs(y1 - newY) < 5 and abs(math.atan2(slope, 1) - math.atan2(lastSlope, 1)) < math.pi / 50:
                newLines[len(newLines) - 1] = [newLines[len(newLines) - 1][0], newLines[len(newLines) - 1][1], x2, y2]
                lastLine = line[0]
                continue
        lastLine = line[0]
        newLines.append([x1, y1, x2, y2])
    return newLines

def processWall(lines, dir):
    walls = []
    corners = []
    lastCorner = [None]
    for line in lines:
        x1, y1, x2, y2 = line
        if y1 > y2 and y2 < 5:
            corner1 = getRawDistance(x1, y1, dir)
            corner2 = getRawDistance(int((x1 + x2) / 2), int((y1 + y2) / 2), dir)
        elif y2 > y1 and y1 < 5:
            corner1 = getRawDistance(int((x1 + x2) / 2), int((y1 + y2) / 2), dir)
            corner2 = getRawDistance(x2, y2, dir)
        else:
            corner1 = getRawDistance(x1, y1, dir)
            corner2 = getRawDistance(x2, y2, dir)
        if math.sqrt((corner1[0] - corner2[0])**2 + (corner1[1] - corner2[1])**2) > 200:
            continue
        if math.sqrt((corner1[0])**2 + (corner1[1])**2) > 190 and math.sqrt((corner2[0])**2 + (corner2[1])**2) > 190:
            continue
        walls.append([corner1, corner2])
        walls[len(walls) - 1][0].append(True)
        walls[len(walls) - 1][1].append(True)
        if lastCorner[0] != None:
            if abs(lastCorner[X] - x1) <= 2:
                if abs(lastCorner[Y] - y1) <= 2:
                    corners.append(getRawDistance(lastCorner[X], lastCorner[Y], dir))
                else:
                    if lastCorner[Y] > y1:
                        corners.append(getRawDistance(lastCorner[X], lastCorner[Y], dir))
                    else:
                        corners.append(corner1)
        lastCorner = [x2, y2]
    if len(walls) > 0:
        walls[0][0][4] = False
        walls[len(walls) - 1][1][4] = False
    return [corners, walls]
def processWalls(leftLines, rightLines):
    leftCorners, leftWalls = processWall(leftLines, -1)
    rightCorners, rightWalls = processWall(rightLines, 1)
    return [leftCorners + rightCorners, leftWalls + rightWalls]

def getContours(imgIn: numpy.ndarray):
    edges = cv2.Canny(cv2.medianBlur(cv2.copyMakeBorder(imgIn[contourStart - undistortCrop:], 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=0), 3), 30, 200)

    contours, hierarchy = cv2.findContours(edges, 
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    processedContours = []
    for contour in contours:
        size = cv2.contourArea(contour)
        if size > minContourSize:
            moment = cv2.moments(contour)
            x = int(moment["m10"] / moment["m00"])
            y = int(moment["m01"] / moment["m00"])
            # if y > 9:
            width = math.ceil(math.sqrt(size) * contourSizeConstant)
            processedContours.append([x, width])
    return processedContours

def mergeContours(leftContours: list, rightContours: list, leftHeights: numpy.ndarray, rightHeights: numpy.ndarray):
    contours = []
    for contour in leftContours:
        if contour[0] == imageWidth:
            contour[0] -= 1
        if contour[1] * 4 > leftHeights[contour[0]]:
            contours.append(getRawDistance(contour[0], leftHeights[contour[0]], -1))
    for contour in rightContours:
        if contour[0] == imageWidth:
            contour[0] -= 1
        if contour[1] * 4 > rightHeights[contour[0]]:
            contours.append(getRawDistance(contour[0], rightHeights[contour[0]], 1))
    # keep angle and distance instead of x and size
    return contours

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