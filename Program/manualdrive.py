from IO import io
from Util import server
from Controller import driver
from Controller import converter
from threading import Thread
import cv2
import base64

running = True
def main():
    global running
    try:
        server.open()
        io.setStatusBlink(2)
        quality = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
        def drive(data):
            io.drive.throttle(data[0]['throttle'])
            io.drive.steer(data[0]['steering'])
        def capture(data):
            io.camera.capture(False, True)
        def rawCapture(data):
            io.camera.captureFull(True)
        def captureFilter(data):
            converter.setColors(data[0], True)
            io.camera.capture(True, True)
        def captureStream(data):
            if data[0]['state'] == True:
                io.camera.startSaveStream(False, True)
            else:
                io.camera.stopSaveStream()
        def captureFilterStream(data):
            converter.setColors(data[0]['colors'])
            if data[0]['state'] == True:
                io.camera.startSaveStream(True, True)
            else:
                io.camera.stopSaveStream()
        def stream(data):
            if data[0]['state'] == True:
                io.camera.startStream(False)
            else:
                io.camera.stopStream()
        def filterstream(data):
            converter.setColors(data[0], True)
            if data[0]['state'] == True:
                io.camera.startStream(True)
            else:
                io.camera.stopStream()
        def view(data):
            encoded = [
                base64.b64encode(cv2.imencode('.jpg', io.camera.read()[0], quality)[1]).decode(),
                base64.b64encode(cv2.imencode('.jpg', io.camera.read()[1], quality)[1]).decode(),
                0
            ]
            server.emit('capture', encoded)
        def viewFilter(data):
            filter.setColors(data[0])
            encoded = [
                base64.b64encode(cv2.imencode('.png', io.camera.read()[0])[1]).decode(),
                base64.b64encode(cv2.imencode('.png', io.camera.read()[1])[1]).decode(),
                1
            ]
            server.emit('capture', encoded)
        def prediction(data):
            filter.predict(io.camera.read(), server, False)
            server.emit('message', 'Ran prediction on image')
        def colors(data):
            filter.setColors(data[0])
        server.on('drive', drive)
        server.on('capture', capture)
        server.on('rawCapture', rawCapture)
        server.on('captureFilter', captureFilter)
        server.on('captureStream', captureStream)
        server.on('captureFilterStream', captureFilterStream)
        server.on('stream', stream)
        server.on('filterstream', filterstream)
        server.on('view', view)
        server.on('prediction', prediction)
        server.on('viewFilter', viewFilter)
        server.on('colors', colors)
        global running
        running = True
        def stop(data):
            global running
            running = False
            print('stopped by emergency stop button')
        server.on('stop', stop)
        while running:
            msg = input()
            if msg == 'reset':
                server.emit('colors', filter.setDefaultColors())
            elif msg == 'stop':
                break
            elif msg != '':
                server.emit('message', msg)
    except KeyboardInterrupt:
        print('\nSTOPPING PROGRAM. DO NOT INTERRUPT.')
    except Exception as err:
        print('---------------------- AN ERROR OCCURED ----------------------')
        print(err)
        io.error()
    running = False
    server.close()
    io.close()

if __name__ == '__main__':
    main()