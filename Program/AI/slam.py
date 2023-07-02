from IO import io
import numpy
import cv2
import base64
import statistics
import math
import json

# does EKF SLAM

X = 0
Y = 1
FOUND = 2
COLOR = 3
RED = 0
GREEN = 1

landmarks = [
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