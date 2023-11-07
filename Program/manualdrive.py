from IO import io
from Util import server
from Controller import controller as controller
from Controller import converter
import traceback
import cv2
import base64
import time
from threading import Thread
import sys

running = True
def main():
    global running
    try:
        io.setStatusBlink(0)
        acceptTerminalInput = True
        for i, arg in enumerate(sys.argv):
            if i != 0:
                if arg == 'no_terminal':
                    acceptTerminalInput = False
        server.open()
        io.setStatusBlink(2)
        quality = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
        streaming = False
        predictStreaming = False
        def idManual(data):
            server.emit('idManual', 0)
        def drive(data):
            io.drive.throttle(data[0]['throttle'])
            io.drive.steer(data[0]['steering'])
        def capture(data):
            try:
                if data[0]['save'] == True:
                    if data[0]['colors'] != False:
                        converter.setColors(data[0]['colors'], True)
                    io.camera.capture(data[0]['filter'], data[0]['undistort'], True)
                else:
                    if data[0]['filter'] == True:
                        if data[0]['colors'] != False:
                            converter.setColors(data[0]['colors'], True)
                        if data[0]['undistort'] == True:
                            encoded = [
                                base64.b64encode(cv2.imencode('.png', cv2.merge(converter.filter(converter.undistort(io.camera.read()[0]))))[1]).decode(),
                                base64.b64encode(cv2.imencode('.png', cv2.merge(converter.filter(converter.undistort(io.camera.read()[1]))))[1]).decode(),
                                1,
                                0,
                                0
                            ]
                            server.emit('capture', encoded)
                        else:
                            encoded = [
                                base64.b64encode(cv2.imencode('.png', cv2.merge(converter.filter(io.camera.read()[0])))[1]).decode(),
                                base64.b64encode(cv2.imencode('.png', cv2.merge(converter.filter(io.camera.read()[1])))[1]).decode(),
                                1,
                                0,
                                0
                            ]
                            server.emit('capture', encoded)
                    else:
                        if data[0]['undistort'] == True:
                            encoded = [
                                base64.b64encode(cv2.imencode('.jpg', io.camera.read()[0], quality)[1]).decode(),
                                base64.b64encode(cv2.imencode('.jpg', io.camera.read()[1], quality)[1]).decode(),
                                0,
                                0,
                                0
                            ]
                            server.emit('capture', encoded)
                        else:
                            encoded = [
                                base64.b64encode(cv2.imencode('.jpg', converter.undistort(io.camera.read()[0]), quality)[1]).decode(),
                                base64.b64encode(cv2.imencode('.jpg', converter.undistort(io.camera.read()[1]), quality)[1]).decode(),
                                0,
                                0,
                                0
                            ]
                            server.emit('capture', encoded)
            except Exception as err:
                traceback.print_exc()
                io.error()
                server.emit('programError', str(err))
        def stream(data):
            nonlocal streaming
            streaming = not streaming
            if data[0]['save'] == True:
                if not streaming:
                    io.camera.stopSaveStream()
                else:
                    if data[0]['filter'] == True:
                        converter.setColors(data[0]['colors'], True)
                    io.camera.startSaveStream(data[0]['filter'], data[0]['undistort'], True)
            else:
                if not streaming:
                    io.camera.stopStream()
                else:
                    if data[0]['filter'] == True:
                        converter.setColors(data[0]['colors'], True)
                    io.camera.startStream(data[0]['filter'], data[0]['undistort'])
        def predictStream(data):
            nonlocal predictStreaming
            predictStreaming = not predictStreaming
            if predictStreaming:
                def loop():
                    nonlocal predictStreaming
                    try:
                        while predictStreaming:
                            start = time.time()
                            controller.drive(True)
                            time.sleep(max(0.1-(time.time()-start), 0))
                    except Exception as err:
                        traceback.print_exc()
                        io.error()
                        server.emit('programError', str(err))
                thread = Thread(target = loop)
                thread.start()
                server.emit('message', 'Began prediction stream')
                server.emit('predictStreamState', [True])
                print('Began prediction stream')
            else:
                server.emit('message', 'Ended prediction stream')
                server.emit('predictStreamState', [False])
                print('Ended prediction stream')
        def resetPrediction(data):
            controller.slam.carAngle = 0
        def getColors(data):
            server.emit('colors', converter.getColors())
        def setColors(data):
            converter.setColors(data[0], True)
        def getStreamState(data):
            nonlocal predictStreaming
            server.emit('streamState', io.camera.streamState())
            server.emit('predictStreamState', [predictStreaming])
        server.on('idManual', idManual)
        server.on('drive', drive)
        server.on('capture', capture)
        server.on('stream', stream)
        server.on('predictStream', predictStream)
        server.on('resetPrediction', resetPrediction)
        server.on('getColors', getColors)
        server.on('setColors', setColors)
        server.on('getStreamState', getStreamState)
        global running
        running = True
        def stop(data):
            global running
            running = False
            print('\n STOPPING PROGRAM. DO NOT INTERRUPT.')
            io.close()
            server.close()
            sys.exit(0)
        io.imu.setAngle(0)
        server.on('stop', stop)
        acceptTerminalInput = False
        if acceptTerminalInput:
            while running:
                msg = input()
                if msg == 'reset':
                    server.emit('colors', converter.setDefaultColors())
                elif msg == 'calibrate-gyro':
                    io.imu.calibrate()
                elif msg == 'stop':
                    break
                elif msg != '':
                    server.emit('unsafemessage', msg)
    except KeyboardInterrupt:
        print('\nSTOPPING PROGRAM. DO NOT INTERRUPT.')
    except Exception as err:
        print('---------------------- AN ERROR OCCURED ----------------------')
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))
    running = False
    io.close()
    server.close()
    sys.exit(0)

if __name__ == '__main__':
    main()