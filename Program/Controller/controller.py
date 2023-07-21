from Controller import converter
from Controller import slam
from IO import io
import math

X = 0
Y = 1
TYPE = 2
FOUND = 3

OUTER_WALL = 0
INNER_WALL = 1
RED_PILLAR = 2
GREEN_PILLAR = 3

CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

useServer = True
def setMode(sendServer: bool = None):
    global useServer
    if sendServer != None: useServer = sendServer

def drive():
    leftEdgesImg, leftBlurredG, leftBlurredR = converter.filter(io.camera.io.camera.io.camera.io.camera.io.camera.read()[0])
    rightEdgesImg, rightBlurredG, rightBlurredR = converter.filter(io.camera.io.camera.io.camera.io.camera.io.camera.read()[1])
    heights = converter.getHeights(leftEdgesImg, rightEdgesImg)
    # red
    # help heights are separate aaaaaaaaaaaaa
    pass

def getSteering():

    landmarks = slam.storedLandmarks[slam.storedLandmarks[FOUND]]
    landmarks.sort(landmarkSort)
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

    waypoints.sort(landmarkSort)
    
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

    return math.atan2(nextPoint[Y] - slam.carY, nextPoint[X] - slam.carX) - slam.carAngle

def landmarkSort(landmark):
    return slam.carDirection * (math.atan2(landmark[Y] - 150, landmark[X] - 150) - math.atan2(slam.carY - 150, slam.carX - 150))

def getDistance(a, b):
    return math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2)
