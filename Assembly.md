<div align=center>

![banner](./img/banner.png)

</div>

***

# **Build Guide**

This is the build guide for SPARK's 2023 WRO Future Engineers solution - SPARK g2. It is segmented into ***TBD*** main steps, with more detailed steps within. It assumes you have necessary tools and miscellaneous materials including but not limited to: M2.5, M3 driver bits; a Dupont connector crimpange kit; a 3D printer; a soldering iron; 20-24 gauge wire; and M2.5, M3 flat/countersunk screws.

Below is a detailed step-by-step guide to recreate SPARK g2.

***

# Contents

* [Chassis Assembly](#chassis-assembly)
* [Jetson NANO Setup](#jetson-nano-setup)
    * [Board Setup, SSHFS, Static IP](#board-setup-sshfs--static-ip)
    * [Enable GPIO & I2C](#enable-gpio-and-i2c)
    * [Remove GUI, Autologin, & Run-on-startup](#text-only-auto-login--run-on-startup)
    * [Camera Color Fix](#camera-color-correction)

***

## Chassis Assembly

guide through 3d printing and assembling (oof), ensure that steering assembly instructions are clear. note that part of the motor mount has to be grinded away and the 3d modeled rear axle assembly cannot be printed. (buy the parts off of schumacher's website!!!) 3d printed parts are in the `/3D Models/` folder and are in the orientation they should be printed in but also include Onshape document

dont forget to rotary tool parts of some of the stock pieces away

## Jetson NANO Setup

### Board Setup, SSHFS, & Static IP

Visit [Yahboom](http://www.yahboom.net/)'s [setup and tutorial repository](http://www.yahboom.net/study/jetson-nano) to begin setting up the [Jetson NANO 4GB](https://category.yahboom.net/collections/jetson/products/jetson-nano-sub). Follow steps 1.1-1.7 in "Development setup > SUB Version".

-> http://www.yahboom.net/study/jetson-nano

After setting up the board, follow step 2.1 in section "Basic Settings" to log into your Jetson NANO. Keep PuTTY open, as it will be used for the rest of the setup process. Also keep the IP. For remote file transfer, install sshfs (linux only), or use [sshfs-win](https://github.com/winfsp/sshfs-win) from WinFsp. Follow instructions to mount the Jetson NANO to a network drive. Now upload all contents of the `/Program/` folder into a new folder on the Jetson NANO. Remember the directory of the folder, this will be used later.

*This method should be used to upload programs.*

<!-- screenshots of setup for mapping network drive (\\sshfs\nano@192.168.1.151\) -->

<!-- sshfs.r mounts to root -->

Make sure a static IP is set to the board to make SSH and file transfer easier. Go to your router settings and [assign a DHCP reservation (PCmag)](https://www.pcmag.com/how-to/how-to-set-up-a-static-ip-address) (or a straight static IP) to your Jetson NANO. Save this IP in your PuTTY settings and SSHFS mounting.

<!-- Install `websockets` package with pip. add rest of stuff! -->

### Enable GPIO and I2C

Next, setting up the board for the application. First, enable GPIO and I2C. Create a new user group, and add your user to it (this is the user running the commands).

```
sudo groupadd -f -r gpio
sudo usermod -a -G gpio your_user_name
```

Copy `99-gpio.rules` from `/dist/` in the project folder to `/etc/udev/rules.d/` on the Jetson NANO. Then enable the rule.

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

### Text-Only, Auto-Login, & Run on Startup

Switch the Jetson NANO to text-only mode (gui is almost useless for this application and only causes unneccesary slowness).

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
ExecStart=cd /filepath /usr/bin/python3 /filepath/startup.py
User=username

[Install]
WantedBy=multi-user.target
```

Save the file and add permissions to it.

```
sudo chmod 644 /etc/systemd/system/spark_startup.service
systemctl enable /etc/systemd/system/spark_startup.service
```

Reboot the Jetson NANO to test if these changes worked. No GUI should appear and you shuld be automatically logged in.

Enable run-on-startup by editing `run-on-startup.txt` in the folder. Replace the first line with `true`.

Go through `startup.py` and `/IO/io.py`, and change `path` to the absolute filepath of your directory (same as filepath in the previous steps)

Example:

```
path = '/home/nano/Documents/SPARK_FutureEngineers_2022/'
```

Reboot the Jetson NANO again

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

### Camera Color Correction

You may encounter pink fringing on the cameras. If that happens, take the following steps to fix it:

Copy `camera_overrides.isp` from `/dist/` in the project folder to `/var/nvidia/nvcam/settings/` on the Jetson Nano.

Give the overrides permissions with the next two:

```
sudo chmod 664 /var/nvidia/nvcam/settings/camera_overrides.isp
sudo chown root:root /var/nvidia/nvcam/settings/camera_overrides.isp
```