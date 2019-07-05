#import RPi.GPIO as GPIO
import tkinter as tk
import time
import cv2
import subprocess
import re
import PIL
from PIL import Image,ImageTk
import pytesseract
from picamera import PiCamera
from time import sleep






def turnOffScreen():
    subprocess.call(['xset', 'dpms', 'force','off'])

def turnOnScreen():
    subprocess.call(['xset', 'dpms', 'force','off'])

def uploadToBucket(filename):
    print("Uploading to Amazon...")
    s3 = boto3.client('s3')
    with open(filename, "rb") as f:
        if s3.upload_fileobj(f, "vive-cam", filename):
            print("Upload complete")
        else:
            print("Upload failed")
        


def recordVideoCv(duration):
    """
    Record a video for a given number of seconds
    
    Parameters:
    duration (float): The length of the recording

    """
    
    #Get video feed from primary device
    cap = cv2.VideoCapture(0) 

    #Video output file name will be the current day and time
    file = "../vivecam-express/public/videos/" +(re.sub('[^A-Za-z0-9]+', '', time.asctime()) +'.m4v').lower()
    

    #Get the default width and height of frame 
    #Note: If this step is ignored there will be no output file
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file, fourcc, 20.0, (width,height))
    

    #Get the current time
    start_time = time.time()

    print("Recording in progess...")
    
    #Record only for the duration
    while(int(time.time() - start_time) < duration):
        ret, frame = cap.read()
        
        if ret==True:
            out.write(frame)
        else:
            break
        
        
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Output written to " + file)

    #uploadToBucket(file)

    
    
    with open('videos.csv','a') as fd:
        fd.write(file)
     


def recordVideoPi():
    camera = PiCamera()
    camera.start_recording('/home/pi/video.h264')
    camera.start_preview()
    sleep(10)
    camera.stop_preview()   






recordVideoPi()

    
#GPIO.setmode(GPIO.BCM)

#GPIO.setup(23, GPIO.IN) #PIR1
#GPIO.setup(24, GPIO.IN) #PIR2

#try:
#    time.sleep(1) 
#    while True:
#        if GPIO.input(23) or GPIO.input(24):
#            print("Motion Detected...")
#            recordVideo(10)
            
            
#            time.sleep(5)
#            time.sleep(0.1)
#
#except:
#    GPIO.cleanup()



