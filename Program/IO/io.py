import Jetson.GPIO as GPIO
from threading import Thread
import time

# unified IO wrapper that handles all IO for the program

path = '/home/nano/Documents/SPARK_FutureEngineers_2023/'

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
# GPIO.setmode(GPIO.BOARD) stupid forced board mode
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
    global blinkThread, borkedThread, running, borked, path, __pwm
    if running == True:
        fd = open(path + '../lock.txt', 'w+')
        fd.write('0')
        fd.close()
        running = False
        drive.throttle(0)
        camera.stop()
        imu.stop()
        if borked:
            borkedThread.join()
        blinkThread.join()
        GPIO.output([__ledGreen, __ledRed], GPIO.LOW)
        time.sleep(0.1)
        GPIO.cleanup()
        return True
    return False

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
            GPIO.output(__ledGreen, GPIO.HIGH)
        time.sleep(0.5)
        if not statusBlink == 1:
            GPIO.output(__ledGreen, GPIO.LOW)
        time.sleep(0.5)

def error():
    global borked, borkedThread, running
    if borked == False and running == True:
        borked = True
        def borkblink():
            while running:
                GPIO.output(__ledRed, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(__ledRed, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(__ledRed, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(__ledRed, GPIO.LOW)
                time.sleep(0.45)
        borkedThread = Thread(target = borkblink)
        borkedThread.start()
        return True
    return False

# button
def waitForButton():
    GPIO.wait_for_edge(__button, GPIO.RISING)
    GPIO.wait_for_edge(__button, GPIO.FALLING)

blinkThread = Thread(target = __blink)
blinkThread.start()