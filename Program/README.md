# SPARK WRO 2022 Future Engineers Program Documentation

This is the documentation for all the source code used for the USEL Future Engineers 2022 season.

The code is divided into multiple modular files. `IO` contains source code for camera input and PWM control for throttle and steering. `Util` contains source code for development utilities and is mostly not needed for autonomous driving. `AI` contains source code for computer vision.

During matches, the `server.py` file in `Util` will not be uploaded to ensure compliance with rule 10.9

### How we Implemented Computer Vision
We first start with an edge detection algorithm on the walls. At the same time, we filter the images to find the walls (black pixels) and traffic signs (red and green pixels). The resulting image is a black rectangle with RGB values representing where the objects are

<!-- maitian insert the images here -->

The resulting filtered image is then sent to the TensorRT model to determine the steering output.

In training, if the outputted steering values doesn't match the recorded steering values for an image, the model is penalized and given the correct steering values. This is an example of reinforcement learning being combined with unsupervised learning - the model is trained on images and recorded data and then tested on new images and data.