from IO import io
from Util import server
from Controller import converter
from Controller import slam
import math
import cv2
import base64
import numpy
import time

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

    leftHeights, rightHeights = converter.getRawHeights(leftEdgesImg, rightEdgesImg)
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

    if slam.carDirection == NO_DIRECTION:
        leftDifferences = numpy.append(numpy.diff(leftHeights), -4)
        rightDifferences = numpy.append(numpy.diff(numpy.flip(rightHeights)), -4)
        leftJump = numpy.argmax(leftDifferences[leftDifferences < -3])
        rightJump = numpy.argmax(rightDifferences[rightDifferences < -3])
        if leftJump < rightJump:
            slam.carDirection = COUNTER_CLOCKWISE
        else:
            slam.carDirection = CLOCKWISE
        # slam.findStartingPosition(leftHeights, rightHeights)
    
    processedWalls = []

    centerWalls = 0
    leftWalls = 0
    rightWalls = 0
    
    centerWallDistance = 0
    leftWallDistance = 0
    rightWallDistance = 0

    carAngle = 0

    for wall in walls:
        UNKNOWN = -1
        LEFT = 0
        CENTER = 1
        RIGHT = 2
        wallType = 0
        
        if wall[0][X] - wall[1][X] != 0 and wall[0][Y] - wall[1][Y] != 0:
            slope = (wall[0][Y] - wall[1][Y]) / (wall[0][X] - wall[1][X])
            yIntercept = -wall[0][Y] + slope * wall[0][X]
            
            distance = abs(yIntercept) / math.sqrt(slope**2 + 1)
            angle = math.atan2(-slope, 1)

            if slope < 1 + 0.25 * slam.carDirection and slope > -1 + 0.25 * slam.carDirection and wall[0][Y] - wall[0][X] * slope > 0:
                wallType = CENTER
            else:
                if wall[0][X] - wall[0][Y] / slope < 0:
                    wallType = LEFT
                else:
                    wallType = RIGHT
                # if slope > 0:
                #     wallType = LEFT
                # else:
                #     wallType = RIGHT
                # if wall[0][X] > 0 and wall[1][X] > 0:
                #     wallType = RIGHT
                # elif wall[0][X] < 0 and wall[1][X] < 0:
                #     wallType = LEFT
                # else:
                    # wallType = UNKNOWN
        elif wall[0][Y] - wall[1][Y] != 0:
            # vertical wall
            distance = abs(wall[0][X])
            if wall[0][X] > 0 and wall[1][X] > 0:
                wallType = RIGHT
                angle = math.pi / 2
            elif wall[0][X] < 0 and wall[1][X] < 0:
                wallType = LEFT
                angle = -math.pi / 2
            else:
                wallType = UNKNOWN
        else:
            #horizontal wall
            distance = abs(wall[0][Y])
            angle = 0
            wallType = CENTER
        
        if wallType == CENTER:
            centerWalls += 1
            centerWallDistance += distance
            carAngle += angle
        elif wallType == LEFT:
            leftWalls += 1
            leftWallDistance += distance
            # carAngle += angle + math.pi / 2
        elif wallType == RIGHT:
            rightWalls += 1
            rightWallDistance += distance
            # carAngle += angle - math.pi / 2
        
        processedWalls.append([wallType, distance, angle])
        
    if centerWalls != 0:
        centerWallDistance /= centerWalls
        carAngle /= centerWalls
    if leftWalls != 0:
        leftWallDistance /= leftWalls
    if rightWalls != 0:
        rightWallDistance /= rightWalls
    
    # if centerWalls + leftWalls + rightWalls != 0:
    #     carAngle /= centerWalls + leftWalls + rightWalls

    maxContourDistance = 200
    
    pillar = [None]
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

    waypointX = 0
    waypointY = 0
    
    slam.carSectionsCooldown -= 1
    
    if centerWalls != 0 and centerWallDistance < 110:
        print("Corner SECTION")
        if slam.uTurnPillar != 0:
            slam.carDirection *= -1
            slam.carSections = 0
        if centerWallDistance < 60 and slam.carSectionsCooldown <= 0:
            slam.carSections += 1
            slam.carSectionsCooldown = 15
        if pillar[0] == None:
            if centerWallDistance < 70:
                steering = 100 * slam.carDirection
        elif pillar[4] == RED_PILLAR:
            # if centerWallDistance < 120:
            if pillar[1] < 50:
                steering = 100 * slam.carDirection
        elif pillar[4] == GREEN_PILLAR:
            if pillar[1] < 20:
                steering = 100 * slam.carDirection
        if steering == 0:
            if pillar[0] == None:
                steering = -carAngle * 40
            elif pillar[4] == GREEN_PILLAR and pillar[0] * slam.carDirection < 40:
                steering = -50 * slam.carDirection - carAngle * 40
    else:
        if slam.carSections == 12 and slam.carSectionsCooldown <= 0:
            io.drive.steer(0)
            io.drive.throttle(0)
            return False
        elif slam.carSections == 8 and slam.carSectionsCooldown <= 0 and pillar[0] != None:
            slam.uTurnPillar = pillar[4]
        # if leftWalls != 0 and rightWalls != 0:
        #     total = leftWallDistance + rightWallDistance
        #     if total > 80 / math.cos(carAngle):
        #         leftWallDistance += (100 / math.cos(carAngle) - total) / 2
        #         rightWallDistance += (100 / math.cos(carAngle) - total) / 2
        #     else:
        #         leftWallDistance += (60 / math.cos(carAngle) - total) / 2
        #         rightWallDistance += (60 / math.cos(carAngle) - total) / 2
        if pillar[0] == None:
            if leftWalls != 0 and rightWalls != 0:
                steering = (rightWallDistance - leftWallDistance) / (rightWallDistance + leftWallDistance) * 100 - carAngle * 80
            elif leftWalls != 0 and leftWallDistance < 20:
                steering = 100
            elif rightWalls != 0 and rightWallDistance < 20:
                steering = -100
            else:
                steering = -carAngle * 40
        else:
            pillarDirection = 1
            if pillar[4] == GREEN_PILLAR:
                pillarDirection = -1
            tangentX = pillar[X] + pillar[Y] / pillar[2] * 20 * pillarDirection
            tangentY = pillar[Y] - pillar[X] / pillar[2] * 20 * pillarDirection
            # xDistance = 0
            # yDistance = pillar[Y] - 15
            # xDistance = pillar[X]
            # if pillar[4] == RED_PILLAR:
            #     xDistance += 15
            # else:
            #     xDistance -= 15
            # if leftWalls != 0 and rightWalls != 0:
            #     if pillar[4] == RED_PILLAR:
            #         xDistance = (pillar[X] + rightWallDistance) / 2
            #     else:
            #         xDistance = (pillar[X] - leftWallDistance) / 2
            # elif leftWalls != 0 and pillar[4] == GREEN_PILLAR:
            #     xDistance = (pillar[X] - leftWallDistance) / 2
            # elif rightWalls != 0 and pillar[4] == RED_PILLAR:
            #     xDistance = (pillar[X] + rightWallDistance) / 2
            # else:
            #     xDistance = pillar[X]
            #     if pillar[4] == RED_PILLAR:
            #         xDistance += 10
            #     else:
            #         xDistance -= 10
            waypointX = tangentX
            waypointY = tangentY
            steering = math.atan2(tangentX, tangentY) * 180
            if pillar[4] == RED_PILLAR:
                steering += 15
            else:
                steering -= 15
            if steering > 0 and rightWalls > 0 and rightWallDistance < 20:
                steering = 0
            if steering < 0 and leftWalls > 0 and leftWallDistance < 20:
                steering = 0

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
            'heights': [leftHeights.tolist(), rightHeights.tolist()],
            'pos': [slam.carX, slam.carY, slam.carAngle],
            'landmarks': slam.storedLandmarks,
            'rawLandmarks': [rContours, gContours, walls],
            'contours': [[rLeftContours, gLeftContours], [rRightContours, gRightContours]],
            'wallLines': [numpy.array(rawLeftWalls, dtype="int").tolist(), numpy.array(rawRightWalls, dtype="int").tolist()],
            'walls': [corners, walls, processedWalls],
            'steering': steering,
            'waypoints': [[], [waypointX, waypointY], 1],
            'raw': [steering, centerWallDistance, leftWallDistance, rightWallDistance, int(slam.carSections), carAngle]
        }
        server.emit('data', data)
    # print("sendserver: ", time.perf_counter() - start)
    
    io.drive.steer(steering)

    print("total: ", time.perf_counter() - totalStart)
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