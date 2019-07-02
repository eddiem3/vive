import os
import cv2
from guizero import App, PushButton, Text, Picture,  Window
from time import gmtime, strftime


thumbnails = []


def new_picture():
    camera.start_preview(alpha=128)
    preview_overlay(camera, overlay)


def detectMotion():
    while True:
        filename = "{0:%Y}-{0:%m}-{0:%d}".format(now)
        pir.wait_for_motion()
        camera.start_recording(filename)
        pir.wait_for_no_motion()
        camera.stop_recording()


def record():
    camera.start_preview(alpha=128)
    preview_overlay(camera, overlay)

def stop():
    camera.stop_recording()


def playVideo(file):
    os.system("omxplayer" +file)



def getFirstFrame(videofile):
    vidcap = cv2.VideoCapture(videofile)
    success, image = vidcap.read()
    if success:
        filename =  videofile +"thumb.jpg"
        thumbnails.append(filename)
        cv2.imwrite(filename, image)

def media():
    window = Window(app, title="2nd window")
    #window.hide()

    #Locate every file in the current directory that ends in mp4
    for file in os.listdir("."):
        if file.endswith("mp4"):
            getFirstFrame(file)
            print(file)

    x = 50
    y = 75
    for  t in thumbnails:
        print(t)
        picture = PushButton(window, image=t, grid=[x,y], width=50, height=50,command=playVideo(t))
        message = Text(window, t, grid=[x+100, y])

    y = y + 50


app = App("Vivecam", 800, 480, layout="grid")
new_pic = PushButton(app, new_picture, text="New picture",  grid=[0,10])
record = PushButton(app, record, text="Record",  grid=[1, 10])
stop = PushButton(app, stop, text="Stop", grid=[2, 10])
media  = stop = PushButton(app, media, text="Media", grid=[3, 10])

app.display()





    
