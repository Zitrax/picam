#!/usr/bin/python3

import datetime
import logging
import os
import picamera
import time


logging.basicConfig(filename="camera.log", level=logging.DEBUG)

base_dir = "/home/pi/camera-images"
latest = os.path.join(base_dir, "latest.jpg")

def filenames(count):
    i = 0
    while True:
        yield "{}/image{}.jpg".format(base_dir, i)
        i += 1
        i %= count

with picamera.PiCamera() as cam:
    for fn in filenames(50):
        if datetime.time(1,00) <= datetime.datetime.now().time() <= datetime.time(7,00):
            time.sleep(120);
        cam.led = True
        logging.info("{}: Capturing {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), fn))
        cam.capture(fn)
        cam.led = False
        os.remove(latest)
        os.symlink(fn, latest)
        time.sleep(120)
