#!/usr/bin/python3

from  datetime import datetime, time
from subprocess import call
from time import sleep, strftime
import logging
import os
import picamera
import re
import signal


script_dir = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=os.path.join(script_dir, "camera.log"), level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

base_dir = "/home/pi/camera-images"
latest = os.path.join(base_dir, "latest.jpg")


class ShutdownHandler:
    """Raises a flag when we should shutdown"""

    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def sigterm_handler(self, _signo, _stack_frame):
        logging.info("Got shutdown signal")
        self.shutdown = True


def upload():
    call(['/home/pi/go/bin/skicka', '-quiet', 'rm', '/birdcam/latest.jpg'])
    if call(['/home/pi/go/bin/skicka', '-quiet', 'upload', '/home/pi/camera-images/latest.jpg', '/birdcam/latest.jpg']):
        logging.warning("Could not upload")


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

def in_between(start, end):
    now = datetime.now().time()
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end


def abortable_sleep(seconds, sh):
    """Sleep for a given number of seconds, or until shutdown"""
    total = 0
    while total < seconds and not sh.shutdown:
        sleep(1)
        total += 1


with picamera.PiCamera() as cam:
    shutdown_handler = ShutdownHandler()
    cam.annotate_text_size = 15
    logging.info("Starting")
    for fn in filenames(50):
        if in_between(time(7), time(1)):
            cam.led = True
            cam.annotate_text = strftime("%Y-%m-%d %H:%M:%S")
            logging.info("Capturing {}".format(fn))
            cam.capture(fn)
            cam.led = False
            if os.path.exists(latest):
                os.remove(latest)
            os.symlink(fn, latest)
            upload()
        abortable_sleep(120, shutdown_handler)
        if shutdown_handler.shutdown:
            logging.info("Goodbye")
            break
