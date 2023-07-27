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
DISTANCE = 2
ANGLE = 3

OUTER_WALL = 0
INNER_WALL = 1
RED_PILLAR = 2
GREEN_PILLAR = 3

storedLandmarks = [
    [0, 0, OUTER_WALL, True, 0], # Outer wall corners
    [300, 0, OUTER_WALL, True, 0],
    [0, 300, OUTER_WALL, True, 0],
    [300, 300, OUTER_WALL, True, 0],
    [0, 0, INNER_WALL, False, 0], # Inner wall corners
    [0, 0, INNER_WALL, False, 0],
    [0, 0, INNER_WALL, False, 0],
    [0, 0, INNER_WALL, False, 0],
    [0, 0, RED_PILLAR, False, 0], # Red Pillars
    [0, 0, RED_PILLAR, False, 0],
    [0, 0, RED_PILLAR, False, 0],
    [0, 0, RED_PILLAR, False, 0],
    [0, 0, RED_PILLAR, False, 0],
    [0, 0, RED_PILLAR, False, 0],
    [0, 0, RED_PILLAR, False, 0],
    [0, 0, RED_PILLAR, False, 0],
    [0, 0, GREEN_PILLAR, False, 0], # green pillarS
    [0, 0, GREEN_PILLAR, False, 0],
    [0, 0, GREEN_PILLAR, False, 0],
    [0, 0, GREEN_PILLAR, False, 0],
    [0, 0, GREEN_PILLAR, False, 0],
    [0, 0, GREEN_PILLAR, False, 0],
    [0, 0, GREEN_PILLAR, False, 0],
    [0, 0, GREEN_PILLAR, False, 0],
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
carSpeed = 0

NO_DIRECTION = 0
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1
carDirection = NO_DIRECTION
carDirectionGuess = 0
carDirectionGuesses = 0
carX = 150
carY = 150
carAngle = 0

carSections = 0
carSectionsTimer = 0
carSectionsExited = 0
carSectionsCooldown = 0
carSectionsEnd = -1
uTurnPillar = 0
uTurning = False
uTurnStage = 0
uTurnGyroAngle = 0
# carAngle = math.pi / 2

maxErrorDistance = 20

def updateUnknownLandmarks(landmarkData, possibleLandmarks, possibleLandmarkStride, index, maxLandmarks, landmarkType):
    landmarks = []
    for landmark in landmarkData:
        # find nearest landmark
        transformedLandmark = transformLandmark(landmark)

        newLandmark = False
        newLandmarkIndex = None
        nearestLandmark = [None]

        for j in range(index, index + maxLandmarks):
            if storedLandmarks[j][FOUND]:
                if nearestLandmark[0] == None:
                    nearestLandmark = [storedLandmarks[j][X], storedLandmarks[j][Y]]
                    newLandmark = False
                elif getDistance(storedLandmarks[j], transformedLandmark) < getDistance(nearestLandmark, transformedLandmark):
                    nearestLandmark = [storedLandmarks[j][X], storedLandmarks[j][Y]]
                    newLandmark = False
            else:
                for k in range((j - index) * possibleLandmarkStride, (j - index) * possibleLandmarkStride + possibleLandmarkStride):
                    if nearestLandmark[0] == None:
                        nearestLandmark = possibleLandmarks[j]
                        newLandmark = True
                        newLandmarkIndex = k
                    elif getDistance(possibleLandmarks[j], transformedLandmark) < getDistance(nearestLandmark, transformedLandmark):
                        nearestLandmark = possibleLandmarks[j]
                        newLandmark = True
                        newLandmarkIndex = k

        if getDistance(nearestLandmark, transformedLandmark) > maxErrorDistance:
            continue
        nearestLandmark.append(landmark[DISTANCE])
        nearestLandmark.append(landmark[ANGLE])
        
        if newLandmark:
            storedLandmarks[round(newLandmarkIndex / possibleLandmarkStride) + index] = [nearestLandmark[X], nearestLandmark[Y], landmarkType, True, 0]
        
        landmarks.append(nearestLandmark)
    return landmarks

def transformLandmark(landmark):
    landmark = list(landmark)
    landmark[X] = carX + math.sin(carAngle) * landmark[X] + math.cos(carAngle) * landmark[Y]
    landmark[Y] = carY + math.cos(carAngle) * landmark[X] + math.sin(carAngle) * landmark[Y]
    return landmark

def slam(corners, walls, redBlobs, greenBlobs):
    global storedLandmarks, possibleInnerWallLandmarks, possiblePillarLandmarks, carX, carY, carAngle, carDirection, carSpeed, maxErrorDistance
    try:
        # dead reckoning
        print(walls, redBlobs, greenBlobs)

        drCarX = carX + math.cos(carAngle) * carSpeed
        drCarY = carY + math.sin(carAngle) * carSpeed
        # drCarAngle = io.imu.angle
        drCarAngle = 0

        # get position from landmarks

        landmarks = []

        lmCarX = 0
        lmCarY = 0
        lmCarAngle = 0

        for landmark in corners:
            # find nearest landmark
            transformedLandmark = transformLandmark(landmark)

            newLandmark = False
            nearestLandmark = [storedLandmarks[0][X], storedLandmarks[0][Y]]
            for j in range(0, 4):
                if getDistance(storedLandmarks[j], transformedLandmark) < getDistance(nearestLandmark, transformedLandmark):
                    nearestLandmark = [storedLandmarks[j][X], storedLandmarks[j][Y]]
            for j in range(5, 8):
                if storedLandmarks[j][FOUND]:
                    if getDistance(storedLandmarks[j], transformedLandmark) < getDistance(nearestLandmark, transformedLandmark):
                        nearestLandmark = [storedLandmarks[j][X], storedLandmarks[j][Y]]
                        newLandmark = False
                else:
                    for k in range((j - 5) * 4, (j - 5) * 4 + 4):
                        if getDistance(possibleInnerWallLandmarks[k], transformedLandmark) < getDistance(nearestLandmark, transformedLandmark):
                            nearestLandmark = possibleInnerWallLandmarks[k]
                            newLandmark = True
                            newLandmarkIndex = k

            if getDistance(nearestLandmark, transformedLandmark) > maxErrorDistance:
                continue
            nearestLandmark.append(landmark[DISTANCE])
            nearestLandmark.append(landmark[ANGLE])
            
            if newLandmark:
                storedLandmarks[math.floor(newLandmarkIndex / 4) + 4] = [nearestLandmark[X], nearestLandmark[Y], INNER_WALL, True, 0]

            landmarks.append(nearestLandmark)

        xWalls = []
        yWalls = []
        
        for wall in walls:
            transformedCorner1 = transformLandmark(wall[0])
            transformedCorner2 = transformLandmark(wall[1])
            
            slope = (transformedCorner1[Y] - transformedCorner2[Y]) / (transformedCorner1[X] - transformedCorner2[X])
            horizontal = abs(slope) < 1
            yIntercept = transformedCorner1[Y] = slope * transformedCorner1[X]
            
            distance = abs(slope * carX + carY + yIntercept) / math.sqrt(slope**2 + 1)

            nearestCorner = [storedLandmarks[0][X], storedLandmarks[0][Y]]
            snappingCorner = transformedCorner1
            if transformedCorner1[4] == False:
                snappingCorner = transformedCorner2
            for j in range(0, 8):
                if storedLandmarks[j][FOUND]:
                    if getDistance(storedLandmarks[j], snappingCorner) < getDistance(nearestCorner, snappingCorner):
                        nearestCorner = [storedLandmarks[j][X], storedLandmarks[j][Y]]
            
            if horizontal:
                if snappingCorner[Y] == 0 or snappingCorner[Y] == 200 or snappingCorner[Y] == 240:
                    yWalls.append(snappingCorner[Y] + distance)
                else:
                    yWalls.append(snappingCorner[Y] - distance)
            else:
                if snappingCorner[X] == 0 or snappingCorner[X] == 200 or snappingCorner[X] == 240:
                    xWalls.append(snappingCorner[X] + distance)
                else:
                    xWalls.append(snappingCorner[X] - distance)

        
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
            
            for wall in xWalls:
                array.append(math.pow(x - wall, 2))
            for wall in yWalls:
                array.append(math.pow(y - wall, 2))
            
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
                array.append(math.pow(math.atan2(lmCarX - landmark[Y], lmCarY - landmark[X]) - landmark[ANGLE] - a, 2))
            
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
        # io.imu.setAngle(carAngle)
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

def getDistance(a, b):
    return math.sqrt(math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2))