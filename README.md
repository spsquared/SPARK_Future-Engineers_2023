<div align=center>

![banner](./img/banner.png)

</div>

***

**Official GitHub repository for WRO USA Future Engineers team SPARK 2023. All code, documentation, and files are located here.**

***

# Contents
* [Hardware](#hardware-documentation)
    * [Parts List](#parts-list)
    * [Assembly Instructions & Diagrams](#assembly)
    * [Photos](#photos)
* [Software](#software-documentation)
    * [Operating System](#operating-system)
    * [Programming Language](#programming-language)
    * [IO](#io)
    * [Input Processing](#input-processing)
        * [TBD](/)
    * [SPARK Control Panel](#spark-control)
* [Team Photos!!](#team-photos)
* [Demonstrations](#demonstration-video)
* [LiPo Battery Safety Notice](#lipo-battery-safety-notice)

***

# Hardware Documentation

## Assembly

Shortened assembly instructions:
1. Print 3D models
2. Assemble rear axle
3. Solder electronics
4. Assemble steering mechanism
5. Attach main platform
6. Attach electronics
7. Attach upper platform

#### **For an actual build guide, go to [ASSEMBLY.md](./ASSEMBLY.md)**

Here is a simple schematic for how the electronics are wired:

![Schematic](./img/docs/schematic.png)

***

## Photos
|                                |                                  |
| ------------------------------ | -------------------------------- |
| ![front](./img/docs/front.png) | ![back](./img/docs/back.png)     |
| ![left](./img/docs/left.png)   | ![right](./img/docs/right.png)   |
| ![top](./img/docs/top.png)     | ![bottom](./img/docs/bottom.png) |

***

# Uploading & Using SPARK-Util tools

Make sure you have gone through the [Jetson Nano setup](./ASSEMBLY.md#jetson-nano-setup) steps and set your static IP, have some form of sshfs, and created the program directory. To upload the program, simply copy the contents of the "Program" into the remote directory. **Do not delete the previous directory; you will have to re-install packages!**



# Software Documentation

## Operating System

We used the Jetson Nano's existing operating system, which is Ubuntu 18.04 with Jetpack. It has been changed to text-only mode to remove the unneccesary GUI. We also added a startup script ([see "Board Setup" in Assembly.md](./ASSEMBLY.md#board-setup-sshfs-and-static-ip)) to run the program on startup, which waits for a button press before running the program.

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

The **entire** `Program` directory must be uploaded in order for the program to run.

Example:

```
path = '/home/nano/Documents/SPARK_FutureEngineers_2023/'
```

## Code Documentation

See [DOCS.md](./DOCS.md).

## SPARK Control

***NEEDS UPDATING***

SPARK Control Panel is our own testing and debugging software.

<div align=center>

![SPARK Control Panel](./img/docs/SPARK_Control.png)

</div>

#### Setup

SPARK Control Panel requires some setup to use. See [Assembly.MD](./Assembly.md#setup-for-spark-control-panel) for more information.

It's possible to use SPARK Control to change the filter colors to adjust to the environment. Simply change the HSV sliders and click the "Capture" button with the "Filter" option on to see the effects of your changes. Afterwards locate the color assignments in `/Program/Controller/converter.py` and change them to match your environment.

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

***

# Team Photos

![Team Photo](./img/team-photo.HEIC)
![Rickroll](./img/rickroll.HEIC)

***

# Demonstration Video

# LiPo Battery Safety Notice

While LiPo batteries are the safest form of portable, affordable, high density energy storage, there are still precautions to be taken when working with them. Lithium is a highly volatile element, and will react with the water vapor in the air if exposed to it.

1. **Do not** puncture, deform, short, or heat LiPo batteries above 80° F
2. Store and charge LiPos in a *fireproof container* **away** from flammable materials and water
3. **NEVER** charge a swollen or damaged battery (e.g. damaged leads, swelling of cells, puncture in wrapping)
4. **NEVER** leave a charging battery unattended
5. Only charge LiPo batteries with chargers *designed for LiPo batteries*
6. Dropping a battery can cause sufficient damage to rupture a cell and cause shorts
7. Overdischarging a LiPo battery can cause **permanent damage**

If a LiPo battery goes below its minimum voltage (stated in the manual included or 3.3v multiplied by the amount of cells connected in series) it can cause **permanent internal damage**. This damage is not visible until after further use, when it can swell, or potentially burst and **cause a FIRE**.

**Read all safety notes and instructions included with LiPo batteries before use.**

### For a more detailed LiPo safety manual there is one on [Tenergy Power](https://power.tenergy.com/lipo-safety-warnings/)