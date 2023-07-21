from Controller import converter
from Controller import slam
from IO import io
from Util import server
import math
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
    read = io.camera.io.camera.io.camera.io.camera.io.camera.read()
    leftEdgesIn, gLeftIn, rLeftIn = converter.filter(converter.undistort(read[0]))
    rightEdgesIn, gRightIn, rRightIn = converter.filter(converter.undistort(read[1]))
    # leftCoordinates, rightCoordinates = converter.getDistances(leftEdgesIn, rightEdgesIn)
    leftHeights, rightHeights = converter.getRawHeights(leftEdgesIn, rightEdgesIn)
    rLeftBlobs, gLeftBlobs, rRightBlobs, gRightBlobs = converter.getBlobs(rLeftIn, gLeftIn, rRightIn, gRightIn)
    # leftWalls = converter.getWallLandmarks(leftCoordinates, rLeftBlobs, gLeftBlobs)
    # rightWalls = converter.getWallLandmarks(rightCoordinates, rRightBlobs, gRightBlobs)
    leftWalls = converter.getWallLandmarks(leftHeights, rLeftBlobs, gLeftBlobs)
    rightWalls = converter.getWallLandmarks(rightHeights, rRightBlobs, gRightBlobs)
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
    walls = []
    for wall in leftWalls:
        walls.append(converter.getRawDistance(wall[0], leftHeights[wall[0]], -1))
    for wall in rightWalls:
        walls.append(converter.getRawDistance(wall[0], rightHeights[wall[0]], 1))
    if slam.carDirection == NO_DIRECTION:
        slam.findStartingPosition(leftHeights, rightHeights)
    slam.slam(walls, rBlobs, gBlobs)
    steering = getSteering()
    if useServer:
        server.emit('data', '\'data\'')
    return steering

def getSteering():

    landmarks = [x for x in slam.storedLandmarks if x[FOUND]]
    landmarks.sort(key=landmarkSort)
    waypoints = []

    outer = GREEN_PILLAR
    inner = RED_PILLAR

    if slam.carDirection == COUNTER_CLOCKWISE:
        outer = RED_PILLAR
        inner = GREEN_PILLAR

    for landmark in landmarks:
        if landmark[TYPE] == INNER_WALL:
            waypoints.push([(abs(landmark[X] - 150) / 2 + 150 / 2) * abs(landmark[X]) / landmark[X], (abs(landmark[Y] - 150) / 2 + 150 / 2) * abs(landmark[Y]) / landmark[Y]])
        elif landmark[TYPE] == outer:
            if landmark[X] >= 100 and landmark[X] <= 200:
                waypoints.push([landmark[X], (abs(landmark[Y] - 150) / 2 + 150 / 2) * abs(landmark[Y]) / landmark[Y]])
            else:
                waypoints.push([(abs(landmark[X] - 150) / 2 + 150 / 2) * abs(landmark[X]) / landmark[X], landmark[Y]])
        elif landmark[TYPE] == inner:
            if landmark[X] >= 100 and landmark[X] <= 200:
                waypoints.push([landmark[X], (abs(landmark[Y] - 150) / 2 + 50 / 2) * abs(landmark[Y]) / landmark[Y]])
            else:
                waypoints.push([(abs(landmark[X] - 150) / 2 + 50 / 2) * abs(landmark[X]) / landmark[X], landmark[Y]])

    waypoints.sort(key=landmarkSort)
    
    nextPoint = [slam.carX, slam.carY]
    nextPointDistance = 10

    for waypoint in waypoints:
        if nextPointDistance < getDistance(nextPoint, waypoint):
            nextPointDistance -= getDistance(nextPoint, waypoint)
            nextPoint = [waypoint[X], waypoint[Y]]
        else:
            angle = math.atan2(waypoint[Y] - nextPoint[Y], waypoint[X] - waypoint[X])
            magnitude = nextPointDistance
            nextPoint[X] += math.cos(angle) * magnitude
            nextPoint[Y] += math.sin(angle) * magnitude

    return min(max(((math.atan2(nextPoint[Y] - slam.carY, nextPoint[X] - slam.carX) - slam.carAngle) / math.pi * 180 / 40 * 100), -100), 100)

def landmarkSort(landmark):
    return slam.carDirection * (math.atan2(landmark[Y] - 150, landmark[X] - 150) - math.atan2(slam.carY - 150, slam.carX - 150))

def getDistance(a, b):
    return math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2)
