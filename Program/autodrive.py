from IO import io
io.setup()
from IO import drive
from IO import camera
from Util import server
from AI import filter
import time
import sys

running = True
def main():
    global running
    try:
        io.setStatusBlink(0)
        infinite = False
        wait = False
        openServer = True
        for i, arg in enumerate(sys.argv):
            if i != 0:
                if arg == 'infinite':
                    infinite = True
                if arg == 'wait_for_button':
                    wait = True
                if arg == 'no_server':
                    openServer = False
        if infinite:
            print('PROGRAM RUNNING IN INFINITE MODE!')
        if openServer:
            server.open()
        drive.start()
        camera.start()
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
            camera.stop()
            server.close()
            drive.stop()
            io.close()
            print('stopped by emergency stop button')
            exit(0)
        def stop2(data):
            global running
            running = False
            io.setStatusBlink(0)
            camera.stop()
            server.close()
            drive.stop()
            io.close()
            print('stopped by 3 laps')
            exit(0)
        server.addListener('stop', stop)
        drive.throttle(50)
        while running:
            image = camera.read()
            prediction = filter.predict(image,server, infinite)
            if prediction == "stop":
                # drive.throttle(-20)
                drive.steer(0)
                # time.sleep(0.2)
                drive.throttle(0)
                time.sleep(0.2)
                stop2(1)
                break
            drive.steer(prediction)
            # print("Current Prediction: " + str(prediction))
        #code here
    except KeyboardInterrupt:
        camera.stop()
        drive.stop()
        io.close()
    except Exception as err:
        print(err)
        io.error()

if __name__ == '__main__':
    main()