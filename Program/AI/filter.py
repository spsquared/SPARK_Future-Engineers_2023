from IO import io
import numpy
import cv2
import base64
import statistics
import math
import json

# preprocessing filter module with cv prediction

# colors
rm = redMin = (0, 95, 75)
rM = redMax = (25, 255, 255)
gm = greenMin = (30, 20, 30)
gM = greenMax = (110, 255, 255)
bm = blueMin = (100, 70, 70)
bM = blueMax = (140, 255, 255)

# wall constants
LEFT = 0
CENTER = 1
RIGHT = 2

def filter(imgIn: numpy.ndarray, checkBlue: bool):
    global redMax, redMin, greenMax, greenMin, blueMax, blueMin
    try:
        # convert to HSV
        hsv = cv2.cvtColor(imgIn, cv2.COLOR_BGR2HSV)
        # red filter
        # red is at 0 and also 180, accounting for HSV wraparound
        rMask1 = cv2.inRange(hsv, redMin, redMax)
        redMaxH = redMax[0]
        redMinList = list(redMin)
        redMinList = [180 - redMaxH,redMinList[1],redMinList[2]]
        redMin2 = tuple(redMinList)
        redMaxList = list(redMax)
        redMaxList = [180,redMaxList[1],redMaxList[2]]
        redMax2 = tuple(redMaxList)
        rMask2 = cv2.inRange(hsv, redMin2, redMax2)
        rMask = cv2.bitwise_or(rMask1, rMask2)
        # green filter
        gMask = cv2.inRange(hsv, greenMin, greenMax)
        # blue filter
        bMask = cv2.inRange(hsv, blueMin, blueMax)
        # blur images to remove noise
        blurredR = cv2.medianBlur(rMask, 5)
        blurredG = cv2.medianBlur(gMask, 5)
        blurredB = cv2.medianBlur(bMask, 3)
        gray_image = cv2.cvtColor(imgIn, cv2.COLOR_RGB2GRAY)
        blurredImg = cv2.GaussianBlur(gray_image, (3,3),0)
        # edge detection
        edgesImage = cv2.Canny(blurredImg, 50, 125, 3)
        # combine images
        if checkBlue == True:
            filteredImg = cv2.merge((edgesImage, blurredG, blurredR, blurredB))
        else:
            filteredImg = cv2.merge((edgesImage, blurredG, blurredR))
        return filteredImg
    except Exception as err:
        print(err)
        io.error()

rightOnRed = True
doPillars = True
counterClockwise = 0
turnsMade = 0
turnCooldown = 40
passedPillar = 0
lastSend = 0

debug = False

def predict(imgIn: numpy.ndarray, server = None, infinite = False):
    global redMax, redMin, greenMax, greenMin, lastSend, rightOnRed, counterClockwise, turnsMade, turnCooldown, passedPillar, debug
    try:
        # useless thing
        if infinite: turnsMade = 0

        # create blob detector
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 65
        params.filterByCircularity = True
        params.minCircularity = 0.3
        params.filterByConvexity = True
        params.minConvexity = 0.7
        params.filterByInertia = True
        params.minInertiaRatio = 0
        blobs = cv2.SimpleBlobDetector_create(params)

        # filter to colors and split
        blurredImg = filter(imgIn,True)
        edgesImage, gImg, rImg, bImg = cv2.split(blurredImg)

        # send images to SPARK Control
        if server != None and blurredImg.all() != None:
            lastSend += 1
            if (lastSend > 2):
                lastSend = 0
                encoded = base64.b64encode(cv2.imencode('.png', cv2.merge((edgesImage, gImg, rImg)))[1]).decode()
                server.broadcast('capture', encoded)

        # steering reason
        steeringReason = ""

        ################# PILLAR STEERING #################


        # pillar steering
        pillarSteering = 0

        # crop for blob detection
        blobStart = 79
        blobEnd = 100

        # initial variables
        rKps = []
        gKps = []
        brKps = 0
        bgKps = 0

        if doPillars == True:
            # add borders to fix blob detection
            rImg = cv2.copyMakeBorder(rImg[blobStart:blobEnd],1,1,1,1, cv2.BORDER_CONSTANT, value=[0,0,0])
            gImg = cv2.copyMakeBorder(gImg[blobStart:blobEnd],1,1,1,1, cv2.BORDER_CONSTANT, value=[0,0,0])

            # detect blobs
            if rightOnRed == True:
                blobs.empty()
                rKps = blobs.detect(255 - rImg)
                blobs.empty()
                gKps = blobs.detect(255 - gImg)
            else:
                blobs.empty()
                rKps = blobs.detect(255 - gImg)
                blobs.empty()
                gKps = blobs.detect(255 - rImg)

            # pillar calculations
            blobSizeRequirement = 0
            dangerSize = 50
            def getRedEquation(x):
                return x * -0.315 + 121 - dangerSize
            def getGreenEquation(x):
                return (272 - x) * -0.315 + 121 - dangerSize

            # find pillars that will collide with car
            for i in range(len(rKps)):
                rKps[i].size /= 2
                position = list(rKps[i].pt)
                position[1] += blobStart
                rKps[i].pt = tuple(position)
                # get largest red pillar
                if rKps[i].pt[1] + rKps[i].size > getRedEquation(rKps[i].pt[0]) and rKps[i].pt[1] + rKps[i].size > 70 and rKps[i].size > blobSizeRequirement:
                    if brKps == 0:
                        brKps = rKps[i]
                    elif brKps.size < rKps[i].size:
                        brKps = rKps[i]
            for i in range(len(gKps)):
                gKps[i].size /= 2
                position = list(gKps[i].pt)
                position[1] += blobStart
                gKps[i].pt = tuple(position)
                # get largest green pillar
                if gKps[i].pt[1] + gKps[i].size > getGreenEquation(gKps[i].pt[0]) and gKps[i].pt[1] + gKps[i].size > 70 and gKps[i].size > blobSizeRequirement:
                    if bgKps == 0:
                        bgKps = gKps[i]
                    elif bgKps.size < gKps[i].size:
                        bgKps = gKps[i]

            # decide steering for each signal that will collide
            reducedSteering = 35
            if brKps != 0:
                if bgKps != 0:
                    if brKps.size > bgKps.size:
                        pillarSteering = -(getRedEquation(brKps.pt[0]) - brKps.pt[1] - brKps.size * 2 - reducedSteering) * (brKps.size - 3) ** 2 * 0.045
                        steeringReason += "red pillar "
                    else:
                        pillarSteering = (getGreenEquation(bgKps.pt[0]) - bgKps.pt[1] - bgKps.size * 2 - reducedSteering) * (bgKps.size - 3) ** 2 * 0.045
                        steeringReason += "green pillar "
                else:
                    pillarSteering = -(getRedEquation(brKps.pt[0]) - brKps.pt[1] - brKps.size * 2 - reducedSteering) * (brKps.size - 3) ** 2 * 0.045
                    steeringReason += "red pillar "
            elif bgKps != 0:
                pillarSteering = (getGreenEquation(bgKps.pt[0]) - bgKps.pt[1] - bgKps.size * 2 - reducedSteering) * (bgKps.size - 3) ** 2 * 0.045
                steeringReason += "green pillar "
            if pillarSteering > 500:
                pillarSteering = 500
            elif pillarSteering < -500:
                pillarSteering = -500
            # passedPillar += (pillarSteering - passedPillar) * 0.1
            passedPillar *= 0.9
            if pillarSteering != 0:
                pillarSteering += passedPillar * 0.9
                if abs(passedPillar) < 50:
                    passedPillar = pillarSteering
            else:
                pillarSteering = passedPillar

        ################# WALL STEERING #################

        # crop for wall detection
        wallStart = 79
        wallEnd = 125
        croppedEdgesImg = numpy.concatenate((edgesImage[wallStart:wallEnd], numpy.full((2,272),1,dtype=int)), axis=0)

        # flip wall
        croppedEdgesImg = numpy.swapaxes(croppedEdgesImg,0,1)

        # get wall heights by finding the bottom edge of the wall
        wallHeightsAll = (croppedEdgesImg!=0).argmax(axis=1)

        # splitting the wall to 8 sections
        oneEighth = 34
        wallHeightsRaw = [wallHeightsAll[0:oneEighth],wallHeightsAll[oneEighth:oneEighth * 2],wallHeightsAll[oneEighth * 2:oneEighth * 3],wallHeightsAll[oneEighth * 3:oneEighth * 4],wallHeightsAll[oneEighth * 4:oneEighth * 5],wallHeightsAll[oneEighth * 5:oneEighth * 6],wallHeightsAll[oneEighth * 6:oneEighth * 7],wallHeightsAll[oneEighth * 7:oneEighth * 8]]

        wallDifferences = [[],[],[],[],[],[],[],[]]
        wallDifferences2 = [[],[],[],[],[],[],[],[]]
        wallSlopes = [0,0,0,0,0,0,0,0]
        wallHeights = [0,0,0,0,0,0,0,0]

        # get difference and slope of wall sections
        for i in range(8):
            wallDifferences[i] = numpy.diff(wallHeightsRaw[i],n=10)
            wallDifferences2[i] = numpy.diff(wallHeightsRaw[i])
            wallSlopes[i] = statistics.mean(wallSlopes)
            wallHeights[i] = statistics.mean(wallHeightsRaw[i])
        
        # wall labels
        wallLabels = [0,0,0,0,0,0,0,0]

        # deteremine wall label based on slope
        for i in range(8):
            if wallSlopes[i] < -0.2:
                wallLabels[i] = LEFT
            elif wallSlopes[i] > 0.2:
                wallLabels[i] = RIGHT
            else:
                wallLabels[i] = CENTER
        
        # change wall labels when a "jump" is detected in a wall, as it must be a different wall.
        jumped = False
        for i in range(7):
            if jumped == True:
                if (6 - i) < 4:
                    if wallLabels[(6 - i)] == CENTER:
                        wallLabels[(6 - i)] = LEFT
            if wallHeights[(6 - i)] - wallHeights[(7 - i)] > 4:
                if (6 - i) < 4:
                    if wallLabels[(6 - i)] == CENTER:
                        wallLabels[(6 - i)] = LEFT
                jumped = True
        
        jumped = False
        for i in range(7):
            if jumped == True:
                if i + 1 > 3:
                    if wallLabels[i + 1] == CENTER:
                        wallLabels[i + 1] = RIGHT
            if wallHeights[i + 1] - wallHeights[i] > 4:
                if i + 1 > 3:
                    if wallLabels[i + 1] == CENTER:
                        wallLabels[i + 1] = RIGHT
                jumped = True

        for i in range(7):
            if wallLabels[i] == LEFT and wallLabels[i + 1] == RIGHT:
                wallLabels[i] = CENTER
                wallLabels[i + 1] = CENTER
        
        # hardcoding wall labels
        wallLabels[0] = LEFT
        wallLabels[1] = LEFT

        if wallLabels[2] == RIGHT:
            wallLabels[2] = CENTER
        if wallLabels[3] == RIGHT:
            wallLabels[3] = CENTER
        if wallLabels[4] == LEFT:
            wallLabels[4] = CENTER
        if wallLabels[5] == LEFT:
            wallLabels[5] = CENTER

        wallLabels[6] = RIGHT
        wallLabels[7] = RIGHT
        
        # for the first frame, detect if we are going clockwise or counterclockwise
        if counterClockwise == 0:
            jumpedLeft = 0
            hitPillarLeft = False
            # detect jump in the wall, if a jump is detected, it must be the way to pass through the wall
            for i in range(4):
                for j in range(len(wallDifferences2[i])):
                    if wallDifferences2[i][j] * -1 > 3:
                        if wallDifferences2[i][j] * -1 > jumpedLeft:
                            jumpedLeft = wallDifferences2[i][j] * -1
                    if wallDifferences2[i][j] > 2:
                        hitPillarLeft = True
                        break
                if hitPillarLeft == True:
                    break
            jumpedRight = 0
            hitPillarRight = False
            # detect jump in the wall, if a jump is detected, it must be the way to pass through the wall
            for i in range(4):
                for j in range(len(wallDifferences2[7 - i])):
                    if wallDifferences2[7 - i][len(wallDifferences2[7 - i]) - j - 1] > 3:
                        if wallDifferences2[7 - i][len(wallDifferences2[7 - i]) - j - 1] > jumpedRight:
                            jumpedRight = wallDifferences2[7 - i][len(wallDifferences2[7 - i]) - j - 1]
                    if wallDifferences2[7 - i][len(wallDifferences2[7 - i]) - j - 1] < -2:
                        hitPillarRight = True
                        break
                if hitPillarRight == True:
                    break
            if jumpedRight > jumpedLeft:
                counterClockwise = 1
            elif jumpedRight < jumpedLeft:
                counterClockwise = -1
            else:
                if wallHeightsRaw[0][0] > wallHeightsRaw[7][len(wallHeightsRaw[7]) - 1]:
                    counterClockwise = 1
                else:
                    counterClockwise = -1
            if debug:
                print(counterClockwise)
                print(jumpedLeft)
                print(jumpedRight)

        leftSteering = 0
        centerSteering = 0
        rightSteering = 0
        
        # steer based on wall heights
        for i in range(8):
            if wallLabels[i] == LEFT:
                if wallHeights[i] > 15:
                    steering = 10
                    if i <= 3:
                        steering += 3.5 * (4 - i)
                    steering += ((wallHeights[i] - 12) ** 2) * 0.5
                    leftSteering += steering
            elif wallLabels[i] == CENTER:
                if wallHeights[i] > 11:
                    steering = 30
                    steering += (wallHeights[i] - 10) * 3
                    centerSteering += steering * counterClockwise
            else:
                if wallHeights[i] > 15:
                    steering = 10
                    if i >= 4:
                        steering += 3.5 * (i - 3)
                    steering += ((wallHeights[i] - 12) ** 2) * 0.5
                    rightSteering -= steering
        
        # decide final steering
        wallSteering = leftSteering + rightSteering
        if abs(wallSteering) < abs(centerSteering):
            wallSteering += centerSteering
            steeringReason += "center wall"
        elif wallSteering != 0:
            steeringReason += "walls"
        
        # BLU #
        
        if debug:
            print(numpy.count_nonzero(bImg[wallStart:]))
        if counterClockwise == 1:
            #CHANGE BACK!!!
            if turnCooldown <= 10 and turnsMade == 12:
                turnsMade += 1
                turnCooldown = 150
                if debug:
                    print(str(turnsMade) + " #########################################")
        else:
            if turnCooldown <= 80 and turnsMade == 12:
                turnsMade += 1
                turnCooldown = 150
                if debug:
                    print(str(turnsMade) + " #########################################")
        if numpy.count_nonzero(bImg[wallStart:]) > 150 and turnCooldown <= 0:
            turnsMade += 1
            turnCooldown = 150
            if debug:
                print(str(turnsMade) + " #########################################")
        turnCooldown -= 1

        if turnsMade >= 13:
            return "stop"

        finalSteering = wallSteering + pillarSteering
        if server != None:
            # send values
            serailzed=[[],[],[],[],[],[],[],[]]
            for i in range(8):
                serailzed[i] = json.dumps(wallHeightsRaw[i].tolist())
            server.broadcast('values', [[str(finalSteering),steeringReason,str(wallSteering),str(pillarSteering)],serailzed])
            arrayR = []
            for i in range(len(rKps)):
                arrayR.append([rKps[i].pt[0],rKps[i].pt[1],rKps[i].size])
            arrayG = []
            for i in range(len(gKps)):
                arrayG.append([gKps[i].pt[0],gKps[i].pt[1],gKps[i].size])
            if brKps != 0 and bgKps != 0:
                server.broadcast('blobs',[[brKps.pt[0],brKps.pt[1],brKps.size],arrayR,[bgKps.pt[0],bgKps.pt[1],bgKps.size],arrayG])
            elif brKps != 0:
                server.broadcast('blobs',[[brKps.pt[0],brKps.pt[1],brKps.size],arrayR,0,arrayG])
            elif bgKps != 0:
                server.broadcast('blobs',[0,arrayR,[bgKps.pt[0],bgKps.pt[1],bgKps.size],arrayG])
            else:
                server.broadcast('blobs',[0,arrayR,0,arrayG])
        return finalSteering
    except Exception as err:
        print(err)
        io.error()

