##############################################
# STEREO INMP441 MEMS Microphone + I2S Module
##############################################
#
# -- Stereo frequency analysis with FFTs and
# -- saving .wav files of MEMS mic recording
#
##############################################
#
import pyaudio
import numpy as np
import RPi.GPIO as GPIO
from time import sleep
import time

#Import time library
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)                    # programming the GPIO by BCM pin numbers

#TRIG = 17
#ECHO = 27
#led = 22

m11=16
m12=18
m21=11
m22=13

#GPIO.setup(TRIG,GPIO.OUT)                  # initialize GPIO Pin as outputs
#GPIO.setup(ECHO,GPIO.IN)                   # initialize GPIO Pin as input
#GPIO.setup(led,GPIO.OUT)                  

GPIO.setup(m11,GPIO.OUT)
GPIO.setup(m12,GPIO.OUT)
GPIO.setup(m21,GPIO.OUT)
GPIO.setup(m22,GPIO.OUT)

#GPIO.output(led, 1)

#time.sleep(5)
def stop():
    print("stop")
    GPIO.output(m11, 0)
    GPIO.output(m12, 0)
    GPIO.output(m21, 0)
    GPIO.output(m22, 0)
    
def forward():
    GPIO.output(m11, 1)
    GPIO.output(m12, 0)
    GPIO.output(m21, 1)
    GPIO.output(m22, 0)
    print ("Forward")
    #return
def back():
    GPIO.output(m11, 0)
    GPIO.output(m12, 1)
    GPIO.output(m21, 0)
    GPIO.output(m22, 1)
    print ("back")
    #return
def left():
    GPIO.output(m11, 0)
    GPIO.output(m12, 0)
    GPIO.output(m21, 1)
    GPIO.output(m22, 0)
    print ("left")

def right():
    GPIO.output(m11, 1)
    GPIO.output(m12, 0)
    GPIO.output(m21, 0)
    GPIO.output(m22, 0)
    print ("right")
    #return
def car_go():
    i=0
    avgDistance=0
    for i in range(5):
        GPIO.output(TRIG, False)                 #Set TRIG as LOW
        time.sleep(0.1)                                   #Delay

        GPIO.output(TRIG, True)                  #Set TRIG as HIGH
        time.sleep(0.00001)                           #Delay of 0.00001 seconds
        GPIO.output(TRIG, False)                 #Set TRIG as LOW

        while GPIO.input(ECHO)==0:              #Check whether the ECHO is LOW
            GPIO.output(led, False)             
        pulse_start = time.time()

        while GPIO.input(ECHO)==1:              #Check whether the ECHO is HIGH
            GPIO.output(led, False) 
        pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start #time to get back the pulse to sensor

        distance = pulse_duration * 17150        #Multiply pulse duration by 17150 (34300/2) to get distance
        distance = round(distance,2)                 #Round to two decimal points
        avgDistance=avgDistance+distance

    avgDistance=avgDistance/5
    print ("avgdis: ",avgDistance)
    flag=0
    #count=0
    if avgDistance < 15:      #Check whether the distance is within 15 cm range
        count=count+1
        stop()
        time.sleep(1)
        back()
        time.sleep(1.5)
        if (count%3 ==1) & (flag==0):
            right()
            flag=1
        else:
            left()
            flag=0
            time.sleep(1.5)
            stop()
            time.sleep(1)
    else:
        forward()
        flag=0
    return 1





def tonum(num):
        fm=10.0/180
        num=num*fm+2.5
        num=int(num*10)/10.0
        return num
servopin1=14
servopin2=15

GPIO.setmode(GPIO.BCM)
GPIO.setup(servopin1,GPIO.OUT,initial=False)
GPIO.setup(servopin2,GPIO.OUT,initial=False)
p1=GPIO.PWM(servopin1,50)
p2=GPIO.PWM(servopin2,50)

p1.start(tonum(0))
p2.start(tonum(0))
sleep(0.5)
#p1.ChangeDutyCycle(0)
#p2.ChangeDutyCycle(0)
sleep(0.1)

a=0
c=0
b=0
d=4

q=[0,10,20,30,45,50,60,70,80,90,100,110,120,135,140,150,160,170,180]

##############################################
# function for setting up pyserial
##############################################
#
def pyserial_start():
    audio = pyaudio.PyAudio() # create pyaudio instantiation
    ##############################
    ### create pyaudio stream  ###
    # -- streaming can be broken down as follows:
    # -- -- format             = bit depth of audio recording (16-bit is standard)
    # -- -- rate               = Sample Rate (44.1kHz, 48kHz, 96kHz)
    # -- -- channels           = channels to read (1-2, typically)
    # -- -- input_device_index = index of sound device
    # -- -- input              = True (let pyaudio know you want input)
    # -- -- frmaes_per_buffer  = chunk to grab and keep in buffer before reading
    ##############################
    stream = audio.open(format = pyaudio_format,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=CHUNK)
    stream.stop_stream() # stop stream to prevent overload
    return stream,audio

def pyserial_end():
    stream.close() # close the stream
    audio.terminate() # close the pyaudio connection

