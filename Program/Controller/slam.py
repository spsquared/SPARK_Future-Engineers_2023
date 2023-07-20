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
TYPE = 2
FOUND = 3
DISTANCE = 4
RED = 0
GREEN = 1

OUTER_WALL = 0
INNER_WALL = 1
RED_PILLAR = 2
GREEN_PILLAR = 3

# make numpy/cupy matrix so we can poke with GPU for sPEEEEEEEEEEED?
storedLandmarks = numpy.array([
    [0, 0, True, 0, OUTER_WALL], # Outer wall corners
    [300, 0, True, 0, OUTER_WALL],
    [0, 300, True, 0, OUTER_WALL],
    [300, 300, True, 0, OUTER_WALL],
    [0, 0, False, 0, INNER_WALL], # Inner wall corners
    [0, 0, False, 0, INNER_WALL],
    [0, 0, False, 0, INNER_WALL],
    [0, 0, False, 0, INNER_WALL],
    [0, 0, False, 0, RED_PILLAR], # Red Pillars
    [0, 0, False, 0, RED_PILLAR],
    [0, 0, False, 0, RED_PILLAR],
    [0, 0, False, 0, RED_PILLAR],
    [0, 0, False, 0, RED_PILLAR],
    [0, 0, False, 0, RED_PILLAR],
    [0, 0, False, 0, RED_PILLAR],
    [0, 0, False, 0, RED_PILLAR],
    [0, 0, False, 0, GREEN_PILLAR], # green pillarS
    [0, 0, False, 0, GREEN_PILLAR],
    [0, 0, False, 0, GREEN_PILLAR],
    [0, 0, False, 0, GREEN_PILLAR],
    [0, 0, False, 0, GREEN_PILLAR],
    [0, 0, False, 0, GREEN_PILLAR],
    [0, 0, False, 0, GREEN_PILLAR],
    [0, 0, False, 0, GREEN_PILLAR],
])

possibleInnerWallLandmarks = numpy.array([
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
])

possiblePillarLandmarks = numpy.array([
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
])

carX = -1
carY = -1
carAngle = 0

CLOCKWISE = 1
COUNTER_CLOCKWISE = -1
carDirection = CLOCKWISE

carSpeed = 0

maxErrorDistance = 20

def getDistance(a, b):
    return math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2)

def updateUnknownLandmarks(landmarkData, possibleLandmarks, possibleLandmarkStride, index, maxLandmarks, landmarkType):
    landmarks = []
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
                        nearestLandmark.append(landmarkType)
                        nearestLandmark.append(True)
                        nearestLandmark.append(0)
                        newLandmark = True
                        newLandmarkIndex = k
                    elif getDistance(possibleLandmarks[j], landmark) < getDistance(nearestLandmark, landmark):
                        nearestLandmark = possibleLandmarks[j]
                        nearestLandmark.append(landmarkType)
                        nearestLandmark.append(True)
                        nearestLandmark.append(0)
                        newLandmark = True
                        newLandmarkIndex = k

        nearestLandmark[DISTANCE] = getDistance([carX, carY], landmark)
        if nearestLandmark[DISTANCE] > maxErrorDistance:
            continue
        
        if newLandmark:
            storedLandmarks[newLandmarkIndex / possibleLandmarkStride + index] = [nearestLandmark[X], nearestLandmark[Y], True]
        
        landmarks.append(nearestLandmark)
    return landmarks

def slam(walls, redBlobs, greenBlobs):
    global storedLandmarks, possibleInnerWallLandmarks, possiblePillarLandmarks, carX, carY, carAngle, carDirection, carSpeed, maxErrorDistance
    try:
        # dead reckoning

        drCarX = carX + math.cos(carAngle) * carSpeed
        drCarY = carY + math.sin(carAngle) * carSpeed
        # drCarAngle = io.imu.gyro.angle
        drCarAngle = 0

        # get position from landmarks

        landmarks = []

        lmCarX = 0
        lmCarY = 0
        lmCarAngle = 0

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
                            nearestLandmark.append(INNER_WALL)
                            nearestLandmark.append(True)
                            nearestLandmark.append(0)
                            newLandmark = True
                            newLandmarkIndex = k
                        elif getDistance(possibleInnerWallLandmarks[k], landmark) < getDistance(nearestLandmark, landmark):
                            nearestLandmark = possibleInnerWallLandmarks[k]
                            nearestLandmark.append(INNER_WALL)
                            nearestLandmark.append(True)
                            nearestLandmark.append(0)
                            newLandmark = True
                            newLandmarkIndex = k
            nearestLandmark[DISTANCE] = getDistance([carX, carY], landmark)
            if nearestLandmark[DISTANCE] > maxErrorDistance:
                continue
            
            if newLandmark:
                storedLandmarks[math.floor(newLandmarkIndex / 4) + 4] = [nearestLandmark[X], nearestLandmark[Y], True]

            landmarks.append(nearestLandmark)
        
        # unknown landmarks
        
        redBlobLandmarks = updateUnknownLandmarks(redBlobs, possiblePillarLandmarks, 6, 8, 8, RED_PILLAR)
        greenBlobLandmarks = updateUnknownLandmarks(greenBlobs, possiblePillarLandmarks, 6, 16, 8, GREEN_PILLAR)

        for landmark in redBlobLandmarks:
            landmarks.append(landmark)
        for landmark in greenBlobLandmarks:
            landmarks.append(landmark)

        print(landmarks)
        
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

        lmCarAngle = angleResult.x[0]

        # set car speed

        carSpeed = math.sqrt(math.pow((drCarX + lmCarX) / 2 - carX, 2) + math.pow((drCarY + lmCarY) / 2 - carY, 2))

        # average!!!!1

        carX = (drCarX + lmCarX) / 2
        carY = (drCarY + lmCarY) / 2
        carAngle = (drCarAngle + lmCarAngle) / 2

        print(carX, carY, carAngle)

        # update gyro angle to prevent drifting
        # io.imu.gyro.setAngle(carAngle)
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))


def findStartingPosition(leftHeights, rightHeights):
    global carX, carY, carAngle, carDirection
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