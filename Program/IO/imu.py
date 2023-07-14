from IO import io
from Util import server
import adafruit_mpu6050
import board
import busio
from threading import Thread
import traceback
import time

# wrapper for IMU

__mpu = adafruit_mpu6050.MPU6050(busio.I2C(board.SCL, board.SDA))

__angle = 0
__trim = 0.017629823913751886 # change this to calibrated number
thread = None
running = True
def __update():
    global __angle, running
    lastTick = time.time()
    try:
        while running:
            __angle += (time.time() - lastTick) * (__mpu.gyro[2] + __trim)
            lastTick = time.time()
            time.sleep(0.02)
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))

def calibrate():
    print('[!] CALIBRATING GYROSCOPE - DO NOT TOUCH [!]')
    anglediffs = []
    for i in range(200):
        anglediffs.append(__mpu.gyro[2])
        if i % 10 == 0: print(str(i / 2) + '%')
        time.sleep(0.05)
    sum = 0
    for i in anglediffs:
        sum += i
    print('[!] CALIBRATION COMPLETE - TRIM BELOW [!]')
    print('')
    print(sum / -200)
    print('')
    print('Place this number in "/IO/imu.py" in "__trim"')


def angle():
    return __angle
def resetAngle(newAngle: int):
    global __angle
    __angle = newAngle

def stop():
    global running
    running = False
    thread.join()
    return

thread = Thread(target = __update)
thread.start()