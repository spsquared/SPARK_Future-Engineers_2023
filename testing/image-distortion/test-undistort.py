# https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

import numpy as np
import cv2 as cv
import glob

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('./calibration/*.png')
for fname in images:
    print('getting points from ' + fname)
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (4,4), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

    corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
    imgpoints.append(corners2)

print('calibrating')

# calibrate the camera
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

h, w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

np.savetxt('matrix.txt', mtx)
np.savetxt('distortion.txt', dist)

print('undistorting')

# try it on some stuff
img = cv.imread('./distorted.png')

# using cv2.undistort()
dst = cv.undistort(img, mtx, dist, None, newcameramtx)
x, y, w, h = roi
cv.imwrite('undistorted-cv2undistort.png', dst)
dst = dst[y:y+h, x:x+w]
cv.imwrite('undistorted-cv2undistort-cropped.png', dst)

# using remap function
mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
cv.imwrite('undistorted-remap.png', dst)
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('undistorted-remap-cropped.png', dst)

# calculate accuracy
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
    mean_error += error

fd = open('error.txt')
fd.write(mean_error)
fd.close()