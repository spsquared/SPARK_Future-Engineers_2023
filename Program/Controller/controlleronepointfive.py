from IO import io
from Util import server
from Controller import converter
from Controller import slam
import math
import cv2
import base64
import numpy
import time

X = 0
Y = 1
TYPE = 2
FOUND = 3

OUTER_WALL = 0
INNER_WALL = 1
RED_PILLAR = 2
GREEN_PILLAR = 3

NO_DIRECTION = 0
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1



useServer = True
def setMode(sendServer: bool = None):
    global useServer
    if sendServer != None: useServer = sendServer

def drive():
# def drive(img):
    totalStart = time.perf_counter()
    start = time.perf_counter()
    read = io.camera.io.camera.io.camera.io.camera.io.camera.read()
    print("camera: ", time.perf_counter() - start)
    start = time.perf_counter()
    # read = numpy.split(numpy.array(img), 2, axis=1)
    leftEdgesImg, gLeftImg, rLeftImg = converter.filter(converter.undistort(read[0]))
    rightEdgesImg, gRightImg, rRightImg = converter.filter(converter.undistort(read[1]))
    print("filter + undistort: ", time.perf_counter() - start)
    start = time.perf_counter()
    # leftCoordinates, rightCoordinates = converter.getDistances(leftEdgesImg, rightEdgesImg)

    leftHeights, rightHeights = converter.getRawHeights(leftEdgesImg, rightEdgesImg)
    rLeftContours = converter.getContours(rLeftImg)
    gLeftContours = converter.getContours(gLeftImg)
    rRightContours = converter.getContours(rRightImg)
    gRightContours = converter.getContours(gRightImg)

    leftWalls = converter.getWalls(leftHeights.copy(), rLeftContours, gLeftContours)
    rightWalls = converter.getWalls(rightHeights.copy(), rRightContours, gRightContours)

    rContours = converter.mergeContours(rLeftContours, rRightContours, leftHeights, rightHeights)
    gContours = converter.mergeContours(gLeftContours, gRightContours, leftHeights, rightHeights)

    corners, walls = converter.processWalls(leftWalls, rightWalls)
    print("image processing: ", time.perf_counter() - start)
    start = time.perf_counter()

    # slam.carAngle = io.imu.angle()
    # xWalls = 0
    # xWallsCount = 0
    # yWalls = 0
    # yWallsCount = 0
    
    # for wall in walls:
    #     transformedCorner1 = slam.transformLandmark(wall[0])
    #     transformedCorner2 = slam.transformLandmark(wall[1])

    #     if transformedCorner1[X] - transformedCorner2[X] != 0 and transformedCorner1[Y] - transformedCorner2[Y] != 0:
    #         slope = (transformedCorner1[Y] - transformedCorner2[Y]) / (transformedCorner1[X] - transformedCorner2[X])
    #         horizontal = abs(slope) < 1
    #         yIntercept = transformedCorner1[Y] - slope * transformedCorner1[X]
            
    #         distance = abs(slope * slam.carX + slam.carY + yIntercept) / math.sqrt(slope**2 + 1)
    #     elif transformedCorner1[Y] - transformedCorner2[Y] != 0:
    #         horizontal = False
    #         distance = abs(slam.carX - transformedCorner1[X])
    #     else:
    #         horizontal = True
    #         distance = abs(slam.carY - transformedCorner1[Y])

    #     nearestCorner = [slam.storedLandmarks[0][X], slam.storedLandmarks[0][Y]]
    #     snappingCorner = transformedCorner1
    #     if transformedCorner1[4] == False:
    #         snappingCorner = transformedCorner2
    #     for j in range(0, 4):
    #         if getDistance(slam.storedLandmarks[j], snappingCorner) < getDistance(nearestCorner, snappingCorner):
    #             nearestCorner = [slam.storedLandmarks[j][X], slam.storedLandmarks[j][Y]]
        
    #     if horizontal:
    #         if snappingCorner[Y] == 0 or snappingCorner[Y] == 200 or snappingCorner[Y] == 240:
    #             yWalls += snappingCorner[Y] + distance
    #         else:
    #             yWalls += snappingCorner[Y] - distance
    #         yWallsCount += 1
    #     else:
    #         if snappingCorner[X] == 0 or snappingCorner[X] == 200 or snappingCorner[X] == 240:
    #             xWalls += snappingCorner[X] + distance
    #         else:
    #             xWalls += snappingCorner[X] - distance
    #         xWallsCount += 1
    
    # if xWallsCount > 0:
    #     slam.carX = xWalls / xWallsCount
    # if yWallsCount > 0:
    #     slam.carY = yWalls / yWallsCount
    
    # if abs(slam.carX - 150) > 50 and abs(slam.carY - 150) > 50:
    #     print(slam.carx, slam.carY)
    #     print("CORNER !!!! WARNNIG: CORNER DETECTED!!!1!!!!!11!!")

    # print(slam.carX, slam.carY)

    if slam.carDirection == NO_DIRECTION:
        slam.findStartingPosition(leftHeights, rightHeights)
    
    processedWalls = []

    cornerSection = False

    for wall in walls:
        transformedCorner1 = wall[0]
        transformedCorner2 = wall[1]

        LEFT = 0
        CENTER = 1
        RIGHT = 2
        wallType = 0
        
        if transformedCorner1[X] - transformedCorner2[X] != 0 and transformedCorner1[Y] - transformedCorner2[Y] != 0:
            slope = (transformedCorner1[Y] - transformedCorner2[Y]) / (transformedCorner1[X] - transformedCorner2[X])
            yIntercept = transformedCorner1[Y] - slope * transformedCorner1[X]
            
            distance = abs(yIntercept) / math.sqrt(slope**2 + 1)

            if abs(slope) < 0.2:
                wallType = CENTER
            else:
                if transformedCorner1[X] > 0:
                    wallType = RIGHT
                else:
                    wallType = LEFT
        elif transformedCorner1[Y] - transformedCorner2[Y] != 0:
            distance = abs(transformedCorner1[X])
            if transformedCorner1[X] > 0:
                wallType = RIGHT
            else:
                wallType = LEFT
        else:
            distance = abs(transformedCorner1[Y])
            wallType = CENTER
        
        processedWalls.append([wallType, distance])
        if wallType == CENTER:
            print(distance)
            if distance < 100:
                cornerSection = True
    
    if cornerSection:
        print("a")

    steering = 0

    contourDistanceThreshold = 80
    contourSteering = 10

    turnDistance = 70

    for contour in rContours:
        if contour[2] < contourDistanceThreshold and contour[0] > -10 and contour[1] > 10:
            steering += slam.carDirection * (contourDistanceThreshold - contour[2]) * contourSteering
            turnDistance = 70 + 30 * slam.carDirection
    for contour in gContours:
        if contour[2] < contourDistanceThreshold and contour[0] < 10 and contour[1] > 10:
            steering += -slam.carDirection * (contourDistanceThreshold - contour[2]) * contourSteering
            turnDistance = 70 - 30 * slam.carDirection

    for wall in processedWalls:

        LEFT = 0
        CENTER = 1
        RIGHT = 2

        wallType = wall[0]
        distance = wall[1]
        
        if wallType == CENTER:
            if cornerSection and distance < turnDistance:
                steering += 200 * slam.carDirection
        elif wallType == LEFT:
            if distance < 40:
                steering += (100 - distance)
        else:
            if distance < 40:
                steering += -(100 - distance)

    print("driving: ", time.perf_counter() - start)
    start = time.perf_counter()

    if useServer:
        data = {
            'images': [
                base64.b64encode(cv2.imencode('.png', cv2.merge((leftEdgesImg, gLeftImg, rLeftImg)))[1]).decode(),
                base64.b64encode(cv2.imencode('.png', cv2.merge((rightEdgesImg, gRightImg, rRightImg)))[1]).decode(),
                1,
                1,
                1
            ],
            'distances': [],
            'heights': [leftHeights.tolist(), rightHeights.tolist()],
            'pos': [slam.carX, slam.carY, slam.carAngle],
            'landmarks': slam.storedLandmarks,
            'rawLandmarks': [rContours, gContours, walls],
            'contours': [[rLeftContours, gLeftContours], [rRightContours, gRightContours]],
            'corners': corners,
            'steering': steering,
            'waypoints': [[], []],
        }
        server.emit('data', data)
    print("sendserver: ", time.perf_counter() - start)
    
    io.drive.steer(steering)

    print("total: ", time.perf_counter() - totalStart)
    # for points in leftWalls:
    #     x1,y1,x2,y2=points
    #     cv2.line(leftEdgesImg,(x1,y1),(x2,y2),125,2)
    
    # print(leftWalls)

    # return leftEdgesImg

def getDistance(a, b):
    try:
        return math.sqrt(math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2))
    except Exception as e:
        print(e, a, b)
