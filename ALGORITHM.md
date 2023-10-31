<div align=center>

![banner](./img/banner.png)

</div>

***

**This file covers the algorithm used for obstacle management.**

***

# Contents
* [**Overview**](#algorithm-overview)
    * [Pseudocode](#pseudocode)
    * [Outline](#outline)
* [**Image Processing**](#image-processing)
* [**Simple Driver**](#simple-driver)

***

# Algorithm Overview

One  and motion planning. Our code processes the camera image and uses it to find the position of the walls relative to the car and the position of the pillars. Using this information, we can figure out where we are supposed to go next and steer accordingly.

The main consideration for our algorithm is to balance localization accuracy and speed. For localization accuracy, our target is to know which section we are in, and how far away the walls and pillars are. We need to know which section we are in to count how many laps we have completed, and to know when to U-turn. We need to know how far away the car is from walls and pillars for collision avoidance.

For motion planning, our controller finds a waypoint based on the pillar position and wall position, and the car will steer toward the waypoint. The waypoint will be updated every iteration. For the U-turn, the car will turn around the first pillar in the section.

Our program runs a constant update loop. All controller code can be found in `./Program/Controller/`, and is divided into three main modules: The `converter`, which pre-process images; `slam`, which is a modified SLAM (Simultaneous Localization and Mapping) algorithm with limited landmark locations; and `controller`, divided into `slamcontroller`, `simplecontroller`, and `borkencontroller` (`borkencontroller` has not been tested and `slamcontroller` is currently also borked).

## Pseudocode

The algorithm part of the code is a loop. For each iteration, it takes images, processes them, and then calculates a steering value.

Each iteration takes about 80ms.

```
while (sections entered != 24): # 24 sections means 3 laps.
    // Image processing for car localization
    Crop the images
    Undistort the images (how to add links to other files?)
    Filter the image
    Find wall heights
    Find contours
    Find wall lines
    Merge and Convert wall lines and contours
    Categorize Walls
    Find Car Orientation
    Filter Pillars
    <!--Car steering control-->
    Find lap direction
    Calculate Steering
```

## Outline
* [**Image Processing**](#image-processing)
    1. [Crop the image](#crop-the-image)
    2. [Undistort](#undistorting)
    3. [Filter](#filtering)
    4. [Find wall heights](#finding-wall-heights)
    5. [Find contours](#finding-contours)
    6. [Find wall lines](#finding-wall-lines)
    7. [Merge & Convert wall lines and contours](#merge-contours--wall-lines)
    8. [Categorize Walls](#categorizing-walls)
    9. [Find Car Orientation](#finding-car-orientation)
    10. [Filter Traffic Signals/Obstacles/Pillars/Game Objects](#filtering-traffic-signals)
* [**Steering and Motion Planning**](#steering-and-motion-planning)
    1. [Find Lap Direction](#finding-lap-direction)
    2. [Calculate Steering](#calculating-steering)

# Image Processing

Steps 1-7 for image processing is in `./Program/Controller/converter.py`.
Steps 8-10 for image processing is in `./Program/Controller/controller.py`.

***

### Crop the image

Because our camera is the same height as the top boundary of the walls, the top of the walls appears as a flat line in the image. We crop out along the top boundary of the wall. This reduces noise in the background, as well as speeding up our processing.

### Undistorting

Because our camera is a fisheye camera (wide angle), our cameras output a distorted image. Before we can process the image, we must undistort it.

At the start of the program, `cv2.fisheye.initUndistortRectifyMap` is used with precalculated distortion matrices to create the remaps. We used a checkerboard image to calculate the distortion matrices D and K. See [SETUP.md](./SETUP.md#) for instructions on how to get the distortion matrix.

The undistort function calls `cv2.remap` to use the precalculated remaps to undistort the image. We scaled up the matrix K to partially zoom out the image to prevent too much of the image from being cropped out.

We present a few examples to explain the processing steps. All the examples are from the left camera. The same calculations are done on the right camera.

| Raw Image                       | Undistorted Image                          |
| ------------------------------- | ------------------------------------------ |
| ![raw IMAGE](/img/docs/raw.png) | ![cooked IMAGE](/img/docs/undistorted.png) |

Because undistorting the image stretches out the edges, there are black gaps in the image on the top and bottom.

In the following image, the distortion is more obvious.

insert image

***

### Filtering

We filter the images to isolate the red pillars and green pillars. We also extract the edges of the walls in this step.

We found that it was easier and more robust to distinguish between very faint green colors and the wall when the image was in HSV mode. HSV stands for Hue-Saturation-Value. Hue is the "color" of the color, going from 0 to 179, covering the rainbow. Saturation is how much of the hue is present, going from 0 to 255, with lower values appearing duller. Value is how dark the color is, from 0 to 255, with lower being darker. The image is converted into HSV mode using `cv2.cvtColor`. ([More information here](https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html))

![HSV Image](/img/docs/HSV.png)

https://en.wikipedia.org/wiki/HSL_and_HSV#/media/File:HSV_color_solid_cylinder_saturation_gray.png

Using `cv2.inRange`, a mask for red colors and green colors is created to filter out the traffic lights. For red pillars, two calls of `cv2.inRange` is necessary because the hue value has 180 to be red as well as 0. The two masks created for red are merged together with `cv2.bitwise_or`. The masks are then blurred to remove noise using `cv2.medianBlur`.

Using `cv2.cvtColor`, the image is turned into grayscale, and blurred using `cv2.GaussianBlur`. Then, using `cv2.Canny`, edges are detected in the image.

Results:
|                                                        |                                                                           |                                                    |
| ------------------------------------------------------ | ------------------------------------------------------------------------- | -------------------------------------------------- |
|                                                        | Undistorted image from previous![cooked IMAGE](/img/docs/undistorted.png) |                                                    |
| Red pillar mask![red filtered](/img/docs/rLeftImg.png) | Green pillar mask![green filtered](/img/docs/gLeftImg.png)                | Wall edge mask![edges](/img/docs/leftEdgesImg.png) |
|                                                        | Combined output to control panel![combined](/img/docs/filtered.png)       |                                                    |

***

### Finding Contours

Right now, we only have two images containing only red pixels and only green pixels. The purpose of this step is to find a bounding box of the red/green pixels to represent the pillars. This bounding box has a center (x,y) coordinate, width, and height. With this information, we can calculate the distance to the top point of the pillar. The algorithm to do this will be explained in [Merge Contours & Wall Lines](#merge-contours--wall-lines).

Using `cv2.Canny`, edges can be found on the masked red or green image. To make sure `cv2.Canny` functions, a border is added using `cv2.copyMakeBorder`. The edges are blurred using `cv2.medianBlur`. Now, `cv2.findContours` can be used to find the contours on the image of edges. After finding the contours, using `cv2.contourArea` and `cv2.moments`, we can get the area and position of the contour. If the contour is smaller than `minContourSize`, or if the contour is above the walls, it gets thrown out.

***

### Finding Wall Heights

We find the "height" of the walls, which is the distance between the top edge and bottom edge. Similarly to the pillars, this information is used later to find the distance from the car to any point on the top boundary of the wall.

The edges image is cropped to remove areas on the top and bottom of the image. The left camera is slightly tilted, so some areas of the left image get set to 0. `numpy.argmax` will find the index of the largest element in each subarray of the image. However, because the image only contains values of 0 and 255, `numpy.argmax` will return the first largest value, which is at the edge of the wall. If no 255 values are found, `numpy.​argmax` returns 0, which is a problem. To fix this, an array filled with a value of 255 is stacked to the end of the image using `numpy.hstack`.

***

### Finding Wall Lines

This step turns the wall heights into some lines. Each line represents a straight wall.

To find wall lines, we create a new image with only the bottom of the wall. For every pillar, the nearby wall heights get set to 0 based on the size of the contour. Creating this image is optimized using `numpy.zeros`. The bottom of the wall is set to 255. We first create a list of indices so we can quickly set all the values to 255.

Using `cv2.HoughLinesP`, we can find lines on this newly created image. After sorting the lines based on the x value, similar slope lines are merged.

Results:

The Wall Lines are the pink lines on the image. The shaded white area are the wall heights.

| Left camera                                                    | Right camera                                                     |
| -------------------------------------------------------------- | ---------------------------------------------------------------- |
| ![Left Contours and Wall Lines](/img/docs/filteredAllLeft.png) | ![Right Contours and Wall Lines](/img/docs/filteredAllRight.png) |

***

### Merge Contours & Wall Lines

We can find the distance to any point on the top of the wall. Diagram 1 is a side view of the camera and the wall. Our cameras are positioned at the same height as the wall, so the top of the wall forms a straight line on the image. In diagram 1, the right line is the wall, which we know is 10cm tall. $d$ is the distance we want to calculate. $newf$ is the new focal length, which we will calculate later. $h$ is the height of the wall in pixels, which we get when we find the wall heights. The two triangles are similar, so $\frac{new f}{h} = \frac{d}{10cm}$. Isolating $d$ gives us $d = \frac{10cm \times newf}{h}$.

To calculate $new f$, we need to know the base focal length. For our undistorted image, we use an approximation of 110px as the base focal length. Diagram 2 is a birds-eye view of the camera. $f$ is the base focal length, and $x$ is the x position of the wall relative to the center. Using the Pythagorean theorem, we get $new f = \sqrt{f^2 + x^2}$.

<div align=center>

![focal length](/img/docs/distance-calc.png)

</div>

Using this algorithm, which is in `getRawDistance`, we can convert the contours into x and y positions relative to the vehicle. For wall lines, we convert each endpoint and connect them together.


**The contours and wall lines are merged from the left and right camera. This is why you see duplicate pillars.**

Results:

| Mapped Contours and Wall Lines                       |
| ---------------------------------------------------- |
| ![Mapped Contours and Wall Lines](/img/docs/map.png) |

***

### Transforming Walls and Pillars

It is important to know which wall is the center wall, the left wall, and the right wall. When the car is straight, the center wall is the wall in front of the car. In the image, the center wall is a horizontal line.

When the car is at an angle, the walls relative to the car will not be perfectly horizontal or perfectly vertical.

| Wall Classification                                      | Angled Walls                               |
| -------------------------------------------------------- | ------------------------------------------ |
| ![Wall Classification](/img/docs/wallClassification.png) | ![Angled Walls](/img/docs/wallsTilted.png) |

In this image to the right, the car sees the center wall at an angle of 45 degrees and the left wall at an angle of 45 degrees. Now, the car doesn't know which wall is the center wall.

To solve this problem, we store the orientation of the car (relative to the mat). Before processing the walls, we rotate them based on the last orientation. This makes it easy to categorize the walls. Updating the orientation is discussed below.

***

### Categorizing Walls

<!-- UPDATE!!! -->
buh we need the orientation stuff

At this step, the wall lines have been turned into line segments that represent the real positions of the walls on the mat.

We have 5 possible categories of Walls: Left, Center, Right, Back, and Unknown. If the wall is perpendicular relative to the driving direction, it is categorized as a center or back wall depending on if it is in front or in the back of the car. If the wall is parallel to the driving direction, it is categorized as a left wall or right wall depending on if it is to the left or to the right of the car.

Now, depending on how slanted the wall is, we can calculate our car orientation. For example, if the center wall is tilted 5 degrees to the right, we know our car is also tilted 5 degrees to the left in addition to the current orientation.

The car orientation is thus updated.

***

### Filtering Traffic Signals

We find the largest pillar. If there are multiple pillars around the same spot we take the average of their positions.

***

# Steering and Motion Planning

All code for the Steering and Motion Planning is in `/Program/Controller/simplecontroller.py`.

***

### Finding Lap Direction

At the start of the program, we need to know if we are going clockwise or counterclockwise. This is done by searching for a jump in the wall. If a jump is detected, it means there is a gap there, allowing us to find the direction.

| Jump in Wall Height                         
| --------------------------------------------
| ![Jump in Wall Height](/img/docs/gap.png) |

For the first 9 frames, we search for a jump in the wall. Using `numpy.diff`, we can find differences in the wall heights. After this, we split the two images from both cameras into 4 images. The left camera image gets split at 3/4 and the right camera gets split at 1/4. The left parts are used to detect a gap on the left, while the right parts are used to detect a gap on the right. Now, we use `numpy.argmax` to find the first large difference on all 4 images. We add the difference of the indices for the left and the indices for the right to `carDirectionGuess`. If `carDirectionGuess` is greater than 0, then we are going clockwise, otherwise we are going counterclockwise.

***

### Calculating Steering

We calculate the average distance to the left walls, center walls, and right walls.

# No Obstacle Challenge

We run the same code, except without any pillar cases.

# Obstacle Challenge
We have 4 states the car can be in.
- Uturning
- In Center Section
- Steering for pillars
- Default case

1. uTurning:

    The car uses the pillar it sees before the uTUrn starts to know which direction to turn. This pillar is stored in `slam.uTurnAroundPillar`. If it is red, we turn counterclockwise around it. If it is green, we turn clcokwise around it. Our steering value is 100 if we are turning clockwise, and -100 if we are turning counterclockwise.

    We use the gyro to estimate that we have turned 180 degrees. When the gyro says the UTurn is done, it goes back to the other states.

2. In Center Section:

    In this section, we have to turn based on the pillar in the next section.

    If there is no pillar, we turn when the centre wall is close enough.

    If there is a red pillar and we are turning clockwise or there is a green pillar and we are turning counterclockwise, we will turn earlier than the pillar to pass on the correct side.

    If there is a green pillar and we are turning clockwise or there is a red pillar and we are turning counterclockwise, we will turn later to pass behind the pillar.

    
    | Red Pillar Turning                        |Green Pillar Turning
    | --------------------------------------------| --
    | ![Red Pillar Turning](/img/docs/redTurning.png) |![Green Pillar Turning](/img/docs/greenTurning.png) |

3. Steering for Pillars:

    The car will calculate a waypoint 10cm behind the pillar and 15cm to the left or right of the pillar and steer towards this waypoint. If we are already to the right of a red pillar or to the left of a green pillar, the car will instead use the default case.

4. Default Case:

    The car will check if the left wall or right wall is too close. If it is, it will steer away from the wall. If it is not, the car will try to keep its orientation aligned with the driving direction.



***