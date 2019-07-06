#import RPi.GPIO as GPIO
#import tkinter as tk
import time
#import cv2
import subprocess
import re
#import PIL
#from PIL import Image,ImageTk
#import pytesseract
from picamera import PiCamera
from time import sleep
import datetime



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
     
def takeSnapshot():
    camera.start_preview()
    sleep(5)
    camera.capture('/home/pi/Desktop/image.jpg')
    camera.stop_preview()


def recordVideoPi():
    #Get current date and time
    day = datetime.datetime.now()
    format = '%a %b %d %H %M %S %Y'

    #Create output filename
    filepath = '../vive-web/public/videos/'

    exh = '.h264' #input extension from PiCamera
    exm =  '.mp4' #output extension after ffmpeg
    
    filename  = re.sub('[^A-Za-z0-9]+', '', day.strftime(format)).lower() 
    input_file_name = filepath + filename + exh
    output_file_name =  filepath + filename +exm


    #Record video
    camera = PiCamera()
    camera.start_recording(input_file_name)
    camera.start_preview()
    sleep(10)
    camera.stop_preview()
    sleep(10)
    print("Converting to a useable format.....")
    command = ["ffmpeg", "-f", "h264", "-i",  input_file_name , "-c:v", "copy", output_file_name]
    subprocess.call(command)
    print("Converstion completed. Cleaning up....")
    subprocess.call(["rm", input_file_name])







recordVideoPi()

    
#GPIO.setmode(GPIO.BCM)

#GPIO.setup(23, GPIO.IN) #PIR1
#GPIO.setup(24, GPIO.IN) #PIR2

#try:
#    time.sleep(1) 
#    while True:
#        if GPIO.input(23) or GPIO.input(24):
#            print("Motion Detected...")
#            recordVideoPi()
            
            
#            time.sleep(5)
#            time.sleep(0.1)
#
#except:
#    GPIO.cleanup()



