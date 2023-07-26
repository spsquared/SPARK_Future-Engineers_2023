<div align=center>

![banner](./img/banner.png)

</div>

# Contents
* (oof)[./oof]

document algorithm here lol

# Algorithm

It runs a constant loop on frames.

General outline:

Image processing:
    Taking iamges
    Undistort and filter Iamges
    Find wall heights
    Find contours
    Find wall lines
    Merge contours and wall lines
Simple Driving:
    Catagorize walls
    Filter pillars
    Calculate steering


Image Processing:

All code for Image Processsing is in `Converter.py`

// buh taking images??

Undistorting images:

At the start of the program, cv2.fisheye.initUndistortRectifyMap is used with precalculated distortion matrices to create the remaps. See [Assembly.md] for instructions on how to get the distortion matrix.
`cv2.remap`

MAITIAN EXPLAIN ALGORITHM bETTER SO I CAN WRITE DOCUMENTATION???

# Code Documentation

## General Structure
Control of the vehicle is handled by various modules, grouped into `IO`, `Controller`, and `Util` packages. `IO` modules handle reading sensors and controlling motors, and is used to interface with the physical vehicle. The `Controller` package contains modules that handle processing images into data, which is then fed into other modules that use that data to calculate the path the vehicle should follow. The `Util` modules are tools used to set up and debug the programs.

## IO

All physical IO for the vehicle is handled by the `io` module, found in `/Program/IO/io.py`. Submodules of `io` - `drive`, `camera`, and `imu` -  can be imported separately, but are included in `io` for ease of use.

### IO

`io` is a wrapper containing `drive`, `camera`, and `imu` submodules, as well as indicator LED controls.

| Property                | Description                                                                                                                                           | Return Value    |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| `GPIO`                  | The `GPIO` object used to control the vehicle.                                                                                                        | `GPIO` object   |
| `drive`                 | The [`drive`](#drive) submodule.                                                                                                                      | `drive` module  |
| `camera`                | The [`camera`](#camera) submodule.                                                                                                                    | `camera` module |
| `imu`                   | The [`imu`](#imu) submodule.                                                                                                                          | `imu` module    |
| `waitForButton()`       | Blocks the executing thread whilst waiting for the physical button on the vehicle to be pressed.                                                      | Nothing         |
| `setStatusBlink(blink)` | Sets the green light status blink of the vehicle. Clamps to the range `[0, 2]`, where 0 is off, 1 is solid, and 2 is flashing.<br>`blink: int [0, 2]` | Nothing         |
| `error()`               | Starts the red light status blink of the vehicle. Once activated, the red light flash will not stop unless `close()` is called.                       | Nothing         |
| `close()`               | Stops all submodules and closes the `GPIO`. The green and red status lights will turn off and all other `stop()` effects of submodules take place.    | Nothing         |

### Drive

`drive` controls the steering and throttle of the physical vehicle. It uses `adafruit_servokit` to interface with the PCA9685 PWM driver over I2C. The steering has a smoothing function, which smooths abrupt changes in steering values to prevent high-frequency oscillation, which triggers the servo's disconnect failsafe. (RC servos will ignore inputs if it believes the RC reciever has lost connection or is sending garbage inputs)

| Property                  | Description                                                                                                                                                                            | Return Value                    |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `steer(str)`              | Sets the target steering value, where 0 is straight, and positive is right.<br>`str: int [-100, 100]`                                                                                  | Nothing                         |
| `throttle(thr)`           | Sets the throttle value, where 0 is stopped, and positive is forward.<br>`thr: int [-100, 100]`                                                                                        | Nothing                         |
| `trim(trim)`              | Sets the offset for the steering servo in degrees, where 0 is no offset and positive is right.<br>`trim: int (-inf, inf)`                                                              | Nothing                         |
| `setSmoothFactor(smooth)` | Sets the smoothing factor for steering, as a decimal, where 0 is no smoothing and approaching 1 increases smoothing. A smoothing value of 1 disables steering.<br>`smooth: int [0, 1)` | Nothing                         |
| `getSmoothfactor()`       | Gets the current smoothing factor                                                                                                                                                      | Current smooth factor (`float`) |
| `currentSteering`         | Gets the current steering value                                                                                                                                                        | Current steering (`float`)      |
| `stop()`                  | Stops the `drive` module. Sets throttle to 0. `steer(str)` has no effect after calling this.                                                                                           | Nothing                         |

### Camera

`camera` reads inputs from the cameras, writes images to file, and can stream to the SPARK Control Panel via the server in `Util`. It automatically starts video streams from two cameras using `nvarguscamerasrc` when imported.

| Property                              | Description                                                                                                                                                                                                                                                                                               | Return Value                                          |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `read()`                              | Gets the most recent images read from the cameras as a length-2 list of `numpy` arrays.                                                                                                                                                                                                                   | Current images (`list[numpy.ndarray, numpy.ndarray]`) |
| `capture(filter, sendServer)`         | Writes the most recent images to file, filtering and/or broadcasting from `server` if requested. Images can be found in the program directory under `/image_out/` or `/filtered_out/` if filtering is enabled.<br>`filter: bool default=False`<br>`sendServer: bool default=False`                        | Success (`bool`)                                      |
| `startSaveStream(filter, sendServer)` | Begins a 10 frame-per-second stream of saving images to file, filtering and/or broadcasting from `server` if requested. Images can be found in the program directory under `/image_out/` or `/filtered_out/` if filtering is enabled.<br>`filter: bool default=False`<br>`sendServer: bool default=False` | Success (`bool`)                                      |
| `stopSaveStream()`                    | Stops the running save stream, if one is running.                                                                                                                                                                                                                                                         | Success (`bool`)                                      |
| `startStream(filter)`                 | Begins a 10 frame-per-second stream of broadcasting from `server`, filtering if requested.<br>`filter: bool default=False`                                                                                                                                                                                | Success (`bool`)                                      |
| `stopStream()`                        | Stops the running stream, if one is running.                                                                                                                                                                                                                                                              | Success (`bool`)                                      |
| `streamState()`                       | Returns the state of streaming as a length-3 list of booleans. Indexes 0, 1, and 2 are streaming, filtering, and broadcasting.                                                                                                                                                                            | Stream state (`list[bool, bool, bool]`)               |
| `stop()`                              | Stops the `camera` module. Video streams are closed and images will no longer be updated.                                                                                                                                                                                                                 | Nothing                                               |

### IMU

`imu` handles reading gyroscope and accelerometer data from the MPU6050 integrated IMU over I2C. (Currently only integrates Z-axis angles)

| Property             | Description                                                                                                 | Return Value               |
| -------------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------- |
| `calibrate()`        | Gets the offset to compensate for gyro drift and updates the trim temporarily. Will print to console.       | New drift offset (`float`) |
| `angle()`            | Gets the current vehicle angle around Z-axis, calculated by integrating the rotational velocity.            | Angle in radians (`float`) |
| `setAngle(newAngle)` | Sets the vehicle angle (useful for SLAM or resetting the angle).<br>`newAngle: float (-inf, inf) default=0` | Nothing                    |
| `stop()`             | Stops the `imu` module. Angle integration stops after calling this.                                         | Nothing                    |