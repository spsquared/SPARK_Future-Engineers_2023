<div align=center>

![banner](./img/banner.png)

</div>

# Contents
* [Algorithm](#algorithm)
    * [Outline](#general-outline)
    * [Image Processing](#image-processing)
    * [Simple Driver](#simple-driver)
* [Code Structure](#code-structure)

***

# Algorithm

One  and motion planning. Our code processes the camera image and uses it to find the position of the walls relative to the car and the position of the pillars. Using this information, we can figure out where we are supposed to go next and steer accordingly.

The main consideration for our algorithm is to balance localization accuracy and speed. For localization accuracy, our target is to know which section we are in, and how far away the walls and pillars are. We need to know which section we are in to count how many laps we has completed, and to know when to uturn. We need to know how far away the car is from walls and pillars for collision avoidance.

Our program runs a constant update loop. All controller code can be found in `./Program/Controller/`, and is divided into three main modules: The `converter`, which pre-process images; `slam`, which is a modified SLAM (Simultaneous Localization and Mapping) algorithm with limited landmark locations; and `controller`, divided into `slamcontroller`, `simplecontroller`, and `borkencontroller` (`borkencontroller` has not been tested and `slamcontroller` is currently also borked).

## General Outline
* [Image Processing](#image-processing)
    1. Capture
    2. [Undistort](#undistorting)
    3. [Filter](#filtering)
    4. [Find wall heights](#finding-wall-heights)
    5. [Find contours](#finding-contours)
    6. [Find wall lines](#finding-wall-lines)
    7. [Merge & Convert wall lines and contours](#merge-contours--wall-lines)
* [Simple Driver](#simple-driver)
    1. [Find Car Direction](#finding-car-direction)
    2. [Categorize Walls](#categorizing-walls)
    1. [Find Car Orientation](#finding-car-direction)
    3. [Filter Traffic Signals/Obstacles/Pillars/Game Objects](#filtering-traffic-signals)
    4. [Calculate Steering](#calculating-steering)
* SLAM Driver
    1. Non-functional (but if it works it'll be really cool)
    2. its borken

***

## Image Processing

All code for image processing is in `./Program/Controller/converter.py`.

### Undistorting

Our cameras output a distorted image, so before we can process the image, we must undistort it.



At the start of the program, cv2.fisheye.initUndistortRectifyMap is used with precalculated distortion matrices to create the remaps. See [ASSEMBLY.md](./ASSEMBLY.md#) for instructions on how to get the distortion matrix.

The undistort function calls `cv2.remap` to use the precalculated remaps to undistort the image. A new K matrix is used to partially zoom out the image to prevent too much of the image from being cropped out.

To speed up the undistorting, the top of the image is cropped before undistortion.

*All the results are of the left camera. The same calculations are done on the right camera, it is just not shown.*

Results:

Raw Image:

![raw IMAGE](/img/docs/raw.png)

Undistorted Image:

![cooked IMAGE](/img/docs/undistorted.png)

Because undistorting the image stretches out the edges, there are black gaps in the image on the top and bottom.

### Filtering

We filter the images to isolate the red pillars and green pillars. We also extract the edges of the walls in this step.

Using `cv2.inRange`, a mask for red colors and green colors is created to filter out the traffic lights. For red pillars, two calls of `cv2.inRange` is necessary because the hue value has 180 to be red as well as 0. The two masks created for red are merged together with `cv2.bitwise_or`. The masks are then blurred to remove noise using `cv2.medianBlur`.

Using `cv2.cvtColor`, the image is turned into grayscale, and blurred using `cv2.GaussianBlur`. Then, using `cv2.Canny`, edges are detected in the image.

Results:

Undistored Image:

![cooked IMAGE](/img/docs/undistorted.png)

Red Filtered:

![red filtered](/img/docs/rLeftImg.png)

Green Filtered:

![green filtered](/img/docs/gLeftImg.png)

Edges:

![edges](/img/docs/leftEdgesImg.png)

Combined:

![combined](/img/docs/filtered.png)

### Finding Wall Heights

We find the "height" of the walls, which is the distance between the top edge and bottom edge. This is useful because we can find the distance to any point on the wall if we know the height. The algorithm to do this will be explained in [Merge Contours & Wall Lines](#merge-contours--wall-lines).

The edges image is cropped to remove areas on the top and bottom of the image. The left camera is slightly tilted, so some areas of the left image get set to 0. `numpy.argmax` will find the index of the largest element in each subarray of the image. However, because the image only contains values of 0 and 255, `numpy.argmax` will return the first value which is 255. If no 255 values are found, `numpy.​argmax` returns 0, which is a problem. To fix this, an array filled with a value of 255 is stacked to the end of the image using `numpy.hstack`.

### Finding Contours

Right now, we only have two images containing only red pixels and only green pixels. The purpose of this step is to extract the pillars as an x coordinate, image width, and height. Similarly to the walls, we will be able to calculate the distance from the pillar with this information. The image width is used to remove this portion of the wall heights, as we know it is a pillar and not the wall.

Using `cv2.Canny`, edges can be found on the masked red or green image. To make sure `cv2.Canny` functions, a border is added using `cv2.copyMakeBorder`. The edges are blurred using `cv2.medianBlur`. Now, `cv2.findContours` can be used to find the contours on the image of edges. After finding the contours, using `cv2.contourArea` and `cv2.moments`, we can get the area and position of the contour. If the contour is smaller than `minContourSize`, or if the contour is above the walls, it gets thrown out.

### Finding Wall Lines

This step turns the wall heights into some lines. Each line represents a straight wall. This allows us to seperate the left wall, center wall, and right wall from each other.

To find wall lines, we create a new image with only the bottom of the wall. For every obstacle, the nearby wall heights get set to 0 based on the size of the contour. Creating this image is optimized using `numpy.zeros`. The bottom of the wall is set to 255. We first create a list of indices so we can quickly set all the values to 255.

Using `cv2.HoughLinesP`, we can find lines on this newly created image. After sorting the lines based on the x value, similar slope lines are merged.


Results:

Left Camera:

![Left Contours and Wall Lines](/img/docs/filteredAllLeft.png)

Right Camera:

![Right Contours and Wall Lines](/img/docs/filteredAllRight.png)

### Merge Contours & Wall Lines

We can find the distance to any point on the top of the wall. Diagram 1 is a side view of the camera and the wall. Our cameras are positioned at the same height as the wall, so the top of the wall forms a straight line on the image. In diagram 1, the right line is the wall, which we know is 10cm tall. $d$ is the distance we want to calculate. $newf$ is the new focal length, which we will calculate later. $h$ is the height of the wall in pixels, which we get when we find the wall heights. The two triangles are similar, so $\frac{new f}{h} = \frac{d}{10cm}$. Isolating $d$ gives us $d = \frac{10cm \times newf}{h}$.

To calculate $new f$, we need to know the base focal length. For our undistorted image, we use an approximation of 80px as the base focal length. Diagram 2 is a birds-eye view of the camera. $f$ is the base focal length, and $x$ is the x position of the wall relative to the center. Using the Pythagorean theorem, we get $new f = \sqrt{f^2 + x^2}$.

<div align=center>

![focal length](/img/docs/distance-calc.png)

</div>

Using this algorithm, which is in `getRawDistance`, we can convert the contours into x and y positions relative to the vehicle. For wall lines, we convert each endpoint and connect them together.


*The contours and wall lines are merged from the left and right camera. This is why you see duplicate pillars.*

Results:


Mapped Contours and Wall Lines:

![Mapped Contours and Wall Lines](/img/docs/topview.png)

***

## Simple Driver

All code for the simple driver is in `./Program/Controller/simplecontroller.py`.

### Finding Car Direction

At the start of the program, we need to know if we are going clockwise or counterclockwise. This is done by searching for a jump in the wall. If a jump is detected, it means there is a gap there, allowing us to find the direction.

For the first 9 frames, we search for a jump in the wall. Using `numpy.diff`, we can find differences in the wall heights. After this, we split the two images from both cameras into 4 images. The left camera image gets split at 3/4 and the right camera gets split at 1/4. The left parts are used to detect a gap on the left, while the right parts are used to detect a gap on the right. Now, we use `numpy.argmax` to find the first large difference on all 4 images. We add the difference of the indices for the left and the indices for the right to `carDirectionGuess`. If `carDirectionGuess` is greater than 0, then we are going clockwise, otherwise we are going counterclockwise.

### Categorizing Walls

<!-- UPDATE!!! -->
buh we need the orientation stuff

There are 5 possible categories of walls: Left, Center, Right, Back, and Unknown. The slope of the wall relative to the car is calculated. If the slope is relatively small and in front of the car, the wall gets classified as a center wall. Otherwise, if the slope is small but behind the car, the wall gets classified as Back. If the wall is to the left, it is a left wall, if it is to the right, it is a right wall.

### Filtering Traffic Signals

We find the largest pillar. If there are multiple pillars around the same spot we take the average of their positions.

### Calculating Steering

We calculate the average distance to the left walls, center walls, and right walls. Based on the relative angles of the walls, we can calculate the angle of the car relative to the map. There are 3 cases for steering:

1. Center wall < 110cm
2. We are Uturning
3. Default case

In case 1, if there is no pillar detected, SPARK G2 will keep straight and turn when the center wall is less than 70cm away. If there is a pillar detected, SPARK G2 will turn when the pillar is close enough to pass in front or behind it.

<!-- NOT 3 POINT TURN ANYMORE!!! -->

In case 2, NOTHING BECAUSE ITS NOT 3 POINT TURN OOF uses a precalculated set of instructions for making the 3 point turn. The gyro is used to determine how far we have turned.

In case 3, if there is no pillar detected, SPARK G2 will keep straight. If there is a pillar, it will calculate a tangent to the circle of radius 20cm centered on the pillar. The car calculates the left tangent for green pillars and the right tangent for red pillars. Then, it tries to keep itself pointed towards that tangent point.

***

# Code Structure


Converter.py has all the code for image processing. Converter.py
simplecontroller.py has all the code for the driver.
<!-- talk about how the code is segmented, what modules are made to handle what tasks (not too much detail though) -->