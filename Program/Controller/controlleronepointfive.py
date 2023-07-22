from IO import io
from Util import server
from Controller import converter
from Controller import slam
import math
import cv2
import base64
import numpy

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
    img = io.camera.io.camera.io.camera.io.camera.io.camera.read()
    leftEdgesImg, gLeftImg, rLeftImg = converter.filter(converter.undistort(img[0]))
    rightEdgesImg, gRightImg, rRightImg = converter.filter(converter.undistort(img[1]))
    # leftCoordinates, rightCoordinates = converter.getDistances(leftEdgesImg, rightEdgesImg)
    leftHeights, rightHeights = converter.getRawHeights(leftEdgesImg, rightEdgesImg)
    rLeftBlobs, gLeftBlobs, rRightBlobs, gRightBlobs = converter.getBlobs(rLeftImg, gLeftImg, rRightImg, gRightImg)
    # leftWalls = converter.getWallLandmarks(leftCoordinates, rLeftBlobs, gLeftBlobs)
    # rightWalls = converter.getWallLandmarks(rightCoordinates, rRightBlobs, gRightBlobs)
    leftWalls = converter.getWalls(leftHeights.copy(), rLeftBlobs, gLeftBlobs)
    rightWalls = converter.getWalls(rightHeights.copy(), rRightBlobs, gRightBlobs)
    rBlobs = []
    for blob in rLeftBlobs:
        rBlobs.append(converter.getRawDistance(blob[0], leftHeights[blob[0]], -1))
    for blob in rRightBlobs:
        rBlobs.append(converter.getRawDistance(blob[0], rightHeights[blob[0]], 1))
    gBlobs = []
    for blob in gLeftBlobs:
        gBlobs.append(converter.getRawDistance(blob[0], leftHeights[blob[0]], -1))
    for blob in gRightBlobs:
        gBlobs.append(converter.getRawDistance(blob[0], rightHeights[blob[0]], 1))
    corners, walls = converter.mergeWalls(leftWalls, rightWalls)
    xWalls = 0
    xWallsCount = 0
    yWalls = 0
    yWallsCount = 0
    
    for wall in walls:
        transformedCorner1 = slam.transformLandmark(wall[0])
        transformedCorner2 = slam.transformLandmark(wall[1])

        if transformedCorner1[X] - transformedCorner2[X] == 0:
            slope = (transformedCorner1[Y] - transformedCorner2[Y]) / (transformedCorner1[X] - transformedCorner2[X])
        else:
            slope = 93021930
        horizontal = abs(slope) < 1
        yIntercept = transformedCorner1[Y] = slope * transformedCorner1[X]
        
        distance = abs(slope * slam.carX + slam.carY + yIntercept) / math.sqrt(slope**2 + 1)

        nearestCorner = [slam.storedLandmarks[0][X], slam.storedLandmarks[0][Y]]
        snappingCorner = transformedCorner1
        if transformedCorner1[4] == False:
            snappingCorner = transformedCorner2
        for j in range(0, 4):
            if getDistance(slam.storedLandmarks[j], snappingCorner) < getDistance(nearestCorner, snappingCorner):
                nearestCorner = [slam.storedLandmarks[j][X], slam.storedLandmarks[j][Y]]
        
        if horizontal:
            if snappingCorner[Y] == 0 or snappingCorner[Y] == 200 or snappingCorner[Y] == 240:
                yWalls += snappingCorner[Y] + distance
            else:
                yWalls += snappingCorner[Y] - distance
            yWallsCount += 1
        else:
            if snappingCorner[X] == 0 or snappingCorner[X] == 200 or snappingCorner[X] == 240:
                xWalls += snappingCorner[X] + distance
            else:
                xWalls += snappingCorner[X] - distance
            xWallsCount += 1
    
    if xWallsCount > 0:
        slam.carX = xWalls / xWallsCount
    if yWallsCount > 0:
        slam.carY = yWalls / yWallsCount

    if slam.carDirection == NO_DIRECTION:
        slam.findStartingPosition(leftHeights, rightHeights)

    steering = 0

    blobSizeThreshold = 20
    blobSteering = 1
    for blob in rBlobs:
        if blob[1] > blobSizeThreshold:
            steering += slam.carDirection * blob[1] * blobSteering
    for blob in gBlobs:
        if blob[1] > blobSizeThreshold:
            steering -= slam.carDirection * blob[1] * blobSteering

    num = 0
    for wall in walls:
        transformedCorner1 = wall[0]
        transformedCorner2 = wall[1]
        
        if transformedCorner1[X] - transformedCorner2[X] == 0:
            slope = (transformedCorner1[Y] - transformedCorner2[Y]) / (transformedCorner1[X] - transformedCorner2[X])
        else:
            slope = 93021930
        horizontal = abs(slope) < 1
        yIntercept = transformedCorner1[Y] = slope * transformedCorner1[X]
        
        distance = abs(slope * slam.carX + slam.carY + yIntercept) / math.sqrt(slope**2 + 1)
        if distance < 20:
            if num == 0:
                steering += 50
            elif num == 1:
                steering += -50 * slam.carDirection
            elif num == 2:
                steering += -50

        num += 1
    # if slam.carX < 100 and slam.carY < 100:
    #     steering += 100

    if useServer:
        data = {
            'images': [
                base64.b64encode(cv2.imencode('.png', cv2.merge((leftEdgesImg, gLeftImg, rLeftImg)))[1]).decode(),
                base64.b64encode(cv2.imencode('.png', cv2.merge((rightEdgesImg, gRightImg, rRightImg)))[1]).decode(),
                1,
                1
            ],
            'distances': [],
            'heights': [leftHeights.tolist(), rightHeights.tolist()],
            'pos': [slam.carX, slam.carY, slam.carAngle],
            'landmarks': slam.storedLandmarks,
            'rawLandmarks': [rBlobs, gBlobs, walls],
            'blobs': [[rLeftBlobs, gLeftBlobs], [rRightBlobs, gRightBlobs]],
            'steering': steering,
            'waypoints': [[], []],
        }
        server.emit('data', data)
    io.drive.steer(steering)

def getDistance(a, b):
    return math.sqrt(math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2))
