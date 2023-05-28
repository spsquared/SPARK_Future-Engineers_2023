import Jetson.GPIO as GPIO
from threading import Thread
from IO import io
import time

# drive module for controlling throttle and steering

# setup
throttleFreq = 500
steeringFreq = 200
throttle = GPIO.PWM(32, throttleFreq)
steering = GPIO.PWM(33, steeringFreq)

# pwm min max active times
throttleRev = 1_400_000
throttleStop = 1_500_000
throttleFwd = 1_550_000
steeringRange = 300_000
steeringLeft = 1_500_000 + steeringRange
steeringRight = 1_500_000 - steeringRange
steeringTrim = 0
# control variables
targetThrottle = 0
targetSteering = 0
# control loop
refreshRate = 200
running = False
controlThread = None

def start():
    global controlThread, running, throttle, steering
    if running == False:
        running = True
        throttle.start(0)
        steering.start(0)
        def loop():
            global running, refreshRate, targetThrottle, targetSteering, throttle, steering, throttleRev, throttleStop, throttleFwd, steeringRight, steeringLeft, steeringTrim, steeringRange
            try:
                while running:
                    start = time.time()
                    # apply throttle and steering based on percent to range formula
                    if (targetThrottle < 0): GPIO._set_pwm_duty_cycle(throttle._ch_info, (targetThrottle / 100) * (throttleStop - throttleRev) + throttleStop)
                    else: GPIO._set_pwm_duty_cycle(throttle._ch_info, (targetThrottle / 100) * (throttleFwd - throttleStop) + throttleStop)
                    GPIO._set_pwm_duty_cycle(steering._ch_info, (targetSteering / 100) * ((steeringLeft - steeringRight) / 2) + (steeringLeft + steeringRight) + ((steeringTrim / 100) * steeringRange))
                    time.sleep(max((1/refreshRate)-(time.time()-start), 0))
            except Exception as err:
                print(err)
                io.error()
        controlThread = Thread(target = loop)
        controlThread.start()
        return True
    return False

def stop():
    global running, controlThread, throttle, steering
    if running == True:
        running = False
        controlThread.join()
        throttle.stop()
        steering.stop()
        return True
    return False

# inputs
def steer(steering: int):
    global targetSteering
    targetSteering = max(-100, min(-steering, 100))

def throttle(throttle: int):
    global targetThrottle
    targetThrottle = max(-100, min(throttle, 100))

def trim(trim: int):
    global strTRIM
    strTRIM = trim

# get current
def currentSteering():
    global targetSteering
    return -targetSteering