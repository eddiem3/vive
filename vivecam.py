import RPi.GPIO as GPIO
import time
import subprocess
import re
from picamera import PiCamera
from time import sleep
import datetime

import os
import smtplib




def turnOffScreen():
    subprocess.call(['xset', 'dpms', 'force','off'])

def turnOnScreen():
    subprocess.call(['xset', 'dpms', 'force','on'])


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    from google.cloud import storage
    from google.cloud import bigquery
    from google.cloud.bigquery.client import Client
    creds = '/home/pi/developemnt/vive-gpio/googlecreds.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds
    bq_client = Client()

    #client = bigquery.Client.from_service_account_json(os.environ['HOME'] +
    #"/.google/googlecreds.json"


    """Uploads a file to the bucket."""
    print("Connecting to Google Cloud  Stoarage")
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    print("Uploading file")
    blob.upload_from_filename(source_file_name)
    blob.make_public()

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


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
    
            
        
def email(filename):

    print("Sending email  notification")
    
    TO = 'amogha@carbonorigins.com'
    SUBJECT = 'Motion Detected'
    TEXT = 'Motion detected. View at ' + '<https://storage.googleapis.com/vivecam/' +filename +'.mp4>'

    # Gmail Sign In
    gmail_sender = 'vivecam001@gmail.com'
    gmail_passwd = 'M00nP!3YUM'
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])

    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print ('email sent')
    except:
        print ('error sending mail')

    server.quit()

turnOffScreen()
print("Initalizing GPIO Pins")
GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.IN) #PIR1
GPIO.setup(24, GPIO.IN) #PIR2



# try:
#    time.sleep(1)
#    while True:
#        pir1 = GPIO.input(23)
#        pir2 = GPIO.input(24)

#        print(pir1,pir2)

# except:
#    GPIO.cleanup()


try:
    time.sleep(1)
    while True:
        pir1 = GPIO.input(23)
        pir2 = GPIO.input(24)
        print("In loop")
        print(pir1,pir2)
        sleep(1)
        #if motion is detected
        if pir1 == 1 or  pir2 == 1:
            turnOnScreen()
            print("Motion Detected...")

            #Get current date and time
            day = datetime.datetime.now()
            format = '%a %b %d %H %M %S %Y'
           
            #Create output filename
            filepath = '../vive-web/public/videos/'

            exh = '.h264' #input extension from PiCamera
            exm =  '.mp4' #output extension after ffmpeg
            
            #filename  = re.sub('[^A-Za-z0-9]+', '', day.strftime(format)).lower() 
            filename  = day.strftime(format)
            input_file_name = filepath + filename + exh
            output_file_name =  filepath + filename +exm
           
            camera = PiCamera()
           
            #Take a picture
            rotation = 270
            imagepath = filepath +filename + '.jpg'
            camera.rotation = rotation
            camera.start_preview()
            sleep(2)
            camera.capture(imagepath)

            #Record Video
            camera.start_recording(input_file_name)
            camera.rotation = rotation
            sleep(10)

        
            print("About to end recording")
            camera.stop_recording()
            camera.stop_preview()
            camera.close()
            print("Finished recording. Converting video.....")
            command = ["ffmpeg", "-f", "h264", "-i",  input_file_name , "-c:v", "copy", output_file_name]
            subprocess.call(command)
            print("Converstion completed. Cleaning up....")
            subprocess.call(["rm", input_file_name])
            print("Uploading to cloud......")
            upload_blob('vivecam',imagepath, filename + '.jpg') #upload image
            upload_blob('vivecam', output_file_name, filename + exm) #upload video
            email(filename)
            subprocess.call(["heroku","restart","-a", "vivecam"])
            turnOffScreen()
            
            
                
except:
    GPIO.cleanup()
               
           
               
          

               
       










#recordVideoPi()
#email('fakefilename.mp4')

#turnOffScreen()




# try:
#    while True:
#        if GIPO.input(23) == 1 or GPIO.input(24) == 1:
#            print("One of the sensors is HIGH PIR ONE: ", pir1, "PIR TWO: ", pir2)
           #if GIPO.input(23) == 0 and GPIO.input(24) == 0:
           #    print("One of the sensors is LOW PIR ONE: ", pir1, "PIR TWO: ", pir2)

     
           
       #     sleep(0.1)
        

           

       #     if(not pir1 and not pir2):
       #         print("PIR ONE AND TWO REPORT LOW")
       #         print("PIR ONE: ", pir1, "PIR TWO: " , pir2)
       #         camera.stop_recording()

       #         subprocess.call(["rm", input_file_name])

            
       #         time.sleep(1)
       #         turnOffScreen()
       #         time.sleep(0.1)