def mic_localization():

    ##############################
    ###### initial variable ######
    data = []
    left_arr = []
    right_arr = []
    l_amp_max = 0
    r_amp_max = 0
    l_max_indx = -1
    r_max_indx = -1
    indx_arr = []
    l_r_value = []
    pos_indx = [0] * 6
    pos_arr = []
    ##############################

    ##############################
    # stream info
    ##############################
    stream_data = stream.read(CHUNK,exception_on_overflow=False)
    data.append(np.frombuffer(stream_data,dtype=buffer_format))
    for chan in range(0,chans):
        data_chunks = [data[ii][chan:][::2] for ii in range(0,np.shape(data)[0])]
        if chan == 0:
            for frame in data_chunks:
                left_arr.extend(frame)
        elif chan == 1:
            for frame in data_chunks:
                right_arr.extend(frame)
    ##############################

    ##############################
    # get peak index diff
    ##############################
    for indx in range(0, len(left_arr)):
        if left_arr[indx] > l_amp_max:
            l_amp_max = left_arr[indx]
            l_max_indx = indx
        if right_arr[indx] > r_amp_max:
            r_amp_max = right_arr[indx]
            r_max_indx = indx
        if indx % clip == 0 and l_amp_max > noice_amp and r_amp_max > noice_amp:
            if l_max_indx != -1 and r_max_indx != -1:
                l_r_value.append((left_arr[l_max_indx], right_arr[r_max_indx],\
                                  left_arr[l_max_indx]-right_arr[r_max_indx]))
                indx_arr.append(l_max_indx - r_max_indx)
            l_max_indx = -1
            r_max_indx = -1
            l_amp_max = 0
            r_amp_max = 0
    ##############################

    ##############################
    # counter each direction
    ##############################
    for item in range(0, len(indx_arr)):
        if abs(indx_arr[item]) < 35:
#            print('indx_diff:', indx_arr[item])
#            print('left amp:', l_r_value[item][0], ',right amp:', l_r_value[item][1],\
#                  'l-r:', l_r_value[item][2])
            if indx_arr[item] >= -4 and indx_arr[item] <= 4: #in the degree 90
                pos_indx[3] = pos_indx[3] + 1
            elif indx_arr[item] > 4 and indx_arr[item] <= 13: #in the degree 135
                pos_indx[2] = pos_indx[2] + 1
            elif indx_arr[item] > 13: #in the degree 180
                pos_indx[1] = pos_indx[1] + 1
            elif indx_arr[item] >= -13 and indx_arr[item] < -4: #in the degree 45
                pos_indx[4] = pos_indx[4] + 1
            elif indx_arr[item] < -13: #in the degree 0
                pos_indx[5] = pos_indx[5] + 1
    ##############################

    if any(pos_indx):
        pos_max = max(pos_indx)
        if pos_max > 3:
            pos_arr.append(pos_indx.index(pos_max))
            for elem in range(1, len(pos_indx)):
                if pos_indx[elem] == pos_max and elem != pos_indx.index(pos_max):
                    pos_arr.append(elem)
            for pos in pos_arr:
                print('pos:', pos, ', pos value:', pos_indx[pos])
                print('len',len(pos_arr))
    print('')
    return pos_arr
# 1 to 5: 180 135 90 45 0
def turn_angle(dir):
#    if dir == 1:
#        p1.ChangeDutyCycle(tonum(q[0]))
#        p2.ChangeDutyCycle(tonum(q[18]))
#        print('dir: ',dir,'degree: ',q[18])

#        sleep(0.5)
    if dir == 2:
        p1.ChangeDutyCycle(tonum(q[13]))
        p2.ChangeDutyCycle(tonum(q[9]))
        print('dir: ',dir,'degree: ',q[13])

        sleep(0.5)

    if dir == 3:
        p1.ChangeDutyCycle(tonum(q[9]))
        p2.ChangeDutyCycle(tonum(q[9]))
        print('dir: ',dir,'degree: ',q[9])

        sleep(0.5)
        
    if dir == 4:
        p1.ChangeDutyCycle(tonum(q[9]))
        p2.ChangeDutyCycle(tonum(q[4]))
        print('dir: ',dir,'degree: ',q[4])

        sleep(0.5)

#    if dir == 5:
#        p1.ChangeDutyCycle(tonum(q[0]))
#        p2.ChangeDutyCycle(tonum(q[0]))
#        print('dir: ',dir,'degree: ',q[0])

#        sleep(0.5)




#
##############################################
# Main Data Acquisition Procedure
##############################################
#
if __name__=="__main__":

    #
    ###########################
    # acquisition parameters
    ###########################
    #
    CHUNK          = 44100 // 2  # frames to keep in buffer between reads
    samp_rate      = 44100 # sample rate [Hz]
    pyaudio_format = pyaudio.paInt16 # 16-bit device
    buffer_format  = np.int16 # 16-bit for buffer
    chans          = 2 # only read 1 channel
    dev_index      = 0 # index of sound device


    ######car setting
    stop()
    count=0


    #
    #############################
    # stream info and data saver
    #############################
    # initial variable
    #############################
    #
    stream,audio = pyserial_start() # start the pyaudio stream
    clip_count = 30
    clip = CHUNK / clip_count
    noice_amp = 20
    #
    #############################

    stream.start_stream()
    stream.read(samp_rate,exception_on_overflow=False)
    print('Recording Started.')
    
    while True:
        #dir_arr = []
        
        try:
            #for car
#            i=0
#            avgDistance=0
            #for car
            dir_arr = []
            dir_arr = mic_localization()
            if len(dir_arr) == 1:
                turn_angle(dir_arr[0])
                print("dir_arr: ",dir_arr[0])
                member=True #if the voice is from a member of our family
#                if dir_arr[0] == 3 and member==True:
#                    car_go()



#            turn_angle(1)
#            turn_angle(2)
#            turn_angle(3)
#            turn_angle(4)
#            turn_angle(5)
            #else:





        except KeyboardInterrupt:
            print('keyboard interrupt.')
            raise

    stream.stop_stream()
    print('Recording Stopped.')
    pyserial_end()

