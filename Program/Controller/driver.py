# calculates the path the car should follow
from random import *

def drive():
    if random.random() < 0.001:
        return "stop"
    else:
        return random.randint(-100, 100)