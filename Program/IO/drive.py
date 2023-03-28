import Jetson.GPIO as GPIO
from threading import Thread
from IO import io
import time

# drive module for controlling throttle and steering output

# setup
t = GPIO.PWM(32, 500)
s = GPIO.PWM(33, 200)

# pwm min max and speed
thrBACK = 70
thrMIN = 75
thrMAX = 80
thrBACK2 = 1_400_000
thrMIN2 = 1_500_000
thrMAX2 = 1_550_000
strMAX = 47
strMIN = 28
strTRIM = 8
# throttle feathering
# thrFeaFREQ = 10
# thrFeaDiv = 20
# control variables
targetThrottle = 0
targetSteering = 0
currThrottle = 0
currSteering = 0
steerSpeed = 0.3
# control loop
tickrate = 200
running = False
controlThread = None

def start():
    global controlThread, running
    if running == False:
        # begin
        running = True
        t.start(thrMIN)
        s.start((strMIN+strMAX)/2)
        def loop():
            try:
                # global running, t, s, currThrottle, currSteering, targetThrottle, targetSteering, thrFeaFREQ, thrFeaDiv, tickrate
                global running, t, s, currThrottle, currSteering, targetThrottle, targetSteering, steerSpeed, tickrate
                # timer = 0
                while running:
                    start = time.time()
                    # convert throttle to active time
                    # thrFeaACT = math.floor(abs(targetThrottle)/20)/thrFeaDiv
                    # if timer >= 1: timer = 0
                    # if timer <= thrFeaACT and thrFeaACT < 1 and targetThrottle > 10: currThrottle = 100
                    # elif targetThrottle < -10 or thrFeaACT >= 1: currThrottle = targetThrottle
                    # else: currThrottle = 0
                    currThrottle = targetThrottle
                    currSteering = targetSteering*steerSpeed + currSteering*(1-steerSpeed)
                    # apply throttle and steering
                    if (currThrottle < 0): t.ChangeDutyCycle((currThrottle/100)*(thrMIN-thrBACK)+thrMIN)
                    else: t.ChangeDutyCycle((currThrottle/100)*(thrMAX-thrMIN)+thrMIN)
                    # if (currThrottle < 0): GPIO._set_pwm_duty_cycle(t._ch_info, (currThrottle/100)*(thrMIN2-thrBACK2)+thrMIN2)
                    # else: GPIO._set_pwm_duty_cycle(t._ch_info, (currThrottle/100)*(thrMAX-thrMIN)+thrMIN)
                    s.ChangeDutyCycle((currSteering/100.0)*((strMAX-strMIN)/2)+((strMIN+strMAX)/2)+(strTRIM/10))
                    # advance timer
                    # timer += thrFeaFREQ/tickrate
                    time.sleep(max((1/tickrate)-(time.time()-start), 0))
            except Exception as err:
                print(err)
                io.error()
        controlThread = Thread(target = loop)
        controlThread.start()
        return True
    return False

def stop():
    global running, controlThread
    if running == True:
        running = False
        controlThread.join()
        t.ChangeDutyCycle(thrMIN)
        s.ChangeDutyCycle((strMIN+strMAX)/2)
        t.stop()
        s.stop()
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
    global currSteering
    return -currSteering