#!/usr/bin/env python

import cv2
import subprocess
from datetime import datetime as dt
from time import sleep

MIN_AREA = 500  # how much pixel area needs to change to qualify as motion
SLEEP_TIME = 100
MIN_TIME_DELTA = 5  # seconds

isDebug = True  # print debug information
last_on_timestamp = None  # time when we last turned on the display


def debugging(msg):
    global isDebug
    if isDebug:
        print msg


def monitor_on():
    global last_on_timestamp
    last_on_timestamp = dt.now()
    debugging("Turn display on")
    if not isDebug:
        subprocess.Popen('tvservice -p', shell=True)
        subprocess.Popen('fbset -depth 8 && fbset -depth 16 && xrefresh', shell=True)


def get_monitor_state():
    process = subprocess.Popen(['tvservice', '-s'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    debugging(out)


def detect_motion():
    global last_on_timestamp
    cam = cv2.VideoCapture(0)
    last_img = None

    while True:
        ret, img = cam.read()

        # Quit if we do not get data from webcam
        if not ret:
            debugging("Unable to get data from webcam. Exiting...")
            exit(1)

        img_small = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray_img = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)
        blur_img = cv2.GaussianBlur(gray_img, (21, 21), 0)

        if last_img is None:
            last_img = blur_img
            continue

        # Compute difference between current and last image
        img_delta = cv2.absdiff(last_img, blur_img)
        thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in cnts:
            # Ignore small contours
            if cv2.contourArea(cnt) < MIN_AREA:
                continue
            else:
                debugging("Motion detected")
                if not last_on_timestamp:
                    debugging("First time motion was detected")
                    monitor_on()
                else:
                    time_diff = (dt.now() - last_on_timestamp).total_seconds()
                    if time_diff > MIN_TIME_DELTA:
                        debugging("Minimal time delta exceeded")
                        monitor_on()

        last_img = blur_img

        # Give the motion detection a little pause (in milliseconds)
        sleep(SLEEP_TIME / 1000.0)


if __name__ == "__main__":
    detect_motion()
