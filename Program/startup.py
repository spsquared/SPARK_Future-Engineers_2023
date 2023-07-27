import Jetson.GPIO as GPIO
import time
import subprocess
import os

path = '/home/nano/Documents/SPARK_FutureEngineers_2023/'

if __name__ == '__main__':
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup([11, 13], GPIO.OUT)
    GPIO.output([11, 13], GPIO.LOW)
    time.sleep(0.5)
    GPIO.cleanup()

    subprocess.Popen(['node', path + 'Util/server.js'])

    # in competition, wait for button press
    fd = open(path + 'run_on_startup.txt', 'r')
    run_startup = fd.readlines()[0]
    if run_startup == 'true\n':
        print('Run-on-startup enabled!')
        os.system('python3 ' + path + 'autodrive.py wait_for_button no_server')