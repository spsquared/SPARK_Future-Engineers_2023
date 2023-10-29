<div align=center>

![banner](./img/banner.png)

</div>

***

**Official GitHub repository for WRO USA Future Engineers team SPARK 2023. All code, documentation, and files are located here.**

***

# Contents
* [High-level Overview](#high-level-overview)
    * [Hardware Design](#hardware-design)
    * [Software Design](#software-design)
    * [Photos](#photos)


# High-Level Overview

**This section is a general explaination of Team SPARK's 2023 solution, SPARK G2. For more in-depth explainations and instructions, see [ALGORITHM.md](ALGORITHM.md) and [SETUP.md](SETUP.md)**

<a href=./ALGORITHM.md><img src="https://img.shields.io/badge/-ALGORITHM.md-%23000000?style=for-the-badge&logo=markdown"></a>
<a href=./SETUP.md><img src="https://img.shields.io/badge/-SETUP.md-%23000000?style=for-the-badge&logo=markdown"></a>

## Hardware Design

SPARK G2 consists of a 3D-printed chassis with off-the-shelf components mounted to it, like the motors, cameras, and controller boards. For a full component list, see [SETUP.md](./SETUP.md#parts-list). CAD models can be found in `/dist/3d-models/`, and have all been [modeled in Onshape here](https://cad.onshape.com/documents/82dd14d30b814e8846567203/w/34e1b6a4058ed5fbde8ef66a/e/47aa4028e09ec17a24a63590).

![SPARK G2 chassis with electronics in CAD software](./img/docs/cad-car.png)

The chassis consists of a lower base with vertical walls to mount the rear axle and upper platforms. It has space for the battery and an ESC (electronic speed controller) bay in the rear, and a compartment in the front for the steering mechanism. The rear axle is sourced from the Atom 2 GT12 pan car kit by Schumacher, and is mounted vertically to save space.

The electronics platforms sit on top of the chassis base, and the main platform is also a structural component that provides rigidity to the chassis. Because the electronics are on top, they are easily accessible and wiring is fairly simple. The only exceptions are the ESC, which is in the rear, and the IMU (inertial measurement unit, used for measuring angles and velocity).

| Chassis base with rear axle and steering           | Chassis base and platforms, without camera tower            |
| -------------------------------------------------- | ----------------------------------------------------------- |
| ![Lower chassis base](./img/docs/chassis-base.png) | ![Chassis with platforms](./img/docs/chassis-platforms.png) |

One major physical change is the addition of a second IMX219 wide-angle camera to the front of the car. Both cameras are angled 30 degrees to either side, with a field of view of 150 degrees for each camera. The cameras are mounted on a slider to ensure the accuraccy of the [distance calculations in the algorithm](./ALGORITHM.md#merge-contours--wall-lines).

![Cameras top-down](./img/docs/camera-angles.png)

SPARK G2 does not use any other sensors to percieve its environment - no LiDAR here!

<!-- wiring diagram -->

## Software Design

<!-- high-level overview - what architecture is used, part of SETUP.md i guess -->

## Photos

<!-- photos -->