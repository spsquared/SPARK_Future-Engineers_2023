from adafruit_servokit import ServoKit
import busio
import board

# drive module that does driving stuff

__pwm = ServoKit(channels = 16, i2c = busio.I2C(board.SCL_1, board.SDA_1))
    
__pwm.continuous_servo[0].throttle = 0.1
__pwm.servo[1].angle = 90

currThr = 0
currStr = 0
throttleFwd = 0.10
throttleRev = -0.15
steeringCenter = 90
steeringRange = 35
steeringTrim = 1
def steer(str: int):
    global __pwm, currStr, steeringCenter, steeringRange, steeringTrim
    currStr = max(-100, min(str, 100))
    __pwm.servo[1].angle = (currStr * steeringRange / 100) + steeringCenter + steeringTrim

def throttle(thr: int):
    global __pwm, currThr, throttleFwd, throttleRev
    currThr = max(-100, min(thr, 100))
    if (currThr < 0):__pwm.continuous_servo[0].throttle = (currThr / 100) * (-throttleRev) + 0.1
    else: __pwm.continuous_servo[0].throttle = (currThr / 100) * throttleFwd + 0.1

def trim(trim: int):
    global steeringTrim, __pwm
    steeringTrim = trim
    steer(currStr)