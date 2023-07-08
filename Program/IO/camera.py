from Controller import converter
from Util import server
from jetcam.csi_camera import CSICamera
from IO import io
import cv2
import os
from threading import Thread
import base64
import time
import numpy

# wrapper for camera functions

imageWidthRaw = 544
imageHeightRaw = 308
imageWidth = 272
imageHeight = 154

camera0 = CSICamera(capture_device=0, width=imageWidthRaw, height=imageHeightRaw, capture_width=3264, capture_height=1848, capture_fps=28)
camera1 = CSICamera(capture_device=1, width=imageWidthRaw, height=imageHeightRaw, capture_width=3264, capture_height=1848, capture_fps=28)
running = True
currentImages = [[[[]]], [[[]]]]
thread = None

camera0.running = True
camera1.running = True
def __capture():
    try:
        global running, camera0, camera1, currentImages
        # update loop that constantly updates the most recent image which can be read at any time
        while running:
            start = time.time()
            currentImages[0] = downscale(undistort(camera0.value))
            currentImages[1] = downscale(undistort(camera1.value))
            time.sleep(max(0.02-(time.time()-start), 0))
    except Exception as err:
        print(err)
        io.error()

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
def downscale(img: numpy.ndarray):
    return cv2.resize(img, (imageWidth, imageHeight), interpolation=cv2.INTER_NEAREST)

# single image save
streamQuality = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
def capture(filter: bool = False, sendServer: bool = True):
    global currentImages
    try:
        name = str(round(time.time()*1000))
        if filter:
            filteredImgs = converter.filter(currentImages, False)
            cv2.imwrite('filtered_out/' + name + '.png', numpy.concatenate((filteredImgs[0], filteredImgs[1]), axis=1))
            if sendServer:
                server.send('message', 'Captured (filtered) ' + name + '.png')
                encoded = [
                    base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                    base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode()
                ]
                server.send('capture', encoded)
            print('Captured (filtered) ' + name + '.png')
        else:
            cv2.imwrite('image_out/' + name + '.png', numpy.concatenate((currentImages[0], currentImages[1]), axis=1))
            if sendServer:
                server.send('message', 'Captured ' + name + '.png')
                encoded = [
                    base64.b64encode(cv2.imencode('.jpg', currentImages[0], streamQuality)[1]).decode(),
                    base64.b64encode(cv2.imencode('.jpg', currentImages[1], streamQuality)[1]).decode()
                ]
                server.send('capture', encoded)
            print('Captured ' + name + '.png')
        return currentImages
    except Exception as err:
        print(err)
        io.error()

# save a stream of images at 10 fps
streamThread = None
streaming = False
totalCaptured = 0
streamServing = False
def startSaveStream(filter: bool = False, sendServer: bool = True):
    global streamThread, streaming, streamServing
    if not streaming:
        streamServing = sendServer
        streaming = True
        name = str(round(time.time()*1000))
        if filter:
            os.mkdir('./filtered_out/' + name)
        else:
            os.mkdir('./image_out/' + name)
        def loop():
            global currentImages, streaming, totalCaptured
            try:
                index = 0
                while streaming:
                    start = time.time()
                    if filter:
                        filteredImgs = converter.filter(currentImages, False)
                        cv2.imwrite('filtered_out/' + name + '/' + str(index) + '.png', numpy.concatenate((filteredImgs[0], filteredImgs[1]), axis=1))
                        if sendServer:
                            encoded = [
                                base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                                base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode()
                            ]
                            server.send('capture', encoded)
                    else:
                        cv2.imwrite('image_out/' + name + '/' + str(index) + '.png', numpy.concatenate((currentImages[0], currentImages[1]), axis=1))
                        if sendServer:
                            encoded = [
                                base64.b64encode(cv2.imencode('.jpg', currentImages[0], streamQuality)[1]).decode(),
                                base64.b64encode(cv2.imencode('.jpg', currentImages[1], streamQuality)[1]).decode()
                            ]
                            server.send('capture', encoded)
                    totalCaptured += 1
                    time.sleep(max(0.1-(time.time()-start), 0))
                    index += 1
            except Exception as err:
                print(err)
        streamThread = Thread(target = loop)
        streamThread.start()
        if sendServer:
            server.send('message', 'Began save stream')
        print('Began save stream')
        return True
    return False
def stopSaveStream():
    global streamThread, streaming, totalCaptured, streamServing
    if streaming == True:
        streaming = False
        streamThread.join()
        if streamServing:
            server.send('message', 'Ended save stream:<br>&emsp;Saved ' + str(totalCaptured) + ' images')
        print('Ended save stream:<br>&emsp;Saved ' + str(totalCaptured) + ' images')
        totalCaptured = 0
        return True
    return False

thread = Thread(target = __capture)
thread.start()