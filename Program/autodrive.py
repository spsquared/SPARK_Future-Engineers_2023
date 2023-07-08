from IO import io
from Util import server
from Controller import driver
import time
import sys

running = True
def main():
    global running
    try:
        io.setStatusBlink(0)
        infinite = False
        wait = False
        sendServer = True
        for i, arg in enumerate(sys.argv):
            if i != 0:
                if arg == 'infinite':
                    infinite = True
                if arg == 'wait_for_button':
                    wait = True
                if arg == 'no_server':
                    sendServer = False
        if infinite:
            print('PROGRAM RUNNING IN INFINITE MODE!')
        io.setStatusBlink(1)
        if wait:
            print('Waiting for button')
            io.waitForButton()
        else:
            time.sleep(1)
        io.setStatusBlink(2)
        def stop(data):
            global running
            running = False
            io.setStatusBlink(0)
            io.close()
            print('stopped by emergency stop button')
            exit(0)
        def stop2(data):
            global running
            running = False
            io.setStatusBlink(0)
            io.close()
            print('stopped by 3 laps')
            exit(0)
        server.addListener('stop', stop)
        io.drive.throttle(50)
        while running:
            image = io.camera.read()
            # prediction = driver.predict(image, sendServer, infinite)
            # if prediction == "stop":
            #     # drive.throttle(-20)
            #     io.drive.steer(0)
            #     # time.sleep(0.2)
            #     io.drive.throttle(0)
            #     time.sleep(0.2)
            #     stop2(1)
            #     break
            # io.drive.steer(prediction)
            # print("Current Prediction: " + str(prediction))
        #code here
    except KeyboardInterrupt:
        io.close()
        server.close()
    except Exception as err:
        print(err)
        io.error()

if __name__ == '__main__':
    main()