def setColors(data, server = None):
    global redMax, redMin, greenMax, greenMin, blueMax, blueMin
    redMax = (int(data[0]), int(data[3]), int(data[6]))
    greenMax = (int(data[1]), int(data[4]), int(data[7]))
    blueMax = (int(data[2]), int(data[5]), int(data[8]))
    redMin = (int(data[9]), int(data[12]), int(data[15]))
    greenMin = (int(data[10]), int(data[13]), int(data[16]))
    blueMin = (int(data[11]), int(data[14]), int(data[17]))
    print('-- New ----------')
    print(redMax, redMin)
    print(greenMax, greenMin)
    print(blueMax, blueMin)
    if server != None:
        server.broadcast('colors', getColors())
def getColors():
    global redMax, redMin, greenMax, greenMin, blueMax, blueMin
    array = []
    for i in range(9):
        if i % 3 == 0:
            array.append(redMax[math.ceil(i/3)])
        elif i % 2 == 0:
            array.append(greenMax[math.floor(i/3)+1])
        else:
            array.append(blueMax[math.floor(i/3)])
    for i in range(9):
        if i % 3 == 0:
            array.append(redMin[math.ceil(i/3)])
        elif i % 2 == 0:
            array.append(greenMin[math.floor(i/3)+1])
        else:
            array.append(blueMin[math.floor(i/3)])
    return array
def setDefaultColors():
    global rM, rm, gM, gm, bM, bm
    print('-- New ----------')
    print(rM, rm)
    print(gM, gm)
    print(bM, bm)
    return [rM[2], gM[2], bM[2], rM[1], gM[1], bM[1], rM[0], gM[0], bM[0], rm[2], gm[2], bm[2], rm[1], gm[1], bm[1], rm[0], gm[0], bm[0]]
