import Jetson.GPIO as GPIO
from threading import Thread
from adafruit_servokit import ServoKit
import busio
import board
import time

# general io module

path = '/home/nano/Documents/SPARK_FutureEngineers_2023/'

__pwm = ServoKit(channels = 16, i2c = busio.I2C(board.SCL_1, board.SDA_1))

running = True
blinkThread = None
statusBlink = 0
borked = False
borkedThread = None

# initialize and check if io has been imported multiple times
fd = open(path + '../lock.txt', 'w+')
if fd.read() == '1':
    error()
    raise Exception('ERROR: SETUP HAS DETECTED THAT SETUP IS CURRENTLY RUNNING. PLEASE CLOSE SETUP TO CONTINUE')
fd.write('1')
fd.close()
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup([11, 13, 32, 33], GPIO.OUT)
GPIO.setup(18, GPIO.IN)
GPIO.output([11, 13], GPIO.LOW)

# the status blink stuff
statusBlink = 1
def setStatusBlink(blink: int):
    global statusBlink
    # 0 = off
    # 1 = solid
    # 2 = flashing
    statusBlink = blink

def __blink():
    global running
    while running:
        if not statusBlink == 0:
            GPIO.output(11, GPIO.HIGH)
        time.sleep(0.5)
        if not statusBlink == 1:
            GPIO.output(11, GPIO.LOW)
        time.sleep(0.5)
try:
    blinkThread = Thread(target = __blink)
    blinkThread.start()
except:
    error()

# drive output things
currThr = 0
currStr = 0
throttleFwd = 0.10
throttleRev = -0.15
steeringL = 120
steeringR = 60
steeringTrim = 0
def steer(str: int):
    global __pwm, currStr, steeringL, steeringR, steeringTrim
    currStr = max(-100, min(-str, 100))
    __pwm.servo[1].angle = (currStr / 100) * (steeringL - steeringR) + steeringR + steeringTrim
def throttle(thr: int):
    global __pwm, currThr, throttleFwd, throttleRev
    currThr = max(-100, min(thr, 100))
    if (currThr < 0):__pwm.continuous_servo[0].throttle = (currThr / 100) * (-throttleRev) + 0.1
    else: __pwm.continuous_servo[0].throttle = (currThr / 100) * throttleFwd + 0.1
def trim(trim: int):
    global steeringTrim, __pwm
    steeringTrim = trim
    steer(currStr)
__pwm.continuous_servo[0].throttle = 0.1
__pwm.servo[1].angle = 0

# camera
from IO import camera
camera.start()

# close and error
def close():
    global blinkThread, borkedThread, running, borked, path, __pwm
    if running == True:
        fd = open(path + '../lock.txt', 'w+')
        fd.write('0')
        fd.close()
        running = False
        __pwm.continuous_servo[0].throttle = 0.1
        __pwm.servo[1].angle = 0
        if borked:
            borkedThread.join()
        blinkThread.join()
        camera.stop()
        GPIO.output([11, 13], GPIO.LOW)
        time.sleep(0.1)
        GPIO.cleanup()
        return True
    return False
def error():
    global borked, borkedThread, running
    if borked == False and running == True:
        borked = True
        def borkblink():
            while running:
                GPIO.output(13, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(13, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(13, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(13, GPIO.LOW)
                time.sleep(0.45)
        borkedThread = Thread(target = borkblink)
        borkedThread.start()
        return True
    return False