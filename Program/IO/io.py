

import Jetson.GPIO as GPIO
from threading import Thread
import time

fd = open('/home/nano/Documents/b.txt', 'w+')
fd.write('gpio imported')
fd.close()

# unified IO wrapper that handles all IO for the program

__running = True
__blinkThread = None
__statusBlink = 0
__borked = False
__borkedThread = None

def error():
    global __borked, __borkedThread, __running
    if __borked == False and __running:
        __borked = True
        def borkblink():
            while __running:
                GPIO.output(__ledRed, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(__ledRed, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(__ledRed, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(__ledRed, GPIO.LOW)
                time.sleep(0.45)
        __borkedThread = Thread(target = borkblink)
        __borkedThread.start()
        return True
    return False

GPIO.setwarnings(False)
GPIO.cleanup()
# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.TEGRA_SOC) # stupid forced board mode
__ledGreen = 'UART2_RTS'
__ledRed = 'SPI2_SCK'
__button = 'SPI2_CS0'
GPIO.setup([__ledGreen, __ledRed], GPIO.OUT)
GPIO.setup(__button, GPIO.IN)
GPIO.output([__ledGreen, __ledRed], GPIO.LOW)

from IO import drive
from IO import camera
from IO import imu

def close():
    global __blinkThread, __borkedThread, __running, __borked, __pwm
    if __running:
        __running = False
        drive.stop()
        camera.stop()
        imu.stop()
        if __borked:
            __borkedThread.join()
        __blinkThread.join()
        GPIO.output([__ledGreen, __ledRed], GPIO.LOW)
        time.sleep(0.1)
        GPIO.cleanup()
        return True
    return False

# the status blink stuff
__statusBlink = 1
def setStatusBlink(blink: int):
    global __statusBlink
    # 0 = off
    # 1 = solid
    # 2 = flashing
    __statusBlink = min(2, max(0, blink))

def __blink():
    global __running
    while __running:
        if not __statusBlink == 0:
            GPIO.output(__ledGreen, GPIO.HIGH)
        time.sleep(0.5)
        if not __statusBlink == 1:
            GPIO.output(__ledGreen, GPIO.LOW)
        time.sleep(0.5)

# button
def waitForButton():
    GPIO.wait_for_edge(__button, GPIO.RISING)
    GPIO.wait_for_edge(__button, GPIO.FALLING)

__blinkThread = Thread(target = __blink)
__blinkThread.start()