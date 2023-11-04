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

RIGHT_ON_RED = False
if RIGHT_ON_RED:
    print("[!] [!] [!] [!] Right on red mode is on! [!] [!] [!] [!]") # oh noes right on red is on

UTURN_ON_GREEN = False
UTURN_PILLAR = RED_PILLAR
if UTURN_ON_GREEN:
    UTURN_PILLAR = GREEN_PILLAR
    print("[!] [!] [!] [!] Uturn on green mode is on! [!] [!] [!] [!]") # oh noes uturn on green is on

THROW_OUT_SMALL_WALLS = False

# speed !!!!
speed = 75
speed = 80
# speed = 90
# speed = 100
lastSteering = 0

meter = 1
second = 1

MAX_SPEED = 299792458 * meter / second
if (speed > MAX_SPEED):
    print("ERROR !!!!! SPEED EXCEEDS MAX SPEED !!! BUG FIX NOW")

# slam.carSections = 4

useServer = True
def setMode(sendServer: bool = None):
    global useServer
    if sendServer != None: useServer = sendServer

def drive(manual: bool = False):
    global lastSteering
    read = io.camera.read()

    # Filter and undistort
    leftEdgesImg, gLeftImg, rLeftImg = converter.filter(converter.undistort(read[0]))
    rightEdgesImg, gRightImg, rRightImg = converter.filter(converter.undistort(read[1]))

    # Get contours
    rLeftContours = converter.getContours(rLeftImg)
    gLeftContours = converter.getContours(gLeftImg)
    rRightContours = converter.getContours(rRightImg)
    gRightContours = converter.getContours(gRightImg)

    # Get wall heights
    leftHeights, rightHeights, leftWallStarts, rightWallStarts = converter.getRawHeights(leftEdgesImg, rightEdgesImg)

    rawLeftWalls = converter.getWalls(leftHeights.copy(), rLeftContours, gLeftContours)
    rawRightWalls = converter.getWalls(rightHeights.copy(), rRightContours, gRightContours)

    rContours = converter.mergeContours(rLeftContours, rRightContours, leftHeights, rightHeights)
    gContours = converter.mergeContours(gLeftContours, gRightContours, leftHeights, rightHeights)

    corners, walls = converter.processWalls(rawLeftWalls, rawRightWalls)

    leftJump = 0
    leftJumpPillar = 0
    rightJump = 0
    rightJumpPillar = 0
    leftJump2 = 0
    leftJump2Pillar = 0
    rightJump2 = 0
    rightJump2Pillar = 0

    if slam.carDirectionGuesses < 9:
        #majority vote
        oneFourths = int((converter.imageWidth - 3) / 4)
        threeFourths = int((converter.imageWidth - 3) * 3 / 4)
        leftDifferences = numpy.diff(leftHeights)
        rightDifferences = numpy.diff(numpy.flip(rightHeights))
        leftDifferences2 = leftDifferences + numpy.r_[leftDifferences[1:],leftDifferences[0]]
        rightDifferences2 = rightDifferences + numpy.r_[rightDifferences[1:],rightDifferences[0]]
        leftJump = numpy.argmax(numpy.append(leftDifferences2[:threeFourths] < -7, True))
        leftJumpPillar = numpy.argmax(numpy.append(leftDifferences2[:threeFourths] > 7, True))
        rightJump = numpy.argmax(numpy.append(rightDifferences2[:threeFourths] < -7, True))
        rightJumpPillar = numpy.argmax(numpy.append(rightDifferences2[:threeFourths] > 7, True))
        leftJump2 = numpy.argmax(numpy.append(numpy.flip(leftDifferences2[threeFourths:]) < -7, True))
        leftJump2Pillar = numpy.argmax(numpy.append(numpy.flip(leftDifferences2[threeFourths:]) > 7, True))
        rightJump2 = numpy.argmax(numpy.append(numpy.flip(rightDifferences2[threeFourths:]) < -7, True))
        rightJump2Pillar = numpy.argmax(numpy.append(numpy.flip(rightDifferences2[threeFourths:]) > 7, True))
        slam.carDirectionGuesses += 1
        carDirectionGuess = 0
        if (leftJumpPillar - 5 > leftJump):
            carDirectionGuess += leftJump
        else:
            carDirectionGuess += threeFourths
        if (rightJumpPillar - 5 > rightJump):
            carDirectionGuess -= rightJump
        else:
            carDirectionGuess -= threeFourths
        if (leftJump2Pillar - 5 > leftJump2):
            carDirectionGuess -= leftJump2
        else:
            carDirectionGuess -= oneFourths
        if (rightJump2Pillar - 5 > rightJump2):
            carDirectionGuess += rightJump2
        else:
            carDirectionGuess += oneFourths
        if carDirectionGuess > 0:
            slam.carDirectionGuess += 1
        elif carDirectionGuess < 0:
            slam.carDirectionGuess += -1
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

    def processWalls():
        nonlocal processedWalls, centerWalls, leftWalls, rightWalls, centerWallDistance, leftWallDistance, rightWallDistance, centerWallAngle, leftWallAngle, rightWallAngle, carAngle, walls

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
        sin = math.sin(slam.carAngle)
        cos = math.cos(slam.carAngle)

        UNKNOWN = -1
        LEFT = 0
        CENTER = 1
        RIGHT = 2
        BACK = 3
        
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

                if abs(angle) < 30 / 180 * math.pi and wall[2][Y] - wall[2][X] * slope > 10:
                    if abs(wall[2][X]) > 80 and abs(wall[3][X]) > 80 and abs(wall[2][X] + wall[3][X]) > 160:
                        wallType = UNKNOWN
                    else:
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
            
            if distance > 200:
                processedWalls.append([UNKNOWN, distance, angle])
                continue
            if abs(wall[2][X]) > 100 and abs(wall[3][X]) > 100 and abs(wall[2][Y]) < 50 and abs(wall[3][Y]) < 50:
                processedWalls.append([UNKNOWN, distance, angle])
                continue
            if pow(wall[2][X] - wall[3][X], 2) + pow(wall[2][Y] - wall[3][Y], 2) < 64 and (wallType != LEFT + slam.carDirection + 1 or THROW_OUT_SMALL_WALLS):
                processedWalls.append([UNKNOWN, distance, angle])
                continue
            if pow(wall[2][X], 2) + pow(wall[2][Y], 2) > 150 * 150 and pow(wall[3][X], 2) + pow(wall[3][Y], 2) > 150 * 150:
                processedWalls.append([UNKNOWN, distance, angle])
                continue

            if wallType == LEFT:
                angle = angle + math.pi / 2
                if angle > math.pi / 2:
                    angle -= math.pi
            elif wallType == RIGHT:
                angle = angle + math.pi / 2
                if angle > math.pi / 2:
                    angle -= math.pi
            
            if abs(angle) > 45 / 180 * math.pi:
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
                leftWallAngle += angle
                carAngle += angle
            elif wallType == RIGHT:
                rightWalls += 1
                rightWallDistance += distance
                rightWallAngle += angle
                carAngle += angle
            
            processedWalls.append([wallType, distance, angle])
            
        if centerWalls != 0:
            centerWallDistance /= centerWalls
            centerWallAngle /= centerWalls
            centerWallAngle += slam.carAngle
        if leftWalls != 0:
            leftWallDistance /= leftWalls
            leftWallAngle /= leftWalls
            leftWallAngle += slam.carAngle
        if rightWalls != 0:
            rightWallDistance /= rightWalls
            rightWallAngle /= rightWalls
            rightWallAngle += slam.carAngle
    
        if centerWalls + leftWalls + rightWalls != 0:
            carAngle /= centerWalls + leftWalls + rightWalls
            carAngle += slam.carAngle
    processWalls()
    d = 0.75
    if (carAngle != 0):
        slam.carAngle = d * carAngle + slam.carAngle * (1 - d)
    # if carAngle > slam.carAngle and lastSteering > 0:
    #     slam.carAngle = d * carAngle + slam.carAngle * (1 - d)
    # elif carAngle < slam.carAngle and lastSteering < 0:
    #     slam.carAngle = d * carAngle + slam.carAngle * (1 - d)
    # else:
    #     slam.carAngle = d / 2 * carAngle + slam.carAngle * (1 - d / 2)

    maxContourDistance = 170
    
    pillar = [None, None]
    if not NO_PILLARS:
        for contour in rContours:
            if contour[2] < maxContourDistance:
                if pillar[0] != None and pillar[4] == RED_PILLAR and math.sqrt((pillar[0] - contour[0])**2 + (pillar[1] - contour[1])**2) < 40:
                    pillar[0] = (pillar[0] + contour[0]) / 2
                    pillar[1] = (pillar[1] + contour[1]) / 2
                elif pillar[0] == None or contour[2] < pillar[2]:
                    pillar = contour[:]
                    pillar.append(RED_PILLAR)
        for contour in gContours:
            if contour[2] < maxContourDistance:
                if pillar[0] != None and pillar[4] == GREEN_PILLAR and math.sqrt((pillar[0] - contour[0])**2 + (pillar[1] - contour[1])**2) < 40:
                    pillar[0] = (pillar[0] + contour[0]) / 2
                    pillar[1] = (pillar[1] + contour[1]) / 2
                elif pillar[0] == None or contour[2] < pillar[2]:
                    pillar = contour[:]
                    pillar.append(GREEN_PILLAR)
    
    if pillar[0] == None:
        if slam.lastPillar[0] != None:
            pillar = slam.lastPillar[:]
        slam.lastPillar = [None]
    else:
        slam.lastPillar = pillar[:]
    
    transformedPillar = pillar[:]

    sin = math.sin(slam.carAngle)
    cos = math.cos(slam.carAngle)
    if (pillar[0] != None):
        transformedPillar[X] = pillar[X] * cos + pillar[Y] * sin
        transformedPillar[Y] = pillar[X] * -sin + pillar[Y] * cos
    
    steering = 0
    throttle = None

    waypointX = 0
    waypointY = 0
    
    slam.carSectionTimer -= 1
    if slam.carSectionTimer < 0:
        slam.carSectionTimer = 0
    slam.carSectionCooldown -= 1

    carAngleSteering = 130
    carAngleSteering -= 30
    if slam.uTurnPillar == UTURN_PILLAR:
        carAngleSteering /= 2
    
    reason = ""

    def steerAwayFromWalls():
        nonlocal steering, carAngleSteering, reason
        if leftWalls != 0 and leftWallDistance < 40 and leftWallAngle < 10 / 180 * math.pi:
            steering = max(steering, 60 - leftWallDistance - leftWallAngle * 180 / math.pi * 2)
        elif leftWalls == 0 and rightWalls != 0 and rightWallDistance > 80 and slam.carAngle < 10 / 180 * math.pi:
            steering = max(steering, rightWallDistance - 40)
        elif rightWalls != 0 and rightWallDistance < 40 and rightWallAngle > -10 / 180 * math.pi:
            steering = min(steering, -(60 - rightWallDistance) - rightWallAngle * 180 / math.pi * 2)
        elif rightWalls == 0 and leftWalls != 0 and leftWallDistance > 80 and slam.carAngle > -10 / 180 * math.pi:
            steering = min(steering, -(leftWallDistance - 40))
        reason += " away from walls"
    def steerNormal(awayFromWalls):
        nonlocal steering, carAngleSteering, reason
        steering += -slam.carAngle * carAngleSteering
        if slam.uTurnPillar == UTURN_PILLAR and ((slam.carSections == 7 and slam.carSectionExited == 1) or slam.carSections == 8):
            if slam.uTurnAroundPillar == GREEN_PILLAR and leftWalls != 0:
                steering += -(leftWallDistance - 30)
            elif slam.uTurnAroundPillar == RED_PILLAR and rightWalls != 0:
                steering += rightWallDistance - 30
        elif slam.uTurnPillar == UTURN_PILLAR and slam.carSections == 7 and slam.carSectionExited == 0:
            if slam.carDirection == CLOCKWISE and leftWalls != 0:
                steering += -(leftWallDistance - 30)
            elif slam.carDirection == COUNTER_CLOCKWISE and rightWalls != 0:
                steering += rightWallDistance - 30
        if awayFromWalls:
            steerAwayFromWalls()
        reason += " normal"
    def steerCenter():
        nonlocal steering, carAngleSteering, reason
        if slam.carDirection == CLOCKWISE and (rightWalls > 0 and rightWallDistance < 35):
            steering = -carAngleSteering - rightWallAngle * 40
        elif slam.carDirection == COUNTER_CLOCKWISE and (leftWalls > 0 and leftWallDistance < 35):
            steering = carAngleSteering - leftWallAngle * 40
        else:
            steering = 100 * slam.carDirection
            if slam.carSections == 7 and slam.uTurnPillar == UTURN_PILLAR:
                steering -= 10
        reason += " center"
    def steerPillar():
        nonlocal steering, waypointX, waypointY, carAngleSteering, reason
        
        pillarDirection = 1
        if transformedPillar[4] == GREEN_PILLAR:
            pillarDirection = -1
        
        if RIGHT_ON_RED:
            pillarDirection *= -1

        if transformedPillar[0] * pillarDirection > -15:
            if transformedPillar[1] > 15:
                waypointX = transformedPillar[0] + 20 * pillarDirection
                waypointY = transformedPillar[1] * 0.7
                # atan2 is X, Y
                # do not change
                steering = (math.atan2(waypointX, waypointY) - slam.carAngle) * 250
                if steering * pillarDirection < 0:
                    steering /= 2
                if transformedPillar[0] * pillarDirection > 30:
                    steering *= 2
                if centerWalls != 0 and centerWallDistance < 125:
                    steering *= 0.5
                if transformedPillar[2] < 30:
                    steering += -slam.carAngle * carAngleSteering / 2
            else:
                steering = 40 * pillarDirection
        else:
            steerNormal(False)
        if not (slam.carSections == 8 and slam.uTurnPillar == UTURN_PILLAR):
            if transformedPillar[0] * pillarDirection < -25:
                steerAwayFromWalls()
                steering *= 0.5
                if transformedPillar[0] * pillarDirection < -45:
                    steering *= 2
        reason += " pillar"
    def steerUTurn():
        nonlocal steering
        if slam.uTurnAroundPillar != 0:
            steering = 100 * slam.uTurnAroundPillar

    if (centerWalls != 0 and centerWallDistance < 130) and (not slam.uTurning):
        if slam.carSectionCooldown <= 0 and slam.carSectionExited <= 0:
            slam.carSectionTimer += 2
            if slam.carSectionTimer > 3:
                slam.carSectionEntered = 2
                slam.carSectionCooldown = 3000
                slam.carSectionExited = 6
                # if slam.carSections == 7 and slam.uTurnPillar == UTURN_PILLAR:
                #     slam.carSectionExited = 2
    if (centerWalls == 0 or centerWallDistance > 150) and slam.carSectionEntered == 1:
        slam.carSectionExited -= 1
        if slam.carSectionExited == 0 and (not slam.uTurning):
            if (slam.carSectionEntered == 1):
                slam.carSections += 1
                slam.carSectionEntered = 0
                if slam.carSections == 9:
                    slam.uTurnPillar = 0
            slam.carSectionEntered = 0
            slam.carSectionCooldown = 10
    
    if slam.carSectionEntered == 2 and carAngle != 0 and slam.carAngle * slam.carDirection > 40 / 180 * math.pi and (not slam.uTurning):
        slam.carAngle -= slam.carDirection * math.pi / 2
        # slam.carSections += 1
        slam.carSectionEntered = 1
        processWalls()
        reason += " turn 1"
    # elif slam.carSectionEntered == 2 and carAngle * slam.carDirection < -20 / 180 * math.pi and carAngle != 0 and ((slam.carAngle - carAngle) * slam.carDirection > 7 / 180 * math.pi or carAngle * slam.carDirection < -60 / 180 * math.pi) and (transformedPillar[0] == None or (((slam.carDirection == CLOCKWISE and transformedPillar[4] == RED_PILLAR) or (slam.carDirection == COUNTER_CLOCKWISE and transformedPillar[4] == GREEN_PILLAR)) and transformedPillar[2] < 50)) and (not slam.uTurning):
    #     slam.carSectionEntered = 1
    #     reason += " turn 2"
    
    inMiddleSection = slam.carSectionExited <= 0 and (centerWalls != 0 and centerWallDistance < 160)
    
    if slam.carSectionEntered == 2 and (centerWalls == 0 or centerWallDistance > 150):
        slam.carSectionExited -= 1
        if slam.carSectionExited == 0 and (not slam.uTurning):
            slam.carSections += 1
            slam.carSectionEntered = 0
            slam.carSectionCooldown = 10

    if slam.carSections == 12 and inMiddleSection:
        io.drive.steer(0)
        io.drive.throttle(0)
        return False
    
    if slam.carSections == 7 and transformedPillar[0] != None and transformedPillar[2] < 60 and transformedPillar[1] < 20:
        slam.uTurnPillar = transformedPillar[4]
    if (not slam.uTurning) and slam.uTurnStart <= 0 and slam.carSectionEntered == 0 and slam.carSectionCooldown > -3 and slam.carSections == 8 and transformedPillar[0] != None and transformedPillar[2] < 75:
        if transformedPillar[4] == RED_PILLAR:
            slam.uTurnAroundPillar = -1
            slam.uTurnPillar = RED_PILLAR
        else:
            slam.uTurnAroundPillar = 1
            slam.uTurnPillar = GREEN_PILLAR
    if slam.carSections > 8:
        slam.uTurnPillar = 0

    if slam.carSections == 8 and slam.uTurnPillar == UTURN_PILLAR and slam.carSectionCooldown > -7 and slam.carSectionEntered != 1 and ((transformedPillar[0] != None and transformedPillar[1] < 30)):
        if slam.uTurning == False and slam.uTurnStart <= 0:
            slam.uTurnStart = 7
    
    slam.uTurnStart -= 1

    if slam.uTurnStart == 0:
        print("UTURN ! ! ! ! ! ! ! !")
        slam.uTurnStage = 0
        slam.uTurnPillar = 0
        slam.uTurnGyroAngle = io.imu.angle() - carAngle
        if slam.carDirection == CLOCKWISE:
            slam.uTurnWallDistance = leftWallDistance
        else:
            slam.uTurnWallDistance = rightWallDistance
        slam.uTurning = True
    
    if slam.uTurning:
        slam.carAngle = 0
        if slam.uTurnAroundPillar == 0:
            if leftWalls != 0 and rightWalls != 0:
                if leftWallDistance < rightWallDistance:
                    slam.uTurnAroundPillar = 1
                else:
                    slam.uTurnAroundPillar = -1
        steerUTurn()
        if abs(slam.uTurnGyroAngle - io.imu.angle()) * 1.3 > math.pi:
            slam.uTurning = False
            slam.uTurnPillar = 0
            slam.uTurnStart = 20200202
            # slam.carAngle += math.pi
            slam.carDirection *= -1
            slam.carSectionCooldown = 10
            # slam.carSections += 1
            processWalls()
        # print("oof no u turn code")
    elif centerWalls != 0 and centerWallDistance < 120 and slam.carSectionEntered != 1:
        if transformedPillar[0] == None or abs(transformedPillar[0]) > 120:
            if slam.uTurnPillar == UTURN_PILLAR:
                if centerWallDistance < 65:
                    steerCenter()
            elif NO_PILLARS:
                if centerWallDistance < 75:
                    steerCenter()
            else:
                if centerWallDistance < 75:
                    steerCenter()
        elif ((not RIGHT_ON_RED) and transformedPillar[4] == RED_PILLAR) or (RIGHT_ON_RED and transformedPillar[4] == GREEN_PILLAR):
            if slam.uTurnPillar == UTURN_PILLAR:
                if slam.carDirection == CLOCKWISE:
                    steerCenter()
                elif slam.carDirection == COUNTER_CLOCKWISE:
                    if centerWallDistance < 65:
                        steerCenter()
            elif slam.carDirection == CLOCKWISE and transformedPillar[1] < 75 and centerWallDistance - transformedPillar[1] < 80:
                steerCenter()
            elif slam.carDirection == COUNTER_CLOCKWISE and transformedPillar[1] < 20 and centerWallDistance - transformedPillar[1] < 80:
                steerCenter()
            elif slam.carDirection == COUNTER_CLOCKWISE and transformedPillar[0] < -30:
                steering += 20
            elif centerWallDistance < 55:
                steerCenter() 
        elif ((not RIGHT_ON_RED) and transformedPillar[4] == GREEN_PILLAR) or (RIGHT_ON_RED and transformedPillar[4] == RED_PILLAR):
            if slam.uTurnPillar == UTURN_PILLAR:
                if slam.carDirection == COUNTER_CLOCKWISE:
                    steerCenter()
                elif slam.carDirection == CLOCKWISE:
                    if centerWallDistance < 65:
                        steerCenter()
            elif slam.carDirection == COUNTER_CLOCKWISE and transformedPillar[1] < 75 and centerWallDistance - transformedPillar[1] < 80:
                steerCenter()
            elif slam.carDirection == CLOCKWISE and transformedPillar[1] < 20 and centerWallDistance - transformedPillar[1] < 80:
                steerCenter()
            elif slam.carDirection == CLOCKWISE and -transformedPillar[0] < -30:
                steering -= 20
            elif centerWallDistance < 55:
                steerCenter()
        if steering == 0:
            if transformedPillar[0] == None:
                steering = -slam.carAngle * carAngleSteering
            else:
                steering = -slam.carAngle * carAngleSteering / 2
            # elif slam.carDirection == CLOCKWISE and transformedPillar[4] == GREEN_PILLAR and transformedPillar[0] * slam.carDirection < 40:
            #     steering = -75 * slam.carDirection - carAngle * 40
            # elif slam.carDirection == COUNTER_CLOCKWISE and transformedPillar[4] == RED_PILLAR and transformedPillar[0] * slam.carDirection < 40:
            #     steering = -75 * slam.carDirection - carAngle * 40
    else:
        if transformedPillar[0] == None or transformedPillar[1] < 10 or (leftWalls != 0 and transformedPillar[0] < -leftWallDistance + 23) or (rightWalls != 0 and transformedPillar[0] > rightWallDistance - 23) or abs(transformedPillar[0]) > 80 or (centerWalls > 0 and centerWallDistance - transformedPillar[1] < 90 and centerWallDistance > 130):
            # if leftWalls != 0 and rightWalls != 0:
            #     steering = (rightWallDistance - leftWallDistance) / (rightWallDistance + leftWallDistance) * 50 - carAngle * 80
            steerNormal(True)
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
            'heights': [leftHeights.tolist(), rightHeights.tolist(), leftWallStarts.tolist(), rightWallStarts.tolist()],
            'pos': [150, 150,  slam.carAngle],
            'landmarks': slam.storedLandmarks,
            'rawLandmarks': [rContours, gContours, walls],
            'contours': [[rLeftContours, gLeftContours], [rRightContours, gRightContours]],
            'wallLines': [numpy.array(rawLeftWalls, dtype="int").tolist(), numpy.array(rawRightWalls, dtype="int").tolist()],
            'walls': [corners, walls, processedWalls],
            'steering': steering,
            'waypoints': [[], [waypointX, waypointY], 1],
            'raw': [
                "steering", steering,
                "center dist", centerWallDistance,
                "left dist", leftWallDistance,
                "right dist", rightWallDistance,
                "angle", slam.carAngle / math.pi * 180,
                "raw angle", carAngle / math.pi * 180,
                "sections", int(slam.carSections),
                "sections cooldown", int(slam.carSectionCooldown),
                "section entered", int(slam.carSectionEntered),
                "section exited", int(slam.carSectionExited),
                "direction", int(slam.carDirectionGuess),
                "pillar", transformedPillar[0] != None,
                "pillarX", transformedPillar[0],
                "pillarY", transformedPillar[1],
                "steeringReason", reason,
                "U-turn pillar", slam.uTurnPillar,
                "U-turning", slam.uTurning,
                "U-turn-start", slam.uTurnStart,
                "U-pillaring", slam.uTurnAroundPillar,
                "L jump", int(leftJump),
                "L jump P", int(leftJumpPillar),
                "R jump", int(rightJump),
                "R jump P", int(rightJumpPillar),
                "L jump 2", int(leftJump2),
                "L jump 2 P", int(leftJump2Pillar),
                "R jump 2", int(rightJump2),
                "R jump 2 P", int(rightJump2Pillar)
            ]
        }
        server.emit('data', data)
    # print("sendserver: ", time.perf_counter() - start)
    
    if manual:
        return True
    io.drive.steer(steering)
    lastSteering = steering
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