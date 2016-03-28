#!/usr/bin/python3

import datetime
import logging
import os
import picamera
import re
from subprocess import call
import time


logging.basicConfig(filename="camera.log", level=logging.DEBUG)

base_dir = "/home/pi/camera-images"
latest = os.path.join(base_dir, "latest.jpg")

def upload():
    call(['/home/pi/go/bin/skicka', '-quiet', 'rm', '/birdcam/latest.jpg'])
    if call(['/home/pi/go/bin/skicka', '-quiet', 'upload', '/home/pi/camera-images/latest.jpg', '/birdcam/latest.jpg']):
        logging.warning("{}: Could not upload".format(time.strftime("%Y-%m-%d %H:%M:%S")))

def filenames(count):
    if os.path.exists(latest):
        current = os.path.basename(os.path.realpath(latest))
        m = re.match(r'image(\d+).jpg', current)
        i = (int(m.group(1)) + 1) % count
    else:
        i = 0
    logging.info("Current image id = {}".format(i))
    while True:
        yield "{}/image{:03}.jpg".format(base_dir, i)
        i += 1
        i %= count

with picamera.PiCamera() as cam:
    cam.annotate_text_size = 15
    for fn in filenames(50):
        if datetime.time(1,00) <= datetime.datetime.now().time() <= datetime.time(7,00):
            time.sleep(120);
        cam.led = True
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        cam.annotate_text = time_str
        logging.info("{}: Capturing {}".format(time_str, fn))
        cam.capture(fn)
        cam.led = False
        if os.path.exists(latest):
            os.remove(latest)
        os.symlink(fn, latest)
        upload()
        time.sleep(120)
