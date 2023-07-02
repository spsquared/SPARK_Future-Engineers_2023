from IO import io
import numpy
import math
import scipy
from scipy.optimize import least_squares

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

    # get position from landmarks

    landmarks = []

    lmCarX = 0
    lmCarY = 0
    lmCarAngle = 0

    def getDistance(a, b):
        return math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2)

    for i in range(len(outerWalls)):
        # find nearest landmark
        nearestLandmark = storedLandmarks[0]
        for j in range(1, 4):
            if (getDistance(storedLandmarks[j], outerWalls[i]) < getDistance(nearestLandmark, outerWalls[i])):
                nearestLandmark = storedLandmarks[j]
        
        landmarks.append(nearestLandmark)
    
    def positionEquations(guess):
        x, y, r = guess
        
        array = []

        for i in range(len(landmarks)):
            array.append(math.pow(x - landmarks[X], 2) + math.pow(y - landmarks[Y], 2) - math.pow(math.sqrt(math.pow(landmarks[X], 2) + math.pow(landmarks[Y], 2)) - r, 2))
        
        return tuple(array)

    # omg using package
    # it uses the dead reckoning guess as initial guess
    initialPositionGuess = (drCarX, drCarY, 0)

    # use least squares
    positionResult = least_squares(positionEquations, initialPositionGuess)

    # get position of results
    lmCarX = positionResult.x[0]
    lmCarY = positionResult.x[1]

    # get angle

    def angleEquations(guess):
        a = guess
        
        array = []

        for i in range(len(landmarks)):
            array.append(math.pow(math.atan2(lmCarX - landmarks[Y], lmCarY - landmarks[X]) - a, 2))
        
        return tuple(array)

    # omg using package
    # it uses the dead reckoning guess as initial guess
    initialAngleGuess = drCarAngle

    # use least squares
    angleResult = least_squares(angleEquations, initialAngleGuess)

    lmCarAngle = angleResult

    # set car speed

    carSpeed = math.sqrt(math.pow((drCarX + lmCarX) / 2 - carX, 2) + math.pow((drCarY + lmCarY) / 2 - carY, 2))

    # average!!!!1

    carX = (drCarX + lmCarX) / 2
    carY = (drCarY + lmCarY) / 2
    carAngle = (drCarAngle + lmCarAngle) / 2


def findStartingPosition(outerWalls, innerWalls, redBlobs, greenBlobs):
    # oof
    return "stop"