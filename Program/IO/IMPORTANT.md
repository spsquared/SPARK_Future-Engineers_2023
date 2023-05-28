# rewrite IO to require only using one io instance
# when io is instantiated it also starts the camera, drive, and IMU threads
# do not instantiate io multiple times, add lock file
# no need to instantiate drive or camera anymore
# also add logger for slightly better debugging