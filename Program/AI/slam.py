from IO import io
import numpy
import cv2
import base64
import statistics
import math
import json

# does EKF SLAM

X = 0
Y = 1
FOUND = 2
COLOR = 3
RED = 0
GREEN = 1

storedLandmarks = [
    [0, 0, True], # First 4 are outer wall corners
    [300, 0, True],
    [0, 300, True],
    [300, 300, True],
    [0, 0, False], # Second 4 are inner wall corners
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False], # Third 4 are red pillars
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False], # Fourth 4 are green pillars
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
]

possibleWallLandmarks = [
    [100, 100],
    [100, 200],
    [200, 100],
    [200, 200],
]

possiblePillarLandmarks = [
    # TODO
]

carX = -1
carY = -1
carAngle = 0

carSpeed = 0

def slam(outerWalls, innerWalls, redBlobs, greenBlobs):
    # dead reckoning

    drCarX = carX + math.cos(carAngle) * carSpeed
    drCarY = carY + math.sin(carAngle) * carSpeed
    drCarAngle = io.gyro.read()

    # average position from landmarks

    landmarks = []

    lmCarX = 0
    lmCarY = 0
    lmCarAngle = 0

    def getDistance(a, b):
        return math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2)

    for i in range(len(outerWalls)):
        lmNum += 1

        # find nearest landmark
        nearestLandmark = storedLandmarks[0]
        for j in range(1, 4):
            if (getDistance(storedLandmarks[j], outerWalls[i]) < getDistance(nearestLandmark, outerWalls[i])):
                nearestLandmark = storedLandmarks[j]
        
        landmarks.append(nearestLandmark)
        

        
    lmCarX /= lmNum
    lmCarY /= lmNum
    lmCarAngle /= lmNum

def findStartingPosition(outerWalls, innerWalls, redBlobs, greenBlobs):
