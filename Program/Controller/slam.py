from IO import io
from Util import server
from Controller import converter
import traceback
import numpy
import math
from scipy.optimize import least_squares

# does EKF SLAM without the Kalman filter

X = 0
Y = 1
FOUND = 2
COLOR = 3
DISTANCE = 4
RED = 0
GREEN = 1

# make numpy/cupy matrix so we can poke with GPU for sPEEEEEEEEEEED?
storedLandmarks = [
    [0, 0, True], # Outer wall corners
    [300, 0, True],
    [0, 300, True],
    [300, 300, True],
    [0, 0, False], # Inner wall corners
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False], # Red Pillars
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False], # green pillarS
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
    [0, 0, False],
]

possibleInnerWallLandmarks = [
    [60, 60],
    [100, 60],
    [60, 100],
    [100, 100],
    [200, 60],
    [240, 60],
    [200, 100],
    [240, 100],
    [60, 200],
    [100, 200],
    [60, 240],
    [100, 240],
    [200, 200],
    [240, 200],
    [200, 240],
    [240, 240],
]

possiblePillarLandmarks = [
    [100, 40], # section 1
    [100, 60],
    [150, 40],
    [150, 60],
    [200, 40],
    [200, 60],
    [40, 100], # section 2
    [60, 100],
    [40, 150],
    [60, 150],
    [40, 200],
    [60, 200],
    [100, 240], # section 3 
    [100, 260],
    [150, 240],
    [150, 260],
    [200, 240],
    [200, 260],
    [240, 100], # section 4
    [260, 100],
    [240, 150],
    [260, 150],
    [240, 200],
    [260, 200],
]

carX = -1
carY = -1
carAngle = 0

CLOCKWISE = 1
COUNTER_CLOCKWISE = -1
carDirection = CLOCKWISE

carSpeed = 0

def slam(walls, redBlobs, greenBlobs):
    try:
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

        for landmark in walls:
            # find nearest landmark

            newLandmark = False
            nearestLandmark = storedLandmarks[0]
            for j in range(0, 4):
                if getDistance(storedLandmarks[j], landmark) < getDistance(nearestLandmark, landmark):
                    nearestLandmark = storedLandmarks[j]
            for j in range(5, 8):
                if storedLandmarks[j][2]:
                    if nearestLandmark == None:
                        nearestLandmark = storedLandmarks[j]
                        newLandmark = False
                    elif getDistance(storedLandmarks[j], landmark) < getDistance(nearestLandmark, landmark):
                        nearestLandmark = storedLandmarks[j]
                        newLandmark = False
                else:
                    for k in range((j - 4) * 4, (j - 4) * 4 + 4):
                        if nearestLandmark == None:
                            nearestLandmark = possibleInnerWallLandmarks[k]
                            newLandmark = True
                            newLandmarkIndex = k
                        elif getDistance(possibleInnerWallLandmarks[k], landmark) < getDistance(nearestLandmark, landmark):
                            nearestLandmark = possibleInnerWallLandmarks[k]
                            newLandmark = True
                            newLandmarkIndex = k
            
            if newLandmark:
                storedLandmarks[math.floor(newLandmarkIndex / 4) + 4] = [nearestLandmark[X], nearestLandmark[Y], True]

            nearestLandmark[DISTANCE] = getDistance([carX, carY], landmark)
            landmarks.append(nearestLandmark)
        
        # unknown landmarks
        def updateUnknownLandmarks(landmarkData, possibleLandmarks, possibleLandmarkStride, index, maxLandmarks):
            for landmark in landmarkData:
                # find nearest landmark
                nearestLandmark = None

                newLandmark = False
                newLandmarkIndex = None

                for j in range(index, index + maxLandmarks):
                    if storedLandmarks[j][2]:
                        if nearestLandmark == None:
                            nearestLandmark = storedLandmarks[j]
                            newLandmark = False
                        elif getDistance(storedLandmarks[j], landmark) < getDistance(nearestLandmark, landmark):
                            nearestLandmark = storedLandmarks[j]
                            newLandmark = False
                    else:
                        for k in range((j - index) * possibleLandmarkStride, (j - index) * possibleLandmarkStride + possibleLandmarkStride):
                            if nearestLandmark == None:
                                nearestLandmark = possibleLandmarks[j]
                                newLandmark = True
                                newLandmarkIndex = k
                            elif getDistance(possibleLandmarks[j], landmark) < getDistance(nearestLandmark, landmark):
                                nearestLandmark = possibleLandmarks[j]
                                newLandmark = True
                                newLandmarkIndex = k
                
                if newLandmark:
                    storedLandmarks[newLandmarkIndex / possibleLandmarkStride + index] = [nearestLandmark[X], nearestLandmark[Y], True]
                
                nearestLandmark[DISTANCE] = getDistance([carX, carY], landmark)
                landmarks.append(nearestLandmark)
        
        updateUnknownLandmarks(redBlobs, possiblePillarLandmarks, 6, 8, 8)
        updateUnknownLandmarks(greenBlobs, possiblePillarLandmarks, 6, 16, 8)
        
        def positionEquations(guess):
            x, y = guess
            
            array = []

            for landmark in landmarks:
                array.append(math.pow(x - landmark[X], 2) + math.pow(y - landmark[Y], 2) - math.pow(landmark[DISTANCE], 2))
            
            return tuple(array)

        # omg using package
        # it uses the dead reckoning guess as initial guess
        initialPositionGuess = (drCarX, drCarY)

        # use least squares
        positionResult = least_squares(positionEquations, initialPositionGuess)

        # get position of results
        lmCarX = positionResult.x[0]
        lmCarY = positionResult.x[1]

        # get angle

        def angleEquations(guess):
            a = guess
            
            array = []

            for landmark in landmarks:
                array.append(math.pow(math.atan2(lmCarX - landmark[Y], lmCarY - landmark[X]) - a, 2))
            
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
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))


def findStartingPosition(leftHeights, rightHeights):
    frontWall = (leftHeights[380] + rightHeights[converter.imageWidth - 1 - 380]) / 2 #13 #18 for closeup
    leftWall = leftHeights[56] #55
    rightWall = rightHeights[converter.imageWidth - 1 - 56] #55
    # long = 29

    print(frontWall, leftWall, rightWall)

    closeFrontWall = 18
    farFrontWall = 13

    closeSideWall = 55
    farSideWall = 29

    # needs to be like 40 for side wall threshold

    x = 0
    y = 0

    if frontWall >= (closeFrontWall + farFrontWall) / 2:
        y = 125
    else:
        y = 175
    
    if leftWall >= 65:
        if rightWall >= 65:
            if leftWall >= (closeSideWall + farSideWall) / 2:
                x = 50
        else:
            x = 80
    else:
        x = 20
    
    carX = x
    carY = y
    carAngle = math.pi / 2
    if carDirection == COUNTER_CLOCKWISE:
        carAngle = 0