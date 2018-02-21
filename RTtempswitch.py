
import thread
import os
import glob
import time
import datetime
import subprocess
from RPi import GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setwarnings(False)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

oncode =  "10001110111010001110100010001110100010001000100010001000100010000000000000000000"#corresponds to the signal that triggers on the rc outlet
offcode = "10001110111010001110100011101000100010001000100010001000100010000000000000000000"#corresponds to the signal that triggers off the rc outlet
slplen = 0.00044


def checktemp(lowtemp,hightemp):
        onoff = 0
        degC, degF = read_temp()
        if degF < lowtemp:
                onoff = 0 #says heater is off if temp is low
        if degF > hightemp:
                onoff = 1 #says heater is on if temp is high
        while 1:
                degC, degF = read_temp()
                if degF < lowtemp and onoff == 0:#if temp is low and heater is off
                        print "----------------------------------------------Turn on"
                        switchon()
                        onoff = 1 #heater is on
                if degF > hightemp and onoff == 1:#if temp is high and heater is on
                        print "----------------------------------------------Turn off"
                        switchoff()
                        onoff = 0 #heater is off

def switchon():
    for i in range (0,9):#send signal 10 times
        for j in range(0 ,len(oncode)):#send signal through rf transmitter
            if(oncode[j] == '1'):
                GPIO.output(11,True)
            elif(oncode[j] == '0'):
                GPIO.output(11,False)
            sleep(slplen)#used to set correct length of signal

def switchoff():
    for i in range (0,9):#send signal 10 times
        for j in range(0 ,len(offcode)):#send signal through rf transmitter
            if(offcode[j] == '1'):
                GPIO.output(11,True)
            elif(offcode[j] == '0'):
                GPIO.output(11,False)
            sleep(slplen)#used to set correct length of signal

def read_temp_raw():
    catdata = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)#opens a pipe to read from the standard stream
    out,err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')#splits lines at newline character
    return lines

def read_temp():
    lines = read_temp_raw() #lines from terminal

    while lines[0].strip()[-3] != 'Y': #if the letter 3 from the end isn't Y(ES)
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=') #find t= in string
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0 #converts string to float
        temp_f = temp_c * 9.0 / 5.0 + 32.0 #converts C to F
        return temp_c, temp_f

def main():
        print "\nstarting..."

        thread.start_new_thread(checktemp, (65,66,))#args are (temp to turn on,temp to turn off,)

        while 1:
                degC,degF = read_temp() #update temp
                print str(datetime.datetime.now()) #show time
                print"Room Temperature: %.2f degrees F" % degF
                print "--------------------------------"
                time.sleep(15)

main()


