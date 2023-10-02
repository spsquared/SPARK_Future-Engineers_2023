from IO import io
import time

def main():
    io.setStatusBlink(2)
    try:
        while True:
            print(io.imu.angle)
            time.sleep(0.2)
    except KeyboardInterrupt:
        io.close()

if __name__ == '__main__':
    main()