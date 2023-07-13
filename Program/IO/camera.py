from Controller import converter
from Util import server
from jetcam.csi_camera import CSICamera
from IO import io
import traceback
import cv2
import os
from threading import Thread
import base64
import time
import numpy

# wrapper for camera functions

imageWidthRaw = 1088
imageHeightRaw = 616
imageWidth = 544
imageHeight = 308

camera0 = CSICamera(capture_device=0, width=imageWidthRaw, height=imageHeightRaw, capture_width=3264, capture_height=1848, capture_fps=28)
camera1 = CSICamera(capture_device=1, width=imageWidthRaw, height=imageHeightRaw, capture_width=3264, capture_height=1848, capture_fps=28)
running = True
currentRawImages = [None, None]
currentImages = [None, None]
thread = None

camera0.running = True
camera1.running = True
def __capture():
    try:
        global running, camera0, camera1, currentImages
        # update loop that constantly updates the most recent image which can be read at any time
        while running:
            start = time.time()
            currentRawImages[0] = undistort(camera0.value)
            currentRawImages[1] = undistort(camera1.value)
            currentImages[0] = downscale(currentRawImages[0])
            currentImages[1] = downscale(currentRawImages[1])
            time.sleep(max(0.02-(time.time()-start), 0))
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))

def stop():
    global running, camera0, camera1, thread
    if running:
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
serverQuality = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
def capture(filter: bool, sendServer: bool):
    try:
        name = str(round(time.time()*1000))
        if filter:
            filteredImgs = [cv2.merge(converter.filter(read()[0])), cv2.merge(converter.filter(read()[1]))]
            cv2.imwrite('filtered_out/' + name + '.png', numpy.concatenate((filteredImgs[0], filteredImgs[1]), axis=1))
            if sendServer:
                server.emit('message', 'Captured (filtered) ' + name + '.png')
                encoded = [
                    base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                    base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode(),
                    1
                ]
                server.emit('capture', encoded)
            print('Captured (filtered) ' + name + '.png')
        else:
            cv2.imwrite('image_out/' + name + '.png', numpy.concatenate((currentImages[0], currentImages[1]), axis=1))
            if sendServer:
                server.emit('message', 'Captured ' + name + '.png')
                encoded = [
                    base64.b64encode(cv2.imencode('.jpg', currentImages[0], serverQuality)[1]).decode(),
                    base64.b64encode(cv2.imencode('.jpg', currentImages[1], serverQuality)[1]).decode(),
                    0
                ]
                server.emit('capture', encoded)
            print('Captured ' + name + '.png')
        return True
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))
        return False
def captureFull(sendServer: bool):
    name = str(round(time.time()*1000)) + '-f'
    cv2.imwrite('image_out/' + name + '.png', numpy.concatenate((currentRawImages[0], currentRawImages[1]), axis=1))
    if sendServer:
        server.emit('message', 'Captured ' + name + '.png')
        encoded = [
            base64.b64encode(cv2.imencode('.jpg', currentRawImages[0], serverQuality)[1]).decode(),
            base64.b64encode(cv2.imencode('.jpg', currentRawImages[1], serverQuality)[1]).decode(),
            0
        ]
        server.emit('capture', encoded)
    print('Captured ' + name + '.png')

# save a stream of images at 10 fps
streamThread = None
streaming = False
totalCaptured = 0
streamFiltering = False
streamServing = False
streamSaving = False
def startSaveStream(filter: bool, sendServer: bool):
    global streamThread, streaming, streamServing, streamFiltering, streamSaving
    if not streaming:
        streaming = True
        streamFiltering = filter
        streamSaving = True
        streamServing = sendServer
        name = str(round(time.time()*1000))
        if filter:
            os.mkdir('./filtered_out/' + name)
        else:
            os.mkdir('./image_out/' + name)
        def loop():
            global streaming, totalCaptured
            try:
                index = 0
                while streaming:
                    start = time.time()
                    if filter:
                        filteredImgs = [cv2.merge(converter.filter(read()[0])), cv2.merge(converter.filter(read()[1]))]
                        cv2.imwrite('filtered_out/' + name + '/' + str(index) + '.png', numpy.concatenate((filteredImgs[0], filteredImgs[1]), axis=1))
                        if sendServer:
                            encoded = [
                                base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                                base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode(),
                                1
                            ]
                            server.emit('capture', encoded)
                    else:
                        cv2.imwrite('image_out/' + name + '/' + str(index) + '.png', numpy.concatenate((currentImages[0], currentImages[1]), axis=1))
                        if sendServer:
                            encoded = [
                                base64.b64encode(cv2.imencode('.jpg', currentImages[0], serverQuality)[1]).decode(),
                                base64.b64encode(cv2.imencode('.jpg', currentImages[1], serverQuality)[1]).decode(),
                                0
                            ]
                            server.emit('capture', encoded)
                    totalCaptured += 1
                    time.sleep(max(0.1-(time.time()-start), 0))
                    index += 1
            except Exception as err:
                traceback.print_exc()
                io.error()
                server.emit('programError', str(err))
        streamThread = Thread(target = loop)
        streamThread.start()
        if sendServer:
            server.emit('message', 'Began save stream')
            server.emit('streamState', streamState())
        print('Began save stream')
        return True
    return False
def stopSaveStream():
    global streamThread, streaming, totalCaptured, streamServing
    if streaming and streamSaving:
        streaming = False
        streamThread.join()
        if streamServing:
            server.emit('message', 'Ended save stream:<br>&emsp;Saved ' + str(totalCaptured) + ' images')
            server.emit('streamState', streamState())
        print('Ended save stream:<br>&emsp;Saved ' + str(totalCaptured) + ' images')
        totalCaptured = 0
        return True
    return False
def startStream(filter: bool):
    global streamThread, streaming, streamServing, streamFiltering, streamSaving
    if not streaming:
        streaming = True
        streamFiltering = filter
        streamSaving = False
        streamServing = True
        def loop():
            global streaming
            try:
                index = 0
                while streaming:
                    start = time.time()
                    if filter:
                        filteredImgs = [cv2.merge(converter.filter(read()[0])), cv2.merge(converter.filter(read()[1]))]
                        encoded = [
                            base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                            base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode(),
                            1
                        ]
                        server.emit('capture', encoded)
                    else:
                        encoded = [
                            base64.b64encode(cv2.imencode('.jpg', currentImages[0], serverQuality)[1]).decode(),
                            base64.b64encode(cv2.imencode('.jpg', currentImages[1], serverQuality)[1]).decode(),
                            0
                        ]
                        server.emit('capture', encoded)
                    time.sleep(max(0.1-(time.time()-start), 0))
                    index += 1
            except Exception as err:
                traceback.print_exc()
                io.error()
                server.emit('programError', str(err))
        streamThread = Thread(target = loop)
        streamThread.start()
        server.emit('message', 'Began stream')
        server.emit('streamState', streamState())
        print('Began stream')
        return True
    return False
def stopStream():
    global streamThread, streaming, streamServing
    if streaming and not streamSaving:
        streaming = False
        streamThread.join()
        if streamServing:
            server.emit('message', 'Ended stream')
            server.emit('streamState', streamState())
        print('Ended stream')
        return True
    return False
def streamState():
    return [streaming, streamFiltering, streamSaving]

thread = Thread(target = __capture)
thread.start()