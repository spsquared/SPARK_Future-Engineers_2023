<div align=center>

![banner](./img/banner.png)

</div>

***

**Official GitHub repository for WRO USA team SPARK Future Engineers 2023. All code, documentation, and files are located here.**

Located below is the documentation, and a link to the build instructions.

***

# Contents
* [Hardware Overview](#the-hardware)
    * [Parts List](#parts-list)
    * [Assembly Instructions & Diagrams](#assembly)
    * [Photos](#photos)
* [Software Overview](#the-software)
    * [Operating System](#operating-system)
    * [Programming Language](#programming-language)
    * [IO](#io)
    * [Image Processing and Predictions](#image-predictions)
        * [TBD](/)
    * [SPARK Control Panel](#spark-control)
* [Team Photos](#team-photos)
* [Demonstration Video](#demonstration-video)
* [LiPo Battery Safety Notice](#lipo-battery-safety-notice)

***

# **The Hardware**

## Parts List
* TBD

*link to CAD files used + Onshape link*

## Assembly

*designed in-house!*

#### **For a detailed build guide, go to [ASSEMBLY.md](./ASSEMBLY.md)**

Here is a simple electromechanical schematic for how the electronics are wired:

![Schematic](./img/docs/electromechanical-schematic.png)

***

## Photos
| | |
| ------------------------- | --------------------------- |
| ![front](./img/docs/front.png) | ![back](./img/docs/back.png)     |
| ![left](./img/docs/left.png)   | ![right](./img/docs/right.png)   |
| ![top](./img/docs/top.png)     | ![bottom](./img/docs/bottom.png) |

***

# **The Software**

## **Operating System**

We used Jetson Nano's operating system, which is Ubuntu 18.04. It has been changed to text-only mode to remove the unneccesary GUI. We also added a startup script ([see "Board Setup" in Assembly.md](./ASSEMBLY.md#board-setup-sshfs-and-static-ip)) to run the program on startup, which waits for a button press before running the program.

## **Programming Language**

All our code is in python (except the SPARK Control Panel and SPARK Randomizer, those are HTML/JS/CSS applications used for development). We use *add list*.

The **entire** `Program` directory must be uploaded in order for the program to run. Make sure the directory in `path` in `/Program/IO/io.py` is set correctly (you can use any existing directory with a `lock.txt`, but the uploaded folder is recommended)

Example:

```
path = '/home/nano/Documents/SPARK_FutureEngineers_2023/'
```

## **IO**

*detail IO processes (camera input, motor output)

***

## **Image Predictions**

All the code for image filtering and predictions can be found in `/Program/AI/filter.py`.

### **Image Preprocessing**

*TBD*

### **Image Predictions**

*TBD*

#### **subsection**

*TBD*

***

## **SPARK Control**

***NEEDS UPDATING***

SPARK Control is our own testing and debugging software. It consists of a WebSocket server running on the Jetson NANO, and a local HTML document on our computers. The page uses a WebSocket connection to communicate with the server. The server can broadcast and recieve data in the form of JSON strings, which allows for the differentiation of events and more complex data transfers. The system is modular and is simple to use. As long as the data can be converted to JSON, it can be sent. Broadcasting is as simple as specifying an event name and some data to be sent. To recieve messages, it is possible to add an event listener, which is a function that is run when the specified event is recieved.

The client control panel consists of a log, which is appended to by the `message` event; filter tuning sliders for changing the ranges of the image preprocessor; capture buttons to save and stream raw and filtered images, and the ability to control the vehicle when running in manual drive mode. The data display can show raw and filtered image streams from the car's camera, visualize the detected blobs and wall heights, and display output data from the code. By default, the last 500 frames of data are saved in history and can be replayed for debugging.

<div align=center>

![SPARK Control Panel](./img/docs/SPARK_Control.png)

</div>

To connect to the robot, obtain the IP address (set to static in the assembly instructions) of the robot, and open `/SPARK-Control/index.js`, and change line 1's value to the ip.

Example:

```
const ip = '192.168.1.151';
```

It's possible to use SPARK Control to change the filter colors to adjust to the environment. Simply change the HSV sliders and use the "View Filtered Image" button to see the effects of your changes. Afterwards locate the color assignments in `/Program/AI/filter.py` and change them to match your environment.

Example:

```
rm = redMin = (0, 95, 75)
rM = redMax = (25, 255, 255)
gm = greenMin = (30, 30, 40)
gM = greenMax = (110, 255, 255)
bm = blueMin = (90, 80, 70)
bM = blueMax = (140, 255, 255)
```

You can update the defaults in `/SPARK-Control/index.js` as well in `initcolors`

Example:

```
let initcolors = [
    [
        25, 255, 255,
        0, 95, 75
    ],
    [
        110, 255, 255,
        30, 30, 40
    ],
    [
        140, 255, 255,
        90, 80, 70
    ],
];
```

**Don't forget to upload the `Program` folder again!**

***

# Team Photos

*still have to take photos*
![rick astley](./SPARK-Util/SPARK-Control/rickastley.png)

***

# **Demonstration Video**

*still have to create robot*

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