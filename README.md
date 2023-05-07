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
***INCOMPLETE***

* Parts from [Schumacher Atom 2 S2 1/12 GT12 Competition Pan Car Kit](https://www.amainhobbies.com/schumacher-atom-2-s2-1-12-gt12-competition-pan-car-kit-schk179/p1055346) (not sponsored)
    * [Drive Pod Parts](https://www.racing-cars.com/gt12/atom-2/atom-2-parts=chassis-parts/s2-pod-parts-atom-2-u7905?returnurl=%2fgt12%2fatom-2%2fatom-2-parts%3dchassis-parts%2f)
    * [Assembled Differential](https://www.racing-cars.com/gt12/atom-2/atom-2-parts=transmission/assembled-diff-atom-2-u7713?returnurl=%2fgt12%2fatom-2%2fatom-2-parts%3dtransmission%2f)
    * [Left Drive Wheel Clamp](https://www.racing-cars.com/gt12/atom-2/atom-2-parts=transmission/lh-drive-clamp-a1-a2-u4853?returnurl=%2fgt12%2fatom-2%2fatom-2-parts%3dtransmission%2f)
    * Transmission Housings: [Left Side](https://www.racing-cars.com/gt12/atom-2/atom-2-parts=transmission/trans-housing-lh-a2-3-e2-e5-u7483?returnurl=%2fgt12%2fatom-2%2fatom-2-parts%3dtransmission%2f), [Right Side](https://www.racing-cars.com/gt12/atom-2/atom-2-parts=transmission/trans-housing-rh-a2-3-e2-e3-e4-u7484?returnurl=%2fgt12%2fatom-2%2fatom-2-parts%3dtransmission%2f)
    * [Ride Height Adjusters](https://www.racing-cars.com/gt12/atom-2/atom-2-parts=suspension/ride-height-adjusters-0-25-1-75-4prs-e1-5-ic-2-a3-u4973?returnurl=%2fgt12%2fatom-2%2fatom-2-parts%3dsuspension%2f) (use 1.75mm)
    * 2x [LP Front Axle](https://www.racing-cars.com/gt12/atom-2/atom-2-parts=suspension/low-profile-front-axle-a1-a3-u7302?returnurl=%2fgt12%2fatom-2%2fatom-2-parts%3dsuspension%2f)
    * [Rear Axle Ball Bearings](https://www.racing-cars.com/gt12/atom-2/ball-bearing-1-4x3-8x1-8-flanged-yellow-pr-u4980?returnurl=%2fgt12%2fatom-2%2f)
    * [Front Axle Ball Bearings](https://www.racing-cars.com/gt12/atom-2/ball-bearing-1-8x5-16-flanged-yellow-pr-u4981?returnurl=%2fgt12%2fatom-2%2f)
    * [Steel shims](https://www.racing-cars.com/gt12/atom-2/s-steel-shims-1-4x5-16x0-004-ss-at-ecl-u4112?returnurl=%2fgt12%2fatom-2%2f%3fcount%3d96)
    * [M3 Nyloc Nuts](https://www.racing-cars.com/gt12/atom-2/m3-alloy-nyloc-nuts-low-profile-black-pk10-cr517?returnurl=%2fgt12%2fatom-2%2f)
    * [Servo Horn](https://www.racing-cars.com/gt12/atom-2/atom-2-parts=chassis-parts/25t-servo-saver-assembly-a2-e3-e4-u7895?returnurl=%2fgt12%2fatom-2%2fatom-2-parts%3dchassis-parts%2f)
    * [Ball Studs (short)](https://www.racing-cars.com/gt12/atom-2/pro-ball-stud-short-pk4-u4274?returnurl=%2fgt12%2fatom-2%2f)
* [Yahboom Jetson Nano 4GB Developer Kit](https://category.yahboom.net/collections/jetson/products/jetson-nano-sub)
* 2x [Arducam Raspberry Pi Official Camera Module V2, with 8 Megapixel IMX219 Wide Angle 175 Degree Replacement](https://www.amazon.com/Arducam-Raspberry-Official-Megapixel-Replacement/dp/B083PW4BLH/)
* [Intel AX201 WiFi 6 BT 5.1 M.2 2230 with 10in RP-SMA Antenna](https://www.newegg.com/p/0XM-009Y-001C7) (not required but helpful)
* [Noctua NF-A4x10 5V](https://noctua.at/en/products/fan/nf-a4x10-5v) (not required)
* [HobbyWing QUICRUN 10BL60 Brushless ESC Sensored](https://www.hobbywingdirect.com/products/quicrun-10-sensored)
* [HobbyWing QUICRUN 3650 Sensored Brushless Motor G2 (25.5T)](https://www.hobbywingdirect.com/collections/quicrun-brushless-motor-series-sensorless/products/quicrun-3650-sensored-2-pole-brushless-motor?variant=28166803089)
* [Savox SV1261MG Digital Mini Servo](https://www.savoxusa.com/products/sv1261mg-mini-digital-high-voltage-aluminum-case-servo-0-095-277-7-4v)
* A LiPo balance charger with XT-60 connector, rated for 3S
* [Zeee Premium Series 3S LiPo Battery 4200mAh 11.4V 120C with XT60 Plug](https://www.amazon.com/Zeee-Premium-Compatible-Helicopter-Airplane/dp/B09CMLSK67)
* 2x [DC-DC 5A Adjustable Buck Converter](https://www.amazon.com/Adjustable-Converter-1-25-36v-Efficiency-Regulator/dp/B079N9BFZC)
* [DC Digital Voltometer](https://www.amazon.com/bayite-Digital-Voltmeter-Display-Motorcycle/dp/B00YALUXH0/)
* [Male 5.5mm DC Barrel Connectors](https://www.amazon.com/Pigtails-Female-Connector-Pigtail-Security/dp/B08PYWN3T7/)
* [Panel-Mountable Female XT60 Connectors](https://www.amazon.com/XT60E-M-Mountable-Connector-Models-Multicopter/dp/B07YJMCDC3)
* [Normally Closed/Momentary On Push Button](https://www.amazon.com/Pieces-normally-closed-Button-Momentary/dp/B07HCLVMGS/) (size must match)
* [12 Tooth 48 Pitch Pinion Gear with Set Screw](https://www.amazon.com/Traxxas-PINION-PITCH-SCREW-2428/dp/B00EFXMUO2)
* [78 Tooth Spur Gear 48 Pitch](https://www.amazon.com/Kimbrough-Pitch-Spur-Gear-78T/dp/B0006O1QVM)
* 20-24 gauge wire
* M3 nylon screws
* M3 nylon standoffs
* M3 nylon nuts
* M3 nuts
* Countersunk, cap head M3 screws (6mm, 33mm)
* Differential lubrication

You will need (at least) the following tools:
* Hex Allen drivers (key or bits)
* Phillips head drivers
* Rotary tool with grinding bit
* Crimper tool
* Soldering iron

*There may be items not listed that are used in the build guide, we apologize if that happens.*

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