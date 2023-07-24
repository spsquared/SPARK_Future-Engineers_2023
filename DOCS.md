<div align=center>

![banner](./img/banner.png)

</div>

### General Structure
Control of the vehicle is handled by various modules, grouped into `IO`, `Controller`, and `Util` packages. `IO` modules handle reading sensors and controlling motors, and is used to interface with the physical vehicle. The `Controller` package contains modules that handle processing images into data, which is then fed into other modules that use that data to calculate the path the vehicle should follow. The `Util` modules are tools used to set up and debug the programs.

### IO

All physical IO for the vehicle is handled by the `io` module, found in `/Program/IO/io.py`. Submodules of `io` - `drive`, `camera`, and `imu` -  can be imported separately, but are included in `io` for ease of use.

#### **IO**

`io` is a wrapper containing `drive`, `camera`, and `imu` submodules, as well as indicator LED controls.

| Function | Description | returns |
| -------- | ----------- | ------- |
|          |             |         |

#### **Drive**

`drive` controls the steering and throttle of the physical vehicle. It uses `adafruit_servokit` to interface with the PCA9685 PWM driver over I2C.

| Function        | Description                                                                                                               | Returns |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- | ------- |
| `steer(str)`    | Sets the target steering value, where 0 is straight, and positive is right.<br>`str: int [-100, 100]`                     | Nothing |
| `throttle(thr)` | Sets the throttle value, where 0 is stopped, and positive is forward.<br>`thr: int [-100, 100]`                           | Nothing |
| `trim(trim)`    | Sets the offset for the steering servo in degrees, where 0 is no offset and positive is right.<br>`trim: int (-inf, inf)` | Nothing |
| `close()`       | Closes the `drive` module. Sets steering and throttle to 0.                                                               | Nothing |

#### **Camera**

`camera` reads inputs from the cameras, writes images to file, and can stream to the SPARK Control Panel via the server in `Util`.

| Function | Description | returns |
| -------- | ----------- | ------- |
|          |             |         |

#### **IMU**

`imu` handles reading gyroscope and accelerometer data from the MPU6050 integrated IMU over I2C. (Currently only integrates Z-axis angles)

| Function      | Description                                                                                           | returns                    |
| ------------- | ----------------------------------------------------------------------------------------------------- | -------------------------- |
| `calibrate()` | Gets the offset to compensate for gyro drift and updates the trim temporarily. Will print to console. | New drift offset (`float`) |
| `angle()`     | Gets the current angle, calculated by integrating the rotational velocity.                            |                            |