#!/usr/bin/python3

from subprocess import call
import datetime
import logging
import os
import picamera
import re
import signal
import time


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


with picamera.PiCamera() as cam:
    shutdown_handler = ShutdownHandler()
    cam.annotate_text_size = 15
    logging.info("Starting")
    for fn in filenames(50):
        if datetime.time(1,00) > datetime.datetime.now().time() > datetime.time(7,00):
            cam.led = True
            cam.annotate_text = time.strftime("%Y-%m-%d %H:%M:%S")
            logging.info("Capturing {}".format(fn))
            cam.capture(fn)
            cam.led = False
            if os.path.exists(latest):
                os.remove(latest)
            os.symlink(fn, latest)
            upload()
        if shutdown_handler.shutdown:
            logging.info("Goodbye")
            break
        time.sleep(2)  # Not sleeping very long so we can handle shutdown faster
