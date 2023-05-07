<div align=center>

![banner](./img/banner.png)

</div>

***

# **Build Guide**

This is the build guide for SPARK's 2023 WRO Future Engineers solution - SPARK g2. It is segmented into ***TBD*** main steps, with more detailed steps within. It assumes you have necessary tools and miscellaneous materials including but not limited to: M2.5, M3 driver bits; a Dupont connector crimpange kit; a 3D printer; a soldering iron; 20-24 gauge wire; and M2.5, M3 flat/countersunk screws.

Below is a detailed step-by-step guide to recreate SPARK g2.

***

# Contents

guide through 3d printing and assembling, ensure that steering assembly instructions are clear. note that part of the motor mount has to be grinded away and the 3d modeled rear axle assembly cannot be printed.

* [Jetson NANO Setup](#jetson-nano-setup)
    * [Board Setup, SSHFS, Static IP](#board-setup-sshfs--static-ip)
    * [Enable GPIO & PWM](#enable-gpio-and-pwm)
    * [Remove GUI, Autologin, & Run-on-startup](#text-only-auto-login--run-on-startup)

## Jetson NANO Setup

### Board Setup, SSHFS, & Static IP

Visit [Yahboom](http://www.yahboom.net/)'s [setup and tutorial repository](http://www.yahboom.net/study/jetson-nano) to begin setting up the [Jetson NANO 4GB](https://category.yahboom.net/collections/jetson/products/jetson-nano-sub). Follow steps 1.1-1.7 in "Development setup > SUB Version".

-> http://www.yahboom.net/study/jetson-nano

After setting up the board, follow step 2.1 in section "Basic Settings" to log into your Jetson NANO. Keep PuTTY open, as it will be used for the rest of the setup process. Also keep the IP. For remote file transfer, install sshfs (linux only), or use [sshfs-win](https://github.com/winfsp/sshfs-win) from WinFsp. Follow instructions to mount the Jetson NANO to a network drive. Now upload all contents of the `/Program/` folder into a new folder on the Jetson NANO. Remember the directory of the folder, this will be used later.

*This method should be used to upload programs.*

<!-- screenshots of setup for mapping network drive (\\sshfs\nano@192.168.1.151\) -->

<!-- sshfs.r mounts to root -->

Make sure a static IP is set to the board to make SSH and file transfer easier. Go to your router settings and [assign a DHCP reservation (PCmag)](https://www.pcmag.com/how-to/how-to-set-up-a-static-ip-address) (or a straight static IP) to your Jetson NANO. Save this IP in your PuTTY settings and SSHFS mounting.

Install `websockets` package with pip. <!-- add rest of stuff! -->

### Enable GPIO and PWM

Next, setting up the board for the application. First, enable GPIO and PWM. Create a new user group, and add your user to it (this is the user running the commands).

```
sudo groupadd -f -r gpio
sudo usermod -a -G gpio your_user_name
```

Copy the `99-gpio.rules` file from the `/Program/` folder to `/etc/udev/rules.d/` on the Jetson NANO (use sshfs or ). Then enable the rule.

```
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Now enable PWM. Run the options file for jetson-GPIO.

```
sudo /opt/nvidia/jetson-io/jetson-io.py
```

Go down to "Configure 40-pin expansion header" and enter that submenu. Find `pwm0` and `pwm`, and enable them by selecting them and pressing "Enter". Now exit the tool. GPIO and PWM have been enabled.

### Text-Only, Auto-Login, & Run on Startup

Switch the Jetson NANO to text-only mode (gui is almost useless for this application and only causes unneccesary slowness).

```
sudo systemctl set-default multi-user.target
```

Autologin must be done to avoid having to plug in a monitor and keyboard to start ssh and run programs. The following accomplishes it:

```
sudo systemctl edit getty@tty1
```

A temporary editer will appear. Place the following text in it, replacing "your_user_name" with your user name.

```
[Service]
ExecStart=
ExecStart=-/sbin/agetty -o '-p -f your_user_name' -a your_user_name --noclear %I $TERM
```

Save and close the editor with `:wqa`.

To run the program on startup, first obtain the directory of the program folder uploaded earlier. Create `spark_startup.service` in `/etc/systemd/system` and place the following in the contents, replacing "/filepath/" with the absolute directory of the folder (begins with a "/").

<!-- specify filepath? -->
<!-- switch to bashrc? -->
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
systemctl enable spark_startup.service
```

Reboot the Jetson NANO to test if these changes worked. No GUI should appear and you shuld be automatically logged in.

Enable run-on-startup by editing `run-on-startup.txt` in the folder. Replace the first line with `true`.

Go through `startup.py` and `/IO/io.py`, and change `path` to the absolute filepath of your directory (same as filepath in the previous steps)

Example:

```
path = '/home/nano/Documents/SPARK_FutureEngineers_2022/'
```

Reboot the Jetson NANO again