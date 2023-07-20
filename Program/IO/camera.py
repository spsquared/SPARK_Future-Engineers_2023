from Controller import converter
from Util import server
# from jetcam.csi_camera import CSICamera
from IO.nvcamera import NVCamera
from IO import io
import traceback
import cv2
import os
from threading import Thread
import base64
import time
import numpy

# wrapper for camera functions

__imageWidthRaw = 1088
__imageHeightRaw = 616
__imageWidth = 544
__imageHeight = 308

# __camera0 = CSICamera(capture_device=0, width=__imageWidthRaw, height=__imageHeightRaw, capture_width=3264, capture_height=1848, capture_fps=28)
# __camera1 = CSICamera(capture_device=1, width=__imageWidthRaw, height=__imageHeightRaw, capture_width=3264, capture_height=1848, capture_fps=28)
__camera0 = NVCamera(sid=0, width=__imageWidthRaw, height=__imageHeightRaw)
__camera1 = NVCamera(sid=1, width=__imageWidthRaw, height=__imageHeightRaw)
__running = True
__currentRawImages = [None, None]
__currentImages = [None, None]
__thread = None

__camera0.__running = True
__camera1.__running = True
def __update():
    try:
        global __running, __camera0, __camera1, __currentImages
        # update loop that constantly updates the most recent image which can be read at any time
        while __running:
            start = time.time()
            __currentRawImages[0] = __camera0.read()
            __currentRawImages[1] = __camera1.read()
            __currentImages[0] = downscale(__currentRawImages[0])
            __currentImages[1] = downscale(__currentRawImages[1])
            time.sleep(max(0.02-(time.time()-start), 0))
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))

def stop():
    global __running, __camera0, __camera1, __thread
    if __running:
        __running = False
        __thread.join()
        __camera0.__running = False
        __camera1.__running = False

# read current image
def read():
    global __currentImages
    return __currentImages

def downscale(img: numpy.ndarray):
    return cv2.resize(img, (__imageWidth, __imageHeight), interpolation=cv2.INTER_NEAREST)

# make folder if doesn't exist
if not os.path.exists('image_out/'):
    os.mkdir('image_out/')
if not os.path.exists('filtered_out/'):
    os.mkdir('filtered_out/')

__serverQuality = [int(cv2.IMWRITE_JPEG_QUALITY), 10]

