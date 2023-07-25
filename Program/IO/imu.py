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
__trim = 0.03414636758096449 # change this to calibrated number
__thread = None
__running = True
def __update():
    global __angle, __running
    lastTick = time.time()
    try:
        while __running:
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
    for i in range(500):
        anglediffs.append(__mpu.gyro[2])
        if i % 10 == 0: print(str(i / 5) + '%')
        time.sleep(0.02)
    sum = 0
    for i in anglediffs:
        sum += i
    newtrim = sum / -500
    print('[!] CALIBRATION COMPLETE - TRIM BELOW [!]')
    print('')
    print(newtrim)
    print('')
    print('Place this number in "/IO/imu.py" in "__trim"')
    __trim = newtrim
    return newtrim

# gyro stuff
def angle():
    return __angle
def setAngle(newAngle: float = 0):
    global __angle
    __angle = newAngle

def stop():
    global __running
    __running = False
    __thread.join()
    return

__thread = Thread(target = __update)
__thread.start()