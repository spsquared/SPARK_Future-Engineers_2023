<div align=center>

![banner](./img/banner.png)

</div>

***

**Official GitHub repository for WRO USA Future Engineers team SPARK 2023. All code, documentation, and files are located here.**

***

## For Judges

If you're a judge, we ask that you don't judge our documentation just yet. We've still got some rough edges to smooth out and a bit more detail to add. Thank you!

# Contents
* [High-Level Overview](#high-level-overview)
* [Hardware](#hardware)
    * [Assembly Instructions & Diagrams](#assembly)
    * [Photos](#photos)
* [Uploading Programs](#uploading-programs)
* [Calibration](#calibration)
* [Software](#software)
    * [Operating System](#operating-system)
    * [Programming Language](#programming-language)
    * [Code Documentation](#code-documentation)
    * [SPARK Utilities](#spark-utilities)
        * [Setup Instructions](#using-spark-utilities)
        * [SPARK Control Panel](#spark-control-panel)
        * [Using SPARK Control Panel](#using-spark-control-panel-to-change-parameters)
* [Team Photos!!](#team-photos)
* [Demonstrations](#demonstration-video)
* [LiPo Battery Safety Notice](#lipo-battery-safety-notice)

***

# High-Level Overview

SPARK G2 consists of a 3D-printed chassis with off-the-shelf components mounted to it, like the motors, cameras, and controller boards. For a full component list, see [ASSEMBLY.md](./ASSEMBLY.md#parts-list). CAD models can be found in `/dist/3d-models/`, and have all been [modeled in Onshape here](https://cad.onshape.com/documents/82dd14d30b814e8846567203/w/34e1b6a4058ed5fbde8ef66a/e/47aa4028e09ec17a24a63590).

![SPARK G2 chassis with electronics in CAD software](./img/docs/cad-car.png)

The chassis consists of a lower base with vertical walls to mount the rear axle and upper platforms. It has space for the battery and an ESC (electronic speed controller) bay in the rear, and a compartment in the front for the steering mechanism. The rear axle is sourced from the Atom 2 GT12 pan car kit by Schumacher, and is mounted vertically to save space.

The electronics platforms sit on top of the chassis base, and the main platform is also a structural component that provides rigidity to the chassis. Because the electronics are on top, they are easily accessible and wiring is fairly simple. The only exceptions are the ESC, which is in the rear, and the IMU (inertial measurement unit, used for measuring angles and velocity).

| Chassis base with rear axle and steering           | Chassis base and platforms, without camera tower            |
| -------------------------------------------------- | ----------------------------------------------------------- |
| ![Lower chassis base](./img/docs/chassis-base.png) | ![Chassis with platforms](./img/docs/chassis-platforms.png) |

One major physical change is the addition of a second IMX219 wide-angle camera to the front of the car. Both cameras are angled 30 degrees to either side, with a field of view of 150 degrees for each camera. The cameras are mounted on a slider to ensure the accuraccy of the [distance calculations in the algorithm](./CODE.md#merge-contours--wall-lines).

![Cameras top-down](./img/docs/camera-angles.png)

include diagram of hardware and relationships (what communicates with what to do what)

quick overview of algorithm (scans images, describe what is used to extract data, and generally what it does with that data)

***

# Hardware

## ASSEMBLY

Shortened assembly instructions:
1. Print 3D models
2. Assemble rear axle
3. Solder electronics
4. Assemble steering mechanism
5. Attach main platform
6. Attach electronics
7. Attach upper platform

#### **For an actual build guide, go to [Assembly.md](./Assembly.md)**

Here is a simple schematic for how the electronics are wired:

![Wiring schematic](./img/docs/wiring-schematic.png)

## Photos
|                                |                                  |
| ------------------------------ | -------------------------------- |
| ![front](./img/docs/front.jpg) | ![back](./img/docs/back.jpg)     |
| ![left](./img/docs/left.jpg)   | ![right](./img/docs/right.jpg)   |
| ![top](./img/docs/top.jpg)     | ![bottom](./img/docs/bottom.jpg) |

***

# Uploading Programs

Make sure you have gone through the [Jetson Nano setup](./ASSEMBLY.md#jetson-nano-setup) steps and set your static IP, have some form of sshfs, and created the program directory. To upload the program, simply copy the contents of the "Program" into the remote directory. **Do not delete the previous directory; you will have to re-install packages!**

# Calibration

@maitian fix the calibration code so it doesn't try to access folders that don't exist
also which iamges.ipynb is it and why is everything so disorganized

***

# Software

## Operating System

We used the Jetson Nano's existing operating system, which is Ubuntu 18.04 with Jetpack. It has been changed to text-only mode to remove the unneccesary GUI. We also added a startup script ([see "Board Setup" in ASSEMBLY.md](./ASSEMBLY.md#board-setup-sshfs-and-static-ip)) to run the program on startup, which waits for a button press before running the program.

***

## Programming Language

All our code is in python (except the SPARK Control Panel and SPARK Randomizer, those are HTML/JS/CSS applications used for development).

Dependencies:
* Jetson-GPIO
* jetcam
* numpy
* cv2
* adafruit-servokit
* adafruit-circuitpython-mpu6050
* python-socketio
* math
* asyncio
* typing
* traceback
* os
* base64
* time
* threading

The **entire** `Program` directory must be uploaded in order for the program to run. Ensure the `path` constant in `startup.py` is defined properly.

Example:

```
path = '/home/nano/Documents/SPARK_FutureEngineers_2023/'
```

***

## Code Documentation

See [Code.md](./CODE.md).

***

## SPARK Utilities

We've created some applications to make running and debugging more streamlined. There are two main tools: [SPARK Control Panel](#spark-control-panel) and [SPARK Randomizer](#spark-randomizer).

#### Using SPARK Utilities

SPARK Utilities require a local server to load resources from. The runner can be found in `./SPARK-Util/` in the form of a [.bat](./SPARK-Util/static.bat) and a [Node.js JavaScript](./SPARK-Util/static.js). **You need [Node.js installed](https://nodejs.org/en/download) to use these tools!** Run the runners and navigate to [`localhost:8081`](localhost:8081) in your browser. It should automatically redirect you to the SPARK Control Panel. To open the Randomizer you can navigate to [`localhost:8081/SPARK-Randomiser`](localhost:8081/SPARK-Randomiser). (For whatever reason, the randomizer path is spelled in the british locale)

#### SPARK Control Panel

SPARK Control Panel is our own testing and debugging software. It allows us to log detailed information about the program's data and present it in a graphical format. SPARK Utilities work wirelessly, so as long as the network is configured correctly (see [ASSEMBLY.md](./ASSEMBLY.md#setup-for-spark-control-panel)) SPARK Control Panel can communicate with the robot.

<div align=center>

![SPARK Control Panel](./img/docs/spark-control.png)

</div>

It contains a dropdown to [modify the filter items on-the-fly](#using-spark-control-panel-to-change-parameters)

*Note: SPARK Control Panel is not necessary and competition runs have this feature turned off to reduce latency.*

We recently added a feature that allows us to remotely run the program from the Control Panel, meaning no SSH is required to run the program.

#### Using SPARK Control Panel to Change Parameters

It's possible to use SPARK Control to change the filter colors to adjust to the environment. Simply open the dropdown menu above the map on the right-hand side of the screen, change the HSV sliders, and click the "Capture" button with the "Filter" option enabled on to see the effects of your changes. Afterwards locate the color assignments in `/Program/Controller/converter.py` and change them to match your environment.

Example:

```
rm = redMin = (0, 95, 75)
rM = redMax = (25, 255, 255)
gm = greenMin = (30, 30, 40)
gM = greenMax = (110, 255, 255)
```

You can update the defaults in `/SPARK-Control/index.js` as well in `initcolors`

Example:

```
const initcolors = [
    [
        [ 25, 255, 255 ],
        [ 0, 95, 75 ]
    ],
    [
        [ 110, 255, 255 ],
        [ 30, 30, 40 ]
    ],
];
```

**Don't forget to upload the `Program` folder again!**

#### SPARK Randomizer

SPARK Randomizer is a tool to use when the card-drawing, coin-flipping, headache-inducing randomizing system is too much to handle. SPARK Randomizer generates valid cases (as long as the right button is clicked) according to the 2022 rules.

<div align=center>

![SPARK Randomizer](./img/docs/spark-randomizer.png)

</div>

***

# Team Photos

![Team Photo](./img/team-photo.jpg)
![Rickroll](./img/rickroll.jpg)

***

# Demonstration Videos

UPDATE!!

[![WRO 2023 Future Engineers US East Coast - Demonstration Run - No Traffic Signals](./img/docs/thumbnail0.jpg)](https://youtu.be/9aOxgYunco4)
[![WRO 2023 Future Engineers US East Coast - Demonstration Run - Traffic Signals](./img/docs/thumbnail1.jpg)](https://youtu.be/JWf80Lf_OrA)

***

# LiPo Battery Safety Notice

While LiPo batteries are the safest form of portable, affordable, high density energy storage, there are still precautions to be taken when working with them. Lithium is a highly volatile element, and will react with the water vapor in the air if exposed to it.

1. **Do not** puncture, deform, short, or heat LiPo batteries above 26° C (80° F) (299.15 K)
2. Store and charge LiPos in a *fireproof container* **away** from flammable materials and water
3. **NEVER** charge a swollen or damaged battery (e.g. damaged leads, swelling of cells, puncture in wrapping)
4. **NEVER** leave a charging battery unattended
5. Only charge LiPo batteries with chargers *designed for LiPo batteries*
6. Dropping a battery can cause sufficient damage to rupture a cell and cause shorts
7. Overdischarging a LiPo battery can cause **permanent damage**

If a LiPo battery goes below its minimum voltage (stated in the manual included or 3.3v multiplied by the amount of cells connected in series) it can cause **permanent internal damage**. This damage is not visible until after further use, when it can swell, or potentially burst and **cause a FIRE**.

**Read all safety notes and instructions included with LiPo batteries before use.**

### For a more detailed LiPo safety manual there is one on [Tenergy Power](https://power.tenergy.com/lipo-safety-warnings/)