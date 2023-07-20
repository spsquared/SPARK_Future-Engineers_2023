# calculates the path the car should follow
import slam
import math

X = 0
Y = 1
def landmarkSort(landmark):
    return slam.carDirection * (math.atan2(landmark[Y] - 150, landmark[X] - 150) - math.atan2(slam.carY - 150, slam.carX - 150))

def getDistance(a, b):
    return math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2)

def drive():
    landmarks = slam.storedLandmarks[slam.storedLandmarks[2]].sort(landmarkSort)
    
    nextPoint = [slam.carX, slam.carY]
    nextPointDistance = 10

    for landmark in landmarks:
        if nextPointDistance < getDistance(nextPoint, landmark):
            nextPointDistance -= getDistance(nextPoint, landmark)
            nextPoint = [landmark[X], landmark[Y]]
        else:
            angle = math.atan2(landmark[Y] - nextPoint[Y], landmark[X] - landmark[X])
            magnitude = nextPointDistance
            nextPoint[X] += math.cos(angle) * magnitude
            nextPoint[Y] += math.sin(angle) * magnitude

    return math.atan2(nextPoint[Y] - slam.carY, nextPoint[X] - slam.carX) - slam.carAngle