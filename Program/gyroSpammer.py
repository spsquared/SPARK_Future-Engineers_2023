from IO import io
import time
import math

io.drive.throttle(80)

angle = io.imu.angle() + math.pi * 2 / 1.25
for i in range(3000):
    io.drive.steer(100)
    print(io.imu.angle())
    print(angle)
    if io.imu.angle() > angle:
        break
    time.sleep(0.1)

io.drive.steer(0)
io.drive.throttle(0)