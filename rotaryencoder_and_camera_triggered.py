import RPi.GPIO as GPIO
import threading
from time import sleep
import datetime as dt
import picamera
#import logging

#GPIO ports: input 4 for Channel A, input 14 for Channel B
Enc_A = 4
Enc_B = 14

rotaryCounter=0

Current_A = 1 
Current_B = 1

LockRotary = threading.Lock()

savepath="/home/pi/"

#initializes interrupt handlers
def init_encoder():
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Enc_A, GPIO.IN)
    GPIO.setup(Enc_B, GPIO.IN)

    GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=rotary_interrupt)
    GPIO.add_event_detect(Enc_B, GPIO.RISING, callback=rotary_interrupt)
    return

#initializes pi camera
def init_camera():
    global camera
    camera = picamera.PiCamera()
    camera.resolution = (1920,1080)
    print('camera initialized')
    camera.annotate_frame_num=True


def rotary_interrupt(A_or_B):
    global rotaryCounter, Current_A, Current_B, LockRotary
    Switch_A = GPIO.input(Enc_A)
    Switch_B = GPIO.input(Enc_B)

    if (Current_A == Switch_A and Current_B == Switch_B): #same as before
        return

    Current_A = Switch_A
    Current_B = Switch_B    # actually not sure we need this

    if (Switch_A and Switch_B):
        LockRotary.acquire()
        if A_or_B == Enc_B:
            rotaryCounter += 1
        else:
            rotaryCounter -= 1
        LockRotary.release()
    return


def main():
    global rotaryCounter, LockRotary
    newCounter = 0
    turnCounter = 0
    init_encoder()
    start = dt.datetime.now()
    fn_stamp=start.strftime('%Y-%m-%d_%H:%M:%S')
    logging.basicConfig(filename='test'+ fn_stamp +'.log',filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
    while (dt.datetime.now()-start).seconds < 30:#True:
        sleep(0.1)
        LockRotary.acquire()
        newCounter = rotaryCounter # get counter value
        LockRotary.release()
        if(newCounter != 0):
            if (rotaryCounter>125):
                newCounter = 0
                rotaryCounter = 0
                turnCounter += 1
            logging.info('Counter %s',newCounter)
            logging.info('Turn %s', turnCounter)
            print(newCounter, turnCounter)


def maintriggered():
    global camera, rotaryCounter, LockRotary, istriggered, newCounter, f, g, vid_name, isrecording,start

    newCounter = 0
    turnCounter = 0
    init_encoder()
    init_camera()
    GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # input to detect start trigger
    istriggered = 0 # is the trigger input up

    start = dt.datetime.now()
    #logging.basicConfig(filename='test'+ fn_stamp +'.log',filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
    
    #stream=picamera.PiCameraCircularIO(camera, seconds=3)


    GPIO.add_event_detect(27, GPIO.BOTH, callback=triggercallback)    
    try:
        while (True):
            while ((dt.datetime.now()-start).seconds<200) and (istriggered==1):#(GPIO.input(27)==1):
                camera.annotate_text=dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')
                sleep(0.1)
                LockRotary.acquire()
                newCounter = rotaryCounter # get counter value
                LockRotary.release()
                if not g.closed:
                    g.write(str(camera.frame)+"\n")
                if (newCounter != 0):
                    if not f.closed:
                        f.write(dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')+"\t"+str(rotaryCounter)+"\n")
                        ##logging.info('Counter %s',newCounter)
    except KeyboardInterrupt:
        camera.stop_preview()
        pass
    finally:
        if isrecording==1:
            camera.stop_recording()
        camera.stop_preview()
        GPIO.cleanup()
            


def triggercallback(channel):
    global istriggered,camera,newCounter,f, g,rotaryCounter,vid_name,isrecording,start
    if GPIO.input(27):
        print('trigger up')
        istriggered=1
        newCounter=0
        rotaryCounter=0
        camera.start_preview()
        start = dt.datetime.now()
        fn_stamp=start.strftime('%Y-%m-%d_%H:%M:%S')
        vid_name=savepath+"video_eye" + fn_stamp +".h264"
        camera.start_recording(vid_name,format='h264')
        isrecording=1
        f=open(savepath+'treadmill'+ fn_stamp +'.csv','a')
        g=open(savepath+'video_timestamp'+ fn_stamp + '.csv','a')
        #logging.basicConfig(filename='test'+ fn_stamp +'.log',filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
    else:
        print('trigger down')
        istriggered=0
        f.close()
        g.close()
        #camera.stop_preview()
        camera.stop_recording()
        isrecording=0
        


#main()
maintriggered()
    