# single image save
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
                    1,
                    0
                ]
                server.emit('capture', encoded)
            print('Captured (filtered) ' + name + '.png')
        else:
            cv2.imwrite('image_out/' + name + '.png', numpy.concatenate((__currentImages[0], __currentImages[1]), axis=1))
            if sendServer:
                server.emit('message', 'Captured ' + name + '.png')
                encoded = [
                    base64.b64encode(cv2.imencode('.jpg', __currentImages[0], __serverQuality)[1]).decode(),
                    base64.b64encode(cv2.imencode('.jpg', __currentImages[1], __serverQuality)[1]).decode(),
                    0,
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
    cv2.imwrite('image_out/' + name + '.png', numpy.concatenate((__currentRawImages[0], __currentRawImages[1]), axis=1))
    if sendServer:
        server.emit('message', 'Captured ' + name + '.png')
        encoded = [
            base64.b64encode(cv2.imencode('.jpg', __currentRawImages[0], __serverQuality)[1]).decode(),
            base64.b64encode(cv2.imencode('.jpg', __currentRawImages[1], __serverQuality)[1]).decode(),
            0,
            0
        ]
        server.emit('capture', encoded)
    print('Captured ' + name + '.png')

# save a stream of images at 10 fps
__streamThread = None
__streaming = False
__totalCaptured = 0
__streamFiltering = False
__streamServing = False
__streamSaving = False
def startSaveStream(filter: bool, sendServer: bool):
    global __streamThread, __streaming, __streamServing, __streamFiltering, __streamSaving
    if not __streaming:
        __streaming = True
        __streamFiltering = filter
        __streamSaving = True
        __streamServing = sendServer
        name = str(round(time.time()*1000))
        if filter:
            os.mkdir('./filtered_out/' + name)
        else:
            os.mkdir('./image_out/' + name)
        def loop():
            global __streaming, __totalCaptured
            try:
                index = 0
                while __streaming:
                    start = time.time()
                    if filter:
                        filteredImgs = [cv2.merge(converter.filter(read()[0])), cv2.merge(converter.filter(read()[1]))]
                        cv2.imwrite('filtered_out/' + name + '/' + str(index) + '.png', numpy.concatenate((filteredImgs[0], filteredImgs[1]), axis=1))
                        if sendServer:
                            encoded = [
                                base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                                base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode(),
                                1,
                                1
                            ]
                            server.emit('capture', encoded)
                    else:
                        cv2.imwrite('image_out/' + name + '/' + str(index) + '.png', numpy.concatenate((__currentImages[0], __currentImages[1]), axis=1))
                        if sendServer:
                            encoded = [
                                base64.b64encode(cv2.imencode('.jpg', __currentImages[0], __serverQuality)[1]).decode(),
                                base64.b64encode(cv2.imencode('.jpg', __currentImages[1], __serverQuality)[1]).decode(),
                                0,
                                1
                            ]
                            server.emit('capture', encoded)
                    __totalCaptured += 1
                    time.sleep(max(0.1-(time.time()-start), 0))
                    index += 1
            except Exception as err:
                traceback.print_exc()
                io.error()
                server.emit('programError', str(err))
        __streamThread = Thread(target = loop)
        __streamThread.start()
        if sendServer:
            server.emit('message', 'Began save stream')
            server.emit('streamState', streamState())
        print('Began save stream')
        return True
    return False
def stopSaveStream():
    global __streamThread, __streaming, __totalCaptured, __streamServing
    if __streaming and __streamSaving:
        __streaming = False
        __streamThread.join()
        if __streamServing:
            server.emit('message', 'Ended save stream:<br>&emsp;Saved ' + str(__totalCaptured) + ' images')
            server.emit('streamState', streamState())
        print('Ended save stream:<br>&emsp;Saved ' + str(__totalCaptured) + ' images')
        __totalCaptured = 0
        return True
    return False
def startStream(filter: bool):
    global __streamThread, __streaming, __streamServing, __streamFiltering, __streamSaving
    if not __streaming:
        __streaming = True
        __streamFiltering = filter
        __streamSaving = False
        __streamServing = True
        def loop():
            global __streaming
            try:
                index = 0
                while __streaming:
                    start = time.time()
                    if filter:
                        filteredImgs = [cv2.merge(converter.filter(read()[0])), cv2.merge(converter.filter(read()[1]))]
                        encoded = [
                            base64.b64encode(cv2.imencode('.png', filteredImgs[0])[1]).decode(),
                            base64.b64encode(cv2.imencode('.png', filteredImgs[1])[1]).decode(),
                            1,
                            1
                        ]
                        server.emit('capture', encoded)
                    else:
                        encoded = [
                            base64.b64encode(cv2.imencode('.jpg', __currentImages[0], __serverQuality)[1]).decode(),
                            base64.b64encode(cv2.imencode('.jpg', __currentImages[1], __serverQuality)[1]).decode(),
                            0,
                            1
                        ]
                        server.emit('capture', encoded)
                    time.sleep(max(0.1-(time.time()-start), 0))
                    index += 1
            except Exception as err:
                traceback.print_exc()
                io.error()
                server.emit('programError', str(err))
        __streamThread = Thread(target = loop)
        __streamThread.start()
        server.emit('message', 'Began stream')
        server.emit('streamState', streamState())
        print('Began stream')
        return True
    return False
def stopStream():
    global __streamThread, __streaming, __streamServing
    if __streaming and not __streamSaving:
        __streaming = False
        __streamThread.join()
        if __streamServing:
            server.emit('message', 'Ended stream')
            server.emit('streamState', streamState())
        print('Ended stream')
        return True
    return False
def streamState():
    return [__streaming, __streamFiltering, __streamSaving]

__thread = Thread(target = __update)
__thread.start()