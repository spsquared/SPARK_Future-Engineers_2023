import traitlets
import cv2

class NVCamera(traitlets.HasTraits):
    sid: traitlets.Integer()
    width = traitlets.Integer()
    height = traitlets.Integer()

    def __init__(self, sid, width, height):
        self.__sid = sid
        self.__width = width
        self.__height = height
        try:
            self.__capture = cv2.VideoCapture(self.__gst_str(), cv2.CAP_GSTREAMER)
            re, img = self.__capture.read()
            if not re:
                raise RuntimeError('Could not read image from camera.')
        except:
            raise RuntimeError('Could not initialize camera.')

    def read(self):
        try:
            re, img = self.__capture.read()
            if not re:
                raise RuntimeError('Could not read image from camera.')
            return img
        except:
            raise RuntimeError('Could not read image from camera.')
    
    def stop(self):
        self.__capture.release()
    
    def __gst_str(self):
        return 'nvarguscamerasrc sensor-id=%d ! video/x-raw(memory:NVMM), width=3264, height=1848, format=(string)NV12, framerate=(fraction)28/1 ! nvvidconv ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! videoconvert ! appsink' % (
                self.__sid, self.__width, self.__height)