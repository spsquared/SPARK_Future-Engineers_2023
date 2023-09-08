from IO import io
from Util import server
from Controller import converter
from Controller import slam
import math
import cv2
import base64
import numpy
import time

# defining constants
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

# WARNING !!!!! DO NOT TURN ON NO PILLAR MODE WITH PILLARS
# WARNNIG !!!!! DO NOT TURN ON NO PILLAR MODE WITH PILLARS
# WARNING !!!!! DO NOT TURN ON NO PILLAR MODE WITH PILLARS
NO_PILLARS = False
if NO_PILLARS:
    print("[!] [!] [!] [!] No pillar mode is on! [!] [!] [!] [!]") # oh noes no pillar mode is on

# speed !!!!
speed = 90
# speed = 100

useServer = True
def setMode(sendServer: bool = None):
    global useServer
    if sendServer != None: useServer = sendServer

def drive(manual: bool = False):
# def drive(img):
    totalStart = time.perf_counter()
    start = time.perf_counter()
    read = io.camera.io.camera.io.camera.io.camera.io.camera.read()
    # print("camera: ", time.perf_counter() - start)
    start = time.perf_counter()
    # read = numpy.split(numpy.array(img), 2, axis=1)
    leftEdgesImg, gLeftImg, rLeftImg = converter.filter(converter.undistort(read[0]))
    rightEdgesImg, gRightImg, rRightImg = converter.filter(converter.undistort(read[1]))
    # print("filter + undistort: ", time.perf_counter() - start)
    start = time.perf_counter()
    # leftCoordinates, rightCoordinates = converter.getDistances(leftEdgesImg, rightEdgesImg)

    leftHeights, rightHeights, leftWallStarts, rightWallStarts = converter.getRawHeights(leftEdgesImg, rightEdgesImg)
    rLeftContours = converter.getContours(rLeftImg)
    gLeftContours = converter.getContours(gLeftImg)
    rRightContours = converter.getContours(rRightImg)
    gRightContours = converter.getContours(gRightImg)

    rawLeftWalls = converter.getWalls(leftHeights.copy(), rLeftContours, gLeftContours)
    rawRightWalls = converter.getWalls(rightHeights.copy(), rRightContours, gRightContours)

    rContours = converter.mergeContours(rLeftContours, rRightContours, leftHeights, rightHeights)
    gContours = converter.mergeContours(gLeftContours, gRightContours, leftHeights, rightHeights)

    corners, walls = converter.processWalls(rawLeftWalls, rawRightWalls)
    # print("image processing: ", time.perf_counter() - start)
    start = time.perf_counter()

    # slam.carAngle = io.imu.angle()

    if slam.carDirectionGuesses < 9:
        oneFourths = int((converter.imageWidth - 3) / 4)
        threeFourths = int((converter.imageWidth - 3) * 3 / 4)
        leftDifferences = numpy.diff(leftHeights, 3)
        rightDifferences = numpy.diff(numpy.flip(rightHeights), 3)
        leftJump = numpy.argmax(numpy.append(leftDifferences[:threeFourths] < -6, True))
        leftJumpPillar = numpy.argmax(numpy.append(leftDifferences[:threeFourths] > 6, True))
        rightJump = numpy.argmax(numpy.append(rightDifferences[:threeFourths] < -6, True))
        rightJumpPillar = numpy.argmax(numpy.append(rightDifferences[:threeFourths] > 6, True))
        leftJump2 = numpy.argmax(numpy.append(numpy.flip(leftDifferences[threeFourths:]) < -6, True))
        leftJump2Pillar = numpy.argmax(numpy.append(numpy.flip(leftDifferences[threeFourths:]) > 6, True))
        rightJump2 = numpy.argmax(numpy.append(numpy.flip(rightDifferences[threeFourths:]) < -6, True))
        rightJump2Pillar = numpy.argmax(numpy.append(numpy.flip(rightDifferences[threeFourths:]) > 6, True))
        slam.carDirectionGuesses += 1
        if (leftJumpPillar > leftJump):
            slam.carDirectionGuess += leftJump
        else:
            slam.carDirectionGuess += threeFourths
        if (rightJumpPillar > rightJump):
            slam.carDirectionGuess -= rightJump
        else:
            slam.carDirectionGuess -= threeFourths
        if (leftJump2Pillar > leftJump2):
            slam.carDirectionGuess -= leftJump2
        else:
            slam.carDirectionGuess -= oneFourths
        if (rightJump2Pillar > rightJump2):
            slam.carDirectionGuess += rightJump2
        else:
            slam.carDirectionGuess += oneFourths
        if slam.carDirectionGuess > 0:
            slam.carDirection = 1
        else:
            slam.carDirection = -1
        # print(leftJump + rightJump2, rightJump + leftJump2)
        # slam.findStartingPosition(leftHeights, rightHeights)
    
    processedWalls = []

    centerWalls = 0
    leftWalls = 0
    rightWalls = 0
    
    centerWallDistance = 0
    leftWallDistance = 0
    rightWallDistance = 0

    centerWallAngle = 0
    leftWallAngle = 0
    rightWallAngle = 0

    carAngle = 0
    # drCarX = slam.carX + math.cos(slam.carAngle) * slam.carSpeed
    # drCarY = slam.carY + math.sin(slam.carAngle) * slam.carSpeed

    UNKNOWN = -1
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    BACK = 3

    sin = math.sin(slam.carAngle)
    cos = math.cos(slam.carAngle)

    for wall in walls:

        x1 = wall[0][X]
        y1 = wall[0][Y]
        x2 = wall[1][X]
        y2 = wall[1][Y]

        wall.append([0, 0])
        wall.append([0, 0])

        wall[2][X] = x1 * cos + y1 * sin
        wall[2][Y] = x1 * -sin + y1 * cos
        wall[3][X] = x2 * cos + y2 * sin
        wall[3][Y] = x2 * -sin + y2 * cos

        wallType = 0
        
        if wall[2][X] - wall[3][X] != 0 and wall[2][Y] - wall[3][Y] != 0:
            slope = (wall[2][Y] - wall[3][Y]) / (wall[2][X] - wall[3][X])
            yIntercept = -wall[2][Y] + slope * wall[2][X]
            
            distance = abs(yIntercept) / math.sqrt(slope**2 + 1)
            angle = math.atan2(slope, 1)

            if abs(angle) < 45 / 180 * math.pi and wall[2][Y] - wall[2][X] * slope > 10:
                wallType = CENTER
            elif abs(angle) < 45 / 180 * math.pi and wall[2][Y] - wall[2][X] * slope < -10:
                wallType = BACK
            else:
                if abs(angle) < 30 / 180 * math.pi:
                    wallType = UNKNOWN - 1
                elif wall[2][X] - wall[2][Y] / slope < 0:
                    wallType = LEFT
                else:
                    wallType = RIGHT
        elif wall[2][Y] - wall[3][Y] != 0:
            # vertical wall
            distance = abs(wall[2][X])
            if wall[2][X] > 0 and wall[3][X] > 0:
                wallType = RIGHT
                angle = math.pi / 2
            elif wall[2][X] < 0 and wall[3][X] < 0:
                wallType = LEFT
                angle = -math.pi / 2
            else:
                wallType = UNKNOWN
        else:
            #horizontal wall
            distance = abs(wall[2][Y])
            angle = 0
            wallType = CENTER

        angle += slam.carAngle
        
        if distance > 200:
            processedWalls.append([UNKNOWN, distance, angle])
            continue
        if abs(wall[2][X]) > 100 and abs(wall[3][X]) > 100 and abs(wall[2][Y]) < 50 and abs(wall[3][Y]) < 50:
            processedWalls.append([UNKNOWN, distance, angle])
            continue
        
        if wallType == CENTER:
            centerWalls += 1
            centerWallDistance += distance
            centerWallAngle += angle
            carAngle += angle
        elif wallType == LEFT:
            leftWalls += 1
            leftWallDistance += distance
            newAngle = angle + math.pi / 2
            if newAngle > math.pi / 2:
                newAngle -= math.pi
            leftWallAngle += newAngle
            carAngle += newAngle
        elif wallType == RIGHT:
            rightWalls += 1
            rightWallDistance += distance
            newAngle = angle + math.pi / 2
            if newAngle > math.pi / 2:
                newAngle -= math.pi
            rightWallAngle += newAngle
            carAngle += newAngle
        
        processedWalls.append([wallType, distance, angle])
        
    if centerWalls != 0:
        centerWallDistance /= centerWalls
        centerWallAngle /= centerWalls
    if leftWalls != 0:
        leftWallDistance /= leftWalls
        leftWallAngle /= leftWalls
    if rightWalls != 0:
        rightWallDistance /= rightWalls
        rightWallAngle /= rightWalls
    
    if centerWalls + leftWalls + rightWalls != 0:
        carAngle /= centerWalls + leftWalls + rightWalls
    d = 0.5
    slam.carAngle = d * carAngle + slam.carAngle * (1 - d)

    maxContourDistance = 200
    
    pillar = [None]
    if not NO_PILLARS:
        for contour in rContours:
            if contour[2] < maxContourDistance and (pillar[0] == None or contour[2] < pillar[2]):
                if pillar[0] != None and pillar[4] == RED_PILLAR and math.sqrt((pillar[0] - contour[0])**2 + (pillar[1] - contour[1])**2) < 40:
                    pillar[0] = (pillar[0] + contour[0]) / 2
                    pillar[1] = (pillar[1] + contour[1]) / 2
                else:
                    pillar = contour
                    pillar.append(RED_PILLAR)
        for contour in gContours:
            if contour[2] < maxContourDistance and (pillar[0] == None or contour[2] < pillar[2]):
                if pillar[0] != None and pillar[4] == GREEN_PILLAR and math.sqrt((pillar[0] - contour[0])**2 + (pillar[1] - contour[1])**2) < 40:
                    pillar[0] = (pillar[0] + contour[0]) / 2
                    pillar[1] = (pillar[1] + contour[1]) / 2
                else:
                    pillar = contour
                    pillar.append(GREEN_PILLAR)
    
    steering = 0
    throttle = None

    waypointX = 0
    waypointY = 0
    
    slam.carSectionsTimer -= 1
    if slam.carSectionsTimer < 0:
        slam.carSectionsTimer = 0
    slam.carSectionsCooldown -= 1

    carAngleSteering = 40

    def steerCenter():
        nonlocal steering
        if slam.carDirection == CLOCKWISE and rightWalls > 0 and rightWallDistance < 35:
            steering = -carAngleSteering - rightWallAngle * 40
        elif slam.carDirection == COUNTER_CLOCKWISE and leftWalls > 0 and leftWallDistance < 35:
            steering = carAngleSteering - leftWallAngle * 40
        else:
            steering = 100 * slam.carDirection
    def steerPillar():
        nonlocal steering, waypointX, waypointY, carAngleSteering
        
        pillarDirection = 1
        if pillar[4] == GREEN_PILLAR:
            pillarDirection = -1
        if pillar[0] * pillarDirection > -15:
            if pillar[1] > 10:
                waypointX = pillar[0] + 15 * pillarDirection
                waypointY = pillar[1] - 10
                steering = math.atan2(waypointX, waypointY) * 100
            else:
                steering = 40 * pillarDirection
        else:
            steering = -carAngle * carAngleSteering

    slam.carSectionsEnd -= 1
    if (centerWalls != 0 and centerWallDistance < 110):
        if slam.carSectionsCooldown <= 0 and slam.carSectionsExited <= 0:
            slam.carSectionsTimer += 2
            if slam.carSectionsTimer > 3:
                slam.carSections += 1
                slam.carSectionsCooldown = 3000
                slam.carSectionsExited = 3
                if slam.uTurnPillar == RED_PILLAR:
                    print("UTURN ! ! ! ! ! ! ! !")
                    if slam.uTurning == False:
                        slam.uTurnStage = 0
                        slam.uTurnGyroAngle = io.imu.angle() - carAngle
                        if slam.carDirection == CLOCKWISE:
                            slam.uTurnWallDistance = leftWallDistance
                        else:
                            slam.uTurnWallDistance = rightWallDistance
                    slam.uTurning = True
    if centerWalls == 0 or centerWallDistance > 200:
        slam.carSectionsExited -= 1
        if slam.carSectionsExited == 0:
            slam.carSectionsCooldown = 20
    
    if slam.carSectionsExited > 0 and slam.carAngle * slam.carDirection > 60 / 180 * math.pi:
        slam.carAngle -= slam.carDirection * math.pi / 2
    
    if slam.carSections == 12 and slam.carSectionsExited <= 0 and (centerWalls != 0 or (NO_PILLARS and slam.carSectionsCooldown <= 14)):
        io.drive.steer(0)
        io.drive.throttle(0)
        return False
    
    if slam.carSections == 7 and (slam.carSectionsCooldown > 0 or slam.carSectionsExited <= 0) and pillar[0] != None and pillar[2] < 40:
        slam.uTurnPillar = pillar[4]
    if slam.carSections > 7:
        slam.uTurnPillar = 0
    
    if slam.uTurning:
        print("oof no u turn code")
    if centerWalls != 0 and centerWallDistance < 100:
        if pillar[0] == None:
            if NO_PILLARS:
                if centerWallDistance < 75:
                    steerCenter()
            else:
                if centerWallDistance < 70:
                    steerCenter()
        elif pillar[4] == RED_PILLAR:
            if pillar[1] < 50 + 25 * slam.carDirection:
                steerCenter()
            elif centerWallDistance < 35:
                steerCenter()
        elif pillar[4] == GREEN_PILLAR:
            if pillar[1] < 50 - 25 * slam.carDirection:
                steerCenter()
            elif centerWallDistance < 35:
                steerCenter()
        if steering == 0:
            if pillar[0] == None:
                steering = -carAngle * carAngleSteering
            # elif slam.carDirection == CLOCKWISE and pillar[4] == GREEN_PILLAR and pillar[0] * slam.carDirection < 40:
            #     steering = -75 * slam.carDirection - carAngle * 40
            # elif slam.carDirection == COUNTER_CLOCKWISE and pillar[4] == RED_PILLAR and pillar[0] * slam.carDirection < 40:
            #     steering = -75 * slam.carDirection - carAngle * 40
    else:
        if pillar[0] == None or pillar[1] < 0:
            if leftWalls != 0 and rightWalls != 0:
                steering = (rightWallDistance - leftWallDistance) / (rightWallDistance + leftWallDistance) * 50 - carAngle * 80
            elif leftWalls != 0 and leftWallDistance < 15:
                steering = 50 - carAngle * carAngleSteering
            elif rightWalls != 0 and rightWallDistance < 15:
                steering = -50 - carAngle * carAngleSteering
            else:
                steering = -carAngle * carAngleSteering
        else:
            steerPillar()
    

    # print("driving: ", time.perf_counter() - start)
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
            'heights': [leftHeights.tolist(), rightHeights.tolist(), leftWallStarts.tolist(), rightWallStarts.tolist()],
            'pos': [150, 150,  slam.carAngle],
            'landmarks': slam.storedLandmarks,
            'rawLandmarks': [rContours, gContours, walls],
            'contours': [[rLeftContours, gLeftContours], [rRightContours, gRightContours]],
            'wallLines': [numpy.array(rawLeftWalls, dtype="int").tolist(), numpy.array(rawRightWalls, dtype="int").tolist()],
            'walls': [corners, walls, processedWalls],
            'steering': steering,
            'waypoints': [[], [waypointX, waypointY], 1],
            'raw': ["Center", centerWallDistance, "Left", leftWallDistance, "Right", rightWallDistance, "Angle", slam.carAngle / math.pi * 180, carAngle / math.pi * 180, "Direction", int(slam.carDirectionGuess)]
            # 'raw': [steering, centerWallDistance, leftWallDistance, rightWallDistance, slam.carDirection, slam.uTurnPillar, slam.uTurnStage, int(slam.carSections), carAngle]
        }
        server.emit('data', data)
    # print("sendserver: ", time.perf_counter() - start)
    
    if manual:
        return True
    io.drive.steer(steering)
    if throttle is not None:
        io.drive.throttle(throttle)

    # print("total: ", time.perf_counter() - totalStart)
    # for points in leftWalls:
    #     x1,y1,x2,y2=points
    #     cv2.line(leftEdgesImg,(x1,y1),(x2,y2),125,2)
    
    # print(leftWalls)

    # return leftEdgesImg
    return True

def getDistance(a, b):
    try:
        return math.sqrt(math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2))
    except Exception as e:
        print(e, a, b)

    
def transformCorner(corner):
    corner = list(corner)
    corner[X] = math.sin(-slam.carAngle) * corner[X] + math.cos(-slam.carAngle) * corner[Y]
    corner[Y] = math.cos(-slam.carAngle) * corner[X] + math.sin(-slam.carAngle) * corner[Y]
    return corner