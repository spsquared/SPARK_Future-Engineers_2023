from adafruit_servokit import ServoKit
import busio
import board

# drive module that does driving stuff

__pwm = ServoKit(channels = 16, i2c = busio.I2C(board.SCL_1, board.SDA_1))

__currThr = 0
__currStr = 0
__throttleFwd = 0.10
__throttleRev = -0.15
__steeringCenter = 90
__steeringRange = 35
__steeringTrim = 9
def steer(str: int):
    global __pwm, __currStr, __steeringCenter, __steeringRange, __steeringTrim
    __currStr = max(-100, min(str, 100))
    __pwm.servo[1].angle = (__currStr * __steeringRange / 100) + __steeringCenter + __steeringTrim
def throttle(thr: int):
    global __pwm, __currThr, __throttleFwd, __throttleRev
    __currThr = max(-100, min(thr, 100))
    if (__currThr < 0):__pwm.continuous_servo[0].throttle = (__currThr / 100) * (-__throttleRev) + 0.1
    else: __pwm.continuous_servo[0].throttle = (__currThr / 100) * __throttleFwd + 0.1
def trim(trim: int):
    global __steeringTrim, __pwm
    __steeringTrim = trim
    steer(__currStr)

def stop():
    steer(0)
    throttle(0)

steer(0)
throttle(0)