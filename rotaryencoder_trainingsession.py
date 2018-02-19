# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 20:10:03 2018

@author: tranvaa
"""
# records running during habituation/training session (rotary encoder only)

import RPi.GPIO as GPIO
import threading
from time import sleep
import datetime as dt

#GPIO ports: input 4 for Channel A, input 14 for Channel B
Enc_A = 4
Enc_B = 14

rotaryCounter=0

Current_A = 1 
Current_B = 1

LockRotary = threading.Lock()

savepath="/home/pi/"
trainingDuration = 15 # in minutes

#initializes interrupt handlers
def init_encoder():
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Enc_A, GPIO.IN)
    GPIO.setup(Enc_B, GPIO.IN)

    GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=rotary_interrupt)
    GPIO.add_event_detect(Enc_B, GPIO.RISING, callback=rotary_interrupt)
    return

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
    init_encoder()
    start = dt.datetime.now()
    fn_stamp=start.strftime('%Y-%m-%d_%H:%M:%S')
    f=open(savepath+'treadmill'+ fn_stamp +'.csv','a')
    end_session = start + datetime.timedelta(minutes = trainingDuration)
    while (dt.datetime.now()-start).seconds < 10:#True:
        LockRotary.acquire()
        newCounter = rotaryCounter # get counter value
        LockRotary.release()
        if(newCounter != 0):
            f.write(dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')+"\t"+str(rotaryCounter)+"\n")
            print(newCounter)
    camera.stop_recording()
    #camera_stop_preview()
    f.close()