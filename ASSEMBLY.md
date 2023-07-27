<div align=center>

![banner](./img/banner.png)

</div>

***

# Build Guide

This is the build guide for SPARK's 2023 WRO Future Engineers solution - SPARK G2. It is segmented into ***TBD*** main steps, with more detailed steps within. It assumes you have necessary tools and miscellaneous materials including but not limited to: M2.5, M3 driver bits; a Dupont connector crimpange kit; a 3D printer; a soldering iron; 20-24 gauge wire; and M2.5, M3 flat/countersunk screws.

Below is a more-or-less detailed step-by-step guide to recreate SPARK g2.

***

# Contents

* [Parts List](#parts-list)
* [Chassis Assembly](#chassis-assembly)
* [Jetson Nano Setup](#jetson-nano-setup)
    * [Board Setup, SSHFS, Static IP](#board-setup-sshfs--static-ip)
    * [Enable GPIO & I2C](#enable-gpio-and-i2c)
    * [Install Packages](#package-installation)
    * [Remove GUI, Autologin, & Run-on-startup](#text-only-auto-login--run-on-startup)
    * [SPARK Control Panel Setup](#setup-for-spark-control-panel)
    * [Camera Calibration](#camera-calibration)

***

## Parts List

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
* M3 nylon screws (6mm)
* M3 nylon standoffs (6mm works best)
* M3 nylon nuts
* M3 nuts
* Countersunk, cap head M3 screws (6mm and 8mm work best)
* Socket cap head M3x40mm screws [(like these)](https://www.amazon.com/Alloy-Steel-Socket-Screws-Black/dp/B00W97R5KU)
* Differential lubrication

You will need (at least) the following tools:
* 3D printer or access to 3D printing service
* Hex Allen drivers (key or bits)
* Phillips head drivers
* Rotary tool with grinding bit (depending on which version of motor)
* Crimper tool
* Soldering iron

*There may be items not listed that are used in the build guide, we apologize if that happens.*

## Chassis Assembly

guide through 3d printing and assembling (oof), ensure that steering assembly instructions are clear. note that part of the motor mount has to be grinded away for some versions of the drive motor and the 3d modeled rear axle assembly cannot be printed. (buy the parts off of schumacher's website!!!) 3d printed parts are in the `/3D Models/` folder and are in the orientation they should be printed in but also include Onshape document

pinout sheet:
https://docs.google.com/spreadsheets/d/1WAe1DtCbWhLoC4L6yzJYvS99iHG4yAiWakqxsy8os7s/edit?usp=sharing

## Jetson Nano Setup

### Board Setup, SSHFS, & Static IP

Visit [Yahboom](http://www.yahboom.net/)'s [setup and tutorial repository](http://www.yahboom.net/study/jetson-nano) to begin setting up the [Jetson Nano 4GB](https://category.yahboom.net/collections/jetson/products/jetson-nano-sub). Follow steps 1.1-1.7 in "Development setup > SUB Version".

-> http://www.yahboom.net/study/jetson-nano

After setting up the board, follow step 2.1 in section "Basic Settings" to log into your Jetson Nano. Keep PuTTY open, as it will be used for the rest of the setup process. Also keep the IP. For remote file transfer, install sshfs (linux only), or use [sshfs-win](https://github.com/winfsp/sshfs-win) from WinFsp. Follow instructions to mount the Jetson Nano to a network drive. Now upload all contents of the `/Program/` folder into a new folder on the Jetson Nano. Remember the directory of the folder, this will be used later.

*This method should be used to upload programs.*

Make sure a static IP is set to the board to make SSH and file transfer easier. Go to your router settings and [assign a DHCP reservation (PCmag)](https://www.pcmag.com/how-to/how-to-set-up-a-static-ip-address) (or a straight static IP) to your Jetson Nano. Save this IP in your PuTTY settings and SSHFS mounting.

### Enable GPIO and I2C

Next, setting up the board for the application. First, enable GPIO and I2C. Create a new user group, and add your user to it (this is the user running the commands).

```
sudo groupadd -f -r gpio
sudo usermod -a -G gpio your_user_name
```

Copy `99-gpio.rules` from `/dist/` in the project folder to `/etc/udev/rules.d/` on the Jetson Nano. Then enable the rule.

```
sudo udevadm control --reload-rules && sudo udevadm trigger
```

<!-- Now enable PWM. Run the options file for jetson-GPIO.

```
sudo /opt/nvidia/jetson-io/jetson-io.py
```

Go down to "Configure 40-pin expansion header" and enter that submenu. Find `pwm0` and `pwm`, and enable them by selecting them and pressing "Enter". Now exit the tool. GPIO and PWM have been enabled. -->

You may need to enable permissions for I2C

```
sudo usermod -a -G i2c your_user_name
```

### Package Installation

Some packages will need to be installed. [Jetson-GPIO](https://github.com/NVIDIA/jetson-gpio), socket.io-client, [adafruit-servokit](https://github.com/adafruit/Adafruit_CircuitPython_ServoKit), and [adafruit-mpu6050](https://github.com/adafruit/Adafruit_MPU6050) must be installed (Jetson-GPIO may be pre-installed on some versions).

Use the following pip commands:

```
pip3 install adafruit-circuitpython-servokit
pip3 install adafruit-mpu6050
pip3 install "python-socketio[client]"
```

### Text-Only, Auto-Login, & Run on Startup

Switch the Jetson Nano to text-only mode (gui is almost useless for this application and only causes unneccesary slowness).

```
sudo systemctl set-default multi-user.target
```

Autologin must be done to avoid having to plug in a monitor and keyboard to start ssh and run programs. The following accomplishes it:

```
sudo systemctl edit getty@tty1
```

A temporary editor will appear. Place the following text in it, replacing "your_user_name" with your user name.

```
[Service]
ExecStart=
ExecStart=-/sbin/agetty -o '-p -f your_user_name' -a your_user_name --noclear %I $TERM
```

Save and close the editor with `:wqa`.

To run the program on startup, first obtain the directory of the program folder uploaded earlier. Create `spark_startup.service` in `/etc/systemd/system` and place the following in the contents, replacing "/filepath/" with the absolute directory of the folder (begins with a "/").

```
[Service]
WorkingDirectory=/filepath
ExecStart=/usr/bin/python3 -u /filepath/startup.py
User=username

[Install]
WantedBy=multi-user.target
```

Save the file and add permissions to it.

```
sudo chmod 644 /etc/systemd/system/spark_startup.service
systemctl enable /etc/systemd/system/spark_startup.service
```

Reboot the Jetson Nano to test if these changes worked. No GUI should appear and you shuld be automatically logged in.

Enable run-on-startup by editing `run-on-startup.txt` in the folder. Replace the first line with `true`.

Go through `startup.py` and `/IO/io.py`, and change `path` to the absolute filepath of your directory (same as filepath in the previous steps)

Example:

```
path = '/home/nano/Documents/SPARK_FutureEngineers_2022/'
```

Reboot the Jetson Nano again

### Setup for SPARK Control Panel

SPARK uses a debugging server (SPARK Control Panel) for quick development and real-time monitoring. It runs on a separate Node.js process and is not needed. If you want access to the SPARK Control Panel you must install Node.js and dependencies.

```
sudo apt install nodejs
```

Navigate to `/Util/` and install dependencies.

```
npm install
```

For the authentication system to work properly (not actual authentication, just a UUID exchange to prevent people from sending bogus signals) `auth.json` must be created in `/Util/`.

```
vim auth.json
```

The contents should be a single UUID:

```
"214e7634-b7c3-4044-b297-533da8cfbe7f"
```

This UUID should also be present on client devices, along with the IP of the car (set earlier). On the client devices, create `/SPARK-Util/SPARK-Control/config.js`.

Example:

```
const ip = '192.168.1.151';
const auth_uuid = '214e7634-b7c3-4044-b297-533da8cfbe7f';
```

To open the SPARK Control Panel and other utilities, use `node SPARK-Util/static.js` or open the batch file `/SPARK-Util/static.bat`. In any web browser (only Chrome tested), navigate to `localhost:8081` to access the SPARK Control Panel.

### Camera Calibration

You may encounter pink fringing on the cameras. If that happens, take the following steps to fix it:

Copy `camera_overrides.isp` from `/dist/` in the project folder to `/var/nvidia/nvcam/settings/` on the Jetson Nano.

Give the overrides permissions with the next two:

```
sudo chmod 664 /var/nvidia/nvcam/settings/camera_overrides.isp
sudo chown root:root /var/nvidia/nvcam/settings/camera_overrides.isp
```

Next, calibrate the cameras. If you skip this step, the distortion correction may have error and the program may not function as intended.

aaaaa @maitian @maitian @maitian @maitian @maitian @maitian @maitian @maitian @maitian @maitian @maitian @maitian @maitian @maitian 

TODO: Camera calibration, car assembly