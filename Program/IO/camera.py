from jetcam.csi_camera import CSICamera
import cv2
import os
from threading import Thread
from IO import io
import base64
import time
import numpy

# wrapper for camera functions

imageWidth = 272
imageHeight = 154

camera0 = CSICamera(capture_device=0, width=imageWidth, height=imageHeight, capture_width=3264, capture_height=1848, capture_fps=28)
camera1 = CSICamera(capture_device=1, width=imageWidth, height=imageHeight, capture_width=3264, capture_height=1848, capture_fps=28)
running = False
currentImages = [[[[]]], [[[]]]]
thread = None

camera0.running = True
camera1.running = True
running = True
def __capture():
    try:
        global running, camera0, camera1, currentImages
        # update loop that constantly updates the most recent image which can be read at any time
        while running:
            start = time.time()
            currentImages[0] = undistort(camera0.value)
            currentImages[1] = undistort(camera1.value)
            time.sleep(max(0.02-(time.time()-start), 0))
    except Exception as err:
        print(err)
        io.error()
thread = Thread(target = __capture)
thread.start()

def stop():
    global running, camera0, camera1, thread
    if running == True:
        running = False
        thread.join()
        camera0.running = False
        camera1.running = False

# read current image
def read():
    global currentImages
    return currentImages

def undistort(img: numpy.ndarray):
    return img

# single image save
def capture(converter = None, server = None):
    global currentImages
    try:
        name = str(round(time.time()*1000))
        if converter != None:
            filteredImgs = converter.filter(currentImages, False)
            cv2.imwrite('filtered_out/' + name + '.png', filteredImgs[0].concatenate(filteredImgs[1]))
            if server != None:
                server.broadcast('message', 'Captured (filtered) ' + name + '.png')
                encoded = [
                    base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                    base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode()
                ]
                server.broadcast('capture', encoded)
            print('Captured (filtered) ' + name + '.png')
        else:
            cv2.imwrite('image_out/' + name + '.png', currentImages[0].concatenate(currentImages[1]))
            if server != None:
                server.broadcast('message', 'Captured ' + name + '.png')
                encoded = [
                    base64.b64encode(cv2.imencode('.png', currentImages[0])[1]).decode(),
                    base64.b64encode(cv2.imencode('.png', currentImages[1])[1]).decode()
                ]
                server.broadcast('capture', encoded)
            print('Captured ' + name + '.png')
        return currentImages
    except Exception as err:
        print(err)
        io.error()

# save a stream of images at 10 fps
streamThread = None
streaming = False
totalCaptured = 0
def startSaveStream(converter = None, server = None):
    global streamThread, streaming
    if streaming == False:
        streaming = True
        name = str(round(time.time()*1000))
        if converter != None:
            os.mkdir('./filtered_out/' + name)
        else:
            os.mkdir('./image_out/' + name)
        def loop():
            global currentImages, streaming, totalCaptured
            try:
                index = 0
                while streaming:
                    start = time.time()
                    if converter != None:
                        filteredImgs = converter.filter(currentImages, False)
                        cv2.imwrite('filtered_out/' + name + '/' + str(index) + '.png', filteredImgs[0].concatenate(filteredImgs[1]))
                        if server != None:
                            encoded = [
                                base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                                base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode()
                            ]
                            server.broadcast('capture', encoded)
                    else:
                        cv2.imwrite('image_out/' + name + '/' + str(index) + '.png', currentImages[0].concatenate(currentImages[1]))
                        if server != None:
                            encoded = [
                                base64.b64encode(cv2.imencode('.png', currentImages[0])[1]).decode(),
                                base64.b64encode(cv2.imencode('.png', currentImages[1])[1]).decode()
                            ]
                            server.broadcast('capture', encoded)
                    totalCaptured += 1
                    time.sleep(max(0.1-(time.time()-start), 0))
                    index += 1
            except Exception as err:
                print(err)
        streamThread = Thread(target = loop)
        streamThread.start()
        if server != None:
            server.broadcast('message', 'Began save stream')
        print('Began save stream')
        return True
    return False
def stopSaveStream(server = None):
    global streamThread, streaming, totalCaptured
    if streaming == True:
        streaming = False
        streamThread.join()
        if server != None:
            server.broadcast('message', 'Ended save stream:<br>&emsp;Saved ' + str(totalCaptured) + ' images')
        print('Ended save stream:<br>&emsp;Saved ' + str(totalCaptured) + ' images')
        totalCaptured = 0
        return True
    return False