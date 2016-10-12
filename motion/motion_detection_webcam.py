#/usr/bin/env python

import cv2
import subprocess
from time import sleep

MIN_AREA = 500
SLEEP_TIME = 100

def detect_motion():
    cam = cv2.VideoCapture(0)
    last_img = None
    
    while True:
        outcome = False
        ret, img = cam.read()
        
        # quit if we do not get data from webcam
        if not ret:
            print("Unable to get data from webcam")

        img_small = cv2.resize(img,None,fx=2, fy=2, interpolation = cv2.INTER_CUBIC)
        gray_img = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)
        blur_img = cv2.GaussianBlur(gray_img, (21, 21), 0)

        if last_img is None:
            last_img = blur_img
            continue

        # compute difference between current and last image
        img_delta = cv2.absdiff(last_img, blur_img)
        thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in cnts:
            # ignore small contours
            print(cv2.contourArea(cnt))
            if cv2.contourArea(cnt) < MIN_AREA:
                continue
            else:
                print("change detected")
                subprocess.call(['/opt/vc/bin/tvservice', '-p'])
                subprocess.call(['fbset -depth 8'], shell=True)
                subprocess.call(['fbset -depth 16'], shell=True)
                subprocess.call(['xrefresh'], shell=True)

        last_img = blur_img
        # give it a little pause (in milliseconds)
        sleep(SLEEP_TIME/1000.0)
        

if __name__ == "__main__":
    detect_motion()
