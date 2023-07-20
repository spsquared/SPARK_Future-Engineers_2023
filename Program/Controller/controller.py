# calculates the path the car should follow
from Controller import converter
from Controller import slam
from IO import io
import math

useServer = True
def setMode(sendServer: bool = None):
    global useServer
    if sendServer != None: useServer = sendServer

def drive():
    leftEdgesImg, leftBlurredG, leftBlurredR = converter.filter(io.camera.io.camera.io.camera.io.camera.io.camera.read()[0])
    rightEdgesImg, rightBlurredG, rightBlurredR = converter.filter(io.camera.io.camera.io.camera.io.camera.io.camera.read()[1])
    heights = converter.getHeights(leftEdgesImg, rightEdgesImg)
    red
    # help heights are separate aaaaaaaaaaaaa
    pass

def getSteering():

    landmarks = slam.storedLandmarks[slam.storedLandmarks[2]].sort(landmarkSort)
    
    nextPoint = [slam.carX, slam.carY]
    nextPointDistance = 10

    for landmark in landmarks:
        if nextPointDistance < getDistance(nextPoint, landmark):
            nextPointDistance -= getDistance(nextPoint, landmark)
            nextPoint = [landmark[0], landmark[1]]
        else:
            angle = math.atan2(landmark[1] - nextPoint[1], landmark[0] - landmark[0])
            magnitude = nextPointDistance
            nextPoint[0] += math.cos(angle) * magnitude
            nextPoint[1] += math.sin(angle) * magnitude

    return math.atan2(nextPoint[1] - slam.carY, nextPoint[0] - slam.carX) - slam.carAngle

def landmarkSort(landmark):
    return slam.carDirection * (math.atan2(landmark[1] - 150, landmark[0] - 150) - math.atan2(slam.carY - 150, slam.carX - 150))

def getDistance(a, b):
    return math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2)
