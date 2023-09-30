from IO import io
from Util import server
from adafruit_servokit import ServoKit
import busio
import board
from threading import Thread
import time
import traceback

# drive module that does driving stuff

__pwm = ServoKit(channels = 16, i2c = busio.I2C(board.SCL_1, board.SDA_1))

__currThr = 0
__targetStr = 0
__currStr = 0
__throttleFwd = 0.08
__throttleRev = -0.15
__steeringCenter = 90
__steeringRange = 45
__steeringTrim = 12
__smoothFactor = 0
__thread = None
__running = True
def __update():
    global __currStr, __targetStr, __steeringCenter, __steeringRange, __steeringTrim, __pwm, __running, __smoothFactor
    try:
        lastAngle = 0
        while __running:
            __currStr = (__smoothFactor * __currStr) + ((1 - __smoothFactor) * __targetStr)
            angle = round((__currStr * __steeringRange / 100) + __steeringCenter + __steeringTrim)
            if angle != lastAngle: __pwm.servo[1].angle = angle
            lastAngle = angle
            time.sleep(0.02)
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))
def steer(str: int):
    global __targetStr
    __targetStr = max(-100, min(str, 100))
def throttle(thr: int):
    global __pwm, __currThr, __throttleFwd, __throttleRev
    __currThr = max(-100, min(thr, 100))
    if (__currThr < 0):__pwm.continuous_servo[0].throttle = (__currThr / 100) * (-__throttleRev) + 0.1
    else: __pwm.continuous_servo[0].throttle = (__currThr / 100) * __throttleFwd + 0.1
def trim(trim: int):
    global __steeringTrim
    __steeringTrim = trim
    steer(__currStr)
def setSmoothFactor(smooth: float):
    global __smoothFactor
    __smoothFactor = max(0, min(smooth, 1))

def currentSteering():
    global __currStr
    return __currStr
def getSmoothFactor():
    global __smoothFactor
    return __smoothFactor

def stop():
    global __running
    steer(0)
    throttle(0)
    __running = False
    __thread.join()

__thread = Thread(target = __update)
__thread.start()
steer(0)
throttle(0)