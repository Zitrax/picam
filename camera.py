#!/usr/bin/python3

import picamera
import time


def filenames(count):
    i = 0
    while True:
        yield "image{}.jpg".format(i)
        i += 1
        i %= count

with picamera.PiCamera() as cam:
    cam.capture_sequence(filenames(10))
    time.sleep(30)

    
