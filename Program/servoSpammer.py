from IO import io
import time

for i in range(300):
    io.drive.steer(-100)
    time.sleep(0.05)
    io.drive.steer(100)
    time.sleep(0.05)