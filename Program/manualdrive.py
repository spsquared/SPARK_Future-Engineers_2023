from IO import io
from Util import server
from Controller import controller
from Controller import converter
import traceback
import cv2
import base64
import time

running = True
def main():
    global running
    try:
        server.open()
        io.setStatusBlink(2)
        quality = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
        streaming = False
        def drive(data):
            io.drive.throttle(data[0]['throttle'])
            io.drive.steer(data[0]['steering'])
        def capture(data):
            try:
                if data[0]['save'] == True:
                    if data[0]['filter'] == True:
                        converter.setColors(data[0]['colors'], True)
                    io.camera.capture(data[0]['filter'], True)
                else:
                    if data[0]['filter'] == True:
                        converter.setColors(data[0]['colors'], True)
                        encoded = [
                            base64.b64encode(cv2.imencode('.png', cv2.merge(converter.filter(io.camera.read()[0])))[1]).decode(),
                            base64.b64encode(cv2.imencode('.png', cv2.merge(converter.filter(io.camera.read()[1])))[1]).decode(),
                            1,
                            0
                        ]
                        start = time.perf_counter()

                        # a = 1
                        read = io.camera.read()
                        leftEdgesImg, gLeftImg, rLeftImg = converter.filter(converter.undistort(read[0]))
                        rightEdgesImg, gRightImg, rRightImg = converter.filter(converter.undistort(read[1]))
                        leftHeights, rightHeights = converter.getRawHeights(leftEdgesImg, rightEdgesImg)
                        rLeftBlobs, gLeftBlobs, rRightBlobs, gRightBlobs = converter.getBlobs(rLeftImg, gLeftImg, rRightImg, gRightImg)
                        leftWalls = converter.getWallLandmarks(leftHeights.copy(), rLeftBlobs, gLeftBlobs)
                        # for i in range(converter.imageWidth):
                        #     for j in range(30):
                        #         a += read[j][i]
                        # # new_K = converter.K.copy()
                        # # new_K[0][0] *= 0.5
                        # # new_K[1][1] *= 0.5
                        # # map1, map2 = cv2.fisheye.initUndistortRectifyMap(converter.K, converter.D, numpy.eye(3), new_K, (converter.imageWidth, converter.imageHeight), cv2.CV_16SC2)
                        # # undistortedLeftImg = cv2.remap(io.camera.read()[0], map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
                        print(time.perf_counter() - start)
                        server.emit('capture', encoded)
                    else:
                        encoded = [
                            base64.b64encode(cv2.imencode('.jpg', io.camera.read()[0], quality)[1]).decode(),
                            base64.b64encode(cv2.imencode('.jpg', io.camera.read()[1], quality)[1]).decode(),
                            0,
                            0
                        ]
                        server.emit('capture', encoded)
            except Exception as err:
                traceback.print_exc()
                io.error()
                server.emit('programError', str(err))
        def rawCapture(data):
            io.camera.captureFull(True)
        def stream(data):
            nonlocal streaming
            streaming = not streaming
            if data[0]['save'] == True:
                if not streaming:
                    io.camera.stopSaveStream()
                else:
                    if data[0]['filter'] == True:
                        converter.setColors(data[0]['colors'], True)
                    io.camera.startSaveStream(data[0]['filter'], True)
            else:
                if not streaming:
                    io.camera.stopStream()
                else:
                    if data[0]['filter'] == True:
                        converter.setColors(data[0]['colors'], True)
                    io.camera.startStream(data[0]['filter'])
        def getColors(data):
            server.emit('colors', converter.getColors())
        def setColors(data):
            converter.setColors(data[0], True)
        def getStreamState(data):
            server.emit('streamState', io.camera.streamState())
        server.on('drive', drive)
        server.on('capture', capture)
        server.on('rawCapture', rawCapture)
        server.on('stream', stream)
        server.on('getColors', getColors)
        server.on('setColors', setColors)
        server.on('getStreamState', getStreamState)
        global running
        running = True
        def stop(data):
            global running
            running = False
            print('stopped by emergency stop button')
            io.close()
            server.close()
            exit()
        server.on('stop', stop)
        while running:
            msg = input()
            if msg == 'reset':
                server.emit('colors', converter.setDefaultColors())
            elif msg == 'calibrate-gyro':
                io.imu.calibrate()
            elif msg == 'stop':
                break
            elif msg != '':
                server.emit('message', msg)
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

if __name__ == '__main__':
    main()