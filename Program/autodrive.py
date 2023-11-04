from IO import io
from Util import server
from Controller import controller as controller
import time
import sys
import traceback
running = True
actuallyRunning = True

def main():
    global running, actuallyRunning
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
        if sendServer:
            server.open()
            controller.setMode(sendServer=True)
        else:
            controller.setMode(sendServer=False)
        io.setStatusBlink(1)
        if wait:
            print('Waiting for button')
            io.waitForButton()
        else:
            time.sleep(1)
        io.setStatusBlink(2)
        def stop(data):
            global actuallyRunning
            actuallyRunning = False
            print('Stopped by stop button')
            io.setStatusBlink(0)
            io.close()
            server.close()
            sys.exit(0)
        server.on('stop', stop)
        io.drive.throttle(controller.speed)
        io.imu.setAngle(0)
        print("starting run")
        while running and actuallyRunning:
            running = controller.drive()
            if infinite: running = True
        print('Stopped by driver command')
    except KeyboardInterrupt:
        print('\nSTOPPING PROGRAM. DO NOT INTERRUPT.')
    except Exception as err:
        print('---------------------- AN ERROR OCCURED ----------------------')
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))
    running = False
    io.drive.throttle(0)
    io.close()
    server.close()
    sys.exit(0)

if __name__ == '__main__':
    main()