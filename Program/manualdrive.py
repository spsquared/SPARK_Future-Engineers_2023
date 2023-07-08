from IO import io
from Util import server
from Controller import driver
from Controller import converter
from threading import Thread
import cv2
import time
import base64

__forward = 0
__backward = 0
__left = 0
__right = 0
running = True
streamThread = None
streamThread2 = None
streaming = False
streaming2 = False
def main():
    global running
    try:
        server.open()
        io.setStatusBlink(2)
        def drive(data):
            io.drive.throttle(data['throttle'])
            io.drive.steer(data['steering'])
        def capture(data):
            io.camera.capture(True)
        def captureStream(data):
            if data['state'] == True:
                io.camera.startSaveStream(True)
            else:
                io.camera.stopSaveStream(True)
        def captureFilter(data):
            converter.setColors(data, True)
            io.camera.capture(True, True)
        def captureFilterStream(data):
            converter.setColors(data['colors'])
            if data['state'] == True:
                io.camera.startSaveStream(True, True)
            else:
                io.camera.stopSaveStream(True)
        def stream(data):
            global streamThread, streaming
            if data['state'] == True:
                if streaming == False:
                    streaming = True
                    def loop():
                        global streaming, running
                        try:
                            while streaming and running:
                                start = time.time()
                                encoded = [
                                    base64.b64encode(cv2.imencode('.png', io.camera.read()[0])[1]).decode(),
                                    base64.b64encode(cv2.imencode('.png', io.camera.read()[1])[1]).decode()
                                ]
                                server.emit('capture', encoded)
                                time.sleep(max(0.1-(time.time()-start), 0))
                        except Exception as err:
                            print(err)
                    streamThread = Thread(target = loop)
                    streamThread.start()
                    server.emit('message', 'Began stream')
            else:
                if streaming == True:
                    streaming = False
                    streamThread.join()
                    server.emit('message', 'Ended stream')
        def filterstream(data):
            global streamThread2, streaming2
            filter.setColors(data['colors'])
            if data['state'] == True:
                if streaming2 == False:
                    streaming2 = True
                    def loop():
                        global streaming2, running
                        try:
                            while streaming2 and running:
                                start = time.time()
                                encoded = [
                                    base64.b64encode(cv2.imencode('.png', io.camera.read()[0])[1]).decode(),
                                    base64.b64encode(cv2.imencode('.png', io.camera.read()[1])[1]).decode()
                                ]
                                server.emit('capture', encoded)
                                time.sleep(max(0.05-(time.time()-start), 0))
                        except Exception as err:
                            print(err)
                    streamThread2 = Thread(target = loop)
                    streamThread2.start()
                    server.emit('message', 'Began filtered stream')
            else:
                if streaming2 == True:
                    streaming2 = False
                    streamThread2.join()
                    server.emit('message', 'Ended filtered stream')
        def view(data):
            encoded = [
                base64.b64encode(cv2.imencode('.png', io.camera.read()[0])[1]).decode(),
                base64.b64encode(cv2.imencode('.png', io.camera.read()[1])[1]).decode()
            ]
            server.emit('capture', encoded)
        def viewFilter(data):
            filter.setColors(data)
            encoded = [
                base64.b64encode(cv2.imencode('.png', io.camera.read()[0])[1]).decode(),
                base64.b64encode(cv2.imencode('.png', io.camera.read()[1])[1]).decode()
            ]
            server.emit('capture', encoded)
        def prediction(data):
            filter.predict(io.camera.read(), server, False)
            server.emit('message', 'Ran prediction on image')
        def colors(data):
            filter.setColors(data)
        server.on('drive', drive)
        server.on('capture', capture)
        server.on('captureStream', captureStream)
        server.on('colors', colors)
        server.on('captureFilter', captureFilter)
        server.on('captureFilterStream', captureFilterStream)
        server.on('view', view)
        server.on('viewFilter', viewFilter)
        server.on('stream', stream)
        server.on('filterstream', filterstream)
        server.on('prediction', prediction)
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