import RPi.GPIO as GPIO
import time
import datetime as dt
import picamera
import io

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)
savepath="/home/pi/"

#initializes pi camera
def init_camera():
    global camera
    camera = picamera.PiCamera()
    camera.resolution = (1920,1080)
    print('camera initialized')
    camera.annotate_frame_num=True
    camera.annotate_text=dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')

def main():
    global camera
    init_camera()
    start = dt.datetime.now()
    fn_stamp=start.strftime('%Y-%m-%d_%H:%M:%S')
    while (dt.datetime.now()-start).seconds < 30:#True:
        sleep(0.1)
        stream.copy_to(vid_name)
    camera.stop_recording()
    camera.stop_preview()


def maintriggered():
    global camera, istriggered, vid_name, g,start,isrecording
    isrecording=0
    start = dt.datetime.now()
    init_camera()
    GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # input to detect start trigger
    istriggered = 0 # is the trigger input up

    #start = dt.datetime.now()
    #fn_stamp=start.strftime('%Y-%m-%d_%H:%M:%S')
    #logging.basicConfig(filename='test'+ fn_stamp +'.log',filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
    
    #stream=picamera.PiCameraCircularIO(camera, seconds=5)
    #camera.start_recording(stream, format = 'h264')
                
    currstate=0
    GPIO.add_event_detect(27, GPIO.BOTH, callback=triggercallback)    
    try:
        while (True):
            while ((dt.datetime.now()-start).seconds <200) and (istriggered==1):#(GPIO.input(27)==1):         
                camera.annotate_text=dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')
                time.sleep(0.1)
                #print(camera.frame)
                if not g.closed:
                    g.write(str(camera.frame)+"\n")
    except KeyboardInterrupt:
        camera.stop_preview()
        pass
    finally:
        if isrecording==1:
            camera.stop_recording()
        camera.stop_preview()
        GPIO.cleanup()
            


def triggercallback(channel):
    global istriggered, camera, vid_name, g,start,isrecording
    if GPIO.input(27):
        print('trigger up')
        istriggered=1
        camera.start_preview()
        start = dt.datetime.now()
        fn_stamp=start.strftime('%Y-%m-%d_%H:%M:%S')
        vid_name=savepath+"video_triggered" + fn_stamp + ".h264"
        g=open(savepath+"videobody_timestamp" + fn_stamp + ".csv",'a')
        camera.start_recording(vid_name, format = 'h264')
        isrecording =1
    else:
        print('trigger down')
        istriggered=0
        g.close()
        camera.stop_recording()
        isrecording=0
        


#main()
maintriggered()
    

