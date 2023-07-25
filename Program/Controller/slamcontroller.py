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
# def drive(img):
    imgs = io.camera.io.camera.io.camera.io.camera.io.camera.read()
    leftEdgesImg, gLeftImg, rLeftImg = converter.filter(converter.undistort(imgs[0]))
    rightEdgesImg, gRightImg, rRightImg = converter.filter(converter.undistort(imgs[1]))
    # leftCoordinates, rightCoordinates = converter.getDistances(leftEdgesImg, rightEdgesImg) # OOOOOOOOOOOOOOOF BORKEN
    leftHeights, rightHeights = converter.getRawHeights(leftEdgesImg, rightEdgesImg)
    rLeftContours, gLeftContours, rRightContours, gRightContours = converter.getContours(rLeftImg, gLeftImg, rRightImg, gRightImg)
    # leftWalls = converter.getWallLandmarks(leftCoordinates, rLeftContours, gLeftContours)
    # rightWalls = converter.getWallLandmarks(rightCoordinates, rRightContours, gRightContours)
    leftWalls = converter.getWalls(leftHeights.copy(), rLeftContours, gLeftContours)
    rightWalls = converter.getWalls(rightHeights.copy(), rRightContours, gRightContours)
    rContours = []
    for contour in rLeftContours:
        rContours.append(converter.getRawDistance(contour[0], leftHeights[contour[0]], -1))
    for contour in rRightContours:
        rContours.append(converter.getRawDistance(contour[0], rightHeights[contour[0]], 1))
    gContours = []
    for contour in gLeftContours:
        gContours.append(converter.getRawDistance(contour[0], leftHeights[contour[0]], -1))
    for contour in gRightContours:
        gContours.append(converter.getRawDistance(contour[0], rightHeights[contour[0]], 1))
    corners, walls = converter.processWalls(leftWalls, rightWalls)
    if slam.carDirection == NO_DIRECTION:
        slam.findStartingPosition(leftHeights, rightHeights)
    slam.slam(corners, walls, rContours, gContours)
    steering, waypoints, nextPoint = getSteering(leftHeights, rightHeights, rLeftContours, gLeftContours, rRightContours, gRightContours)
    if useServer:
        data = {
            'images': [
                base64.b64encode(cv2.imencode('.png', cv2.merge((leftEdgesImg, gLeftImg, rLeftImg)))[1]).decode(),
                base64.b64encode(cv2.imencode('.png', cv2.merge((rightEdgesImg, gRightImg, rRightImg)))[1]).decode(),
                1,
                1,
                0
            ],
            'distances': [],
            'heights': [leftHeights.tolist(), rightHeights.tolist()],
            'pos': [slam.carX, slam.carY, slam.carAngle],
            'landmarks': slam.storedLandmarks,
            'rawLandmarks': [rContours, gContours, walls],
            'contours': [[rLeftContours, gLeftContours], [rRightContours, gRightContours]],
            'walls': [corners, walls],
            'steering': steering,
            'waypoints': [waypoints, nextPoint],
        }
        server.emit('data', data)
    # read[0] = converter.undistort(read[0])
    # for l in leftWalls:
    #     cv2.line(read[0], (l[0], l[1] + 14), (l[2], l[3] + 14), (255, 0, 0), 1)
    # return read[0]
    io.drive.steer(steering)

def getSteering(leftHeights, rightHeights, rLeftContours, gLeftContours, rRightContours, gRightContours):
    global contourSizeThreshold
    landmarks = [x for x in slam.storedLandmarks if x[FOUND]]

    if len(landmarks) == 4:
        steering = 0

        contourSizeThreshold = 20
        contourSteering = 1
        for contour in rLeftContours + rRightContours:
            if contour[1] > contourSizeThreshold:
                steering += slam.carDirection * contour[1] * contourSteering
        for contour in gLeftContours + gRightContours:
            if contour[1] > contourSizeThreshold:
                steering -= slam.carDirection * contour[1] * contourSteering
        
        frontWallThreshold = 15
        sideWallThreshold = 80
        if leftHeights[56] > sideWallThreshold:
            steering += 80
        if leftHeights[380] > frontWallThreshold:
            steering += -slam.carDirection * 80
        if rightHeights[converter.imageWidth - 1 - 56] > sideWallThreshold:
            steering += -80
        if rightHeights[converter.imageWidth - 1 - 380] > frontWallThreshold:
            steering += -slam.carDirection * 80

        return [steering, [], []]

    landmarks.sort(key=landmarkSort)
    waypoints = []

    outer = GREEN_PILLAR
    inner = RED_PILLAR

    if slam.carDirection == COUNTER_CLOCKWISE:
        outer = RED_PILLAR
        inner = GREEN_PILLAR

    for landmark in landmarks:
        if landmark[TYPE] == INNER_WALL:
            waypoints.append([(abs(landmark[X] - 150) / 2 + 150 / 2) * abs(landmark[X]) / landmark[X], (abs(landmark[Y] - 150) / 2 + 150 / 2) * abs(landmark[Y]) / landmark[Y]])
        elif landmark[TYPE] == outer:
            if landmark[X] >= 100 and landmark[X] <= 200:
                waypoints.append([landmark[X], (abs(landmark[Y] - 150) / 2 + 150 / 2) * abs(landmark[Y]) / landmark[Y]])
            else:
                waypoints.append([(abs(landmark[X] - 150) / 2 + 150 / 2) * abs(landmark[X]) / landmark[X], landmark[Y]])
        elif landmark[TYPE] == inner:
            if landmark[X] >= 100 and landmark[X] <= 200:
                waypoints.append([landmark[X], (abs(landmark[Y] - 150) / 2 + 50 / 2) * abs(landmark[Y]) / landmark[Y]])
            else:
                waypoints.append([(abs(landmark[X] - 150) / 2 + 50 / 2) * abs(landmark[X]) / landmark[X], landmark[Y]])

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
            break

    return [min(max(((math.atan2(nextPoint[Y] - slam.carY, nextPoint[X] - slam.carX) - slam.carAngle) / math.pi * 180 / 40 * 100), -100), 100), waypoints, nextPoint]

def landmarkSort(landmark):
    return slam.carDirection * (math.atan2(landmark[Y] - 150, landmark[X] - 150) - math.atan2(slam.carY - 150, slam.carX - 150))

def getDistance(a, b):
    return math.sqrt(math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2))
