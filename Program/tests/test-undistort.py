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

img = cv.imread('distorted.png')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Find the chess board corners
ret, corners = cv.findChessboardCorners(gray, (7,6), None)

# If found, add object points, image points (after refining them)
if ret == True:
    objpoints.append(objp)

corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
imgpoints.append(corners2)

# Draw and display the corners
cv.drawChessboardCorners(img, (7,6), corners2, ret)

# cv.imwrite('distorted-corners.png', img)

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

h, w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

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
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('undistorted-remap-cropped.png', dst)