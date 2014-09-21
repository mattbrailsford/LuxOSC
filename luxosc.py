from OSC import OSCServer,OSCClient, OSCMessage
import OSC
import sys
from time import sleep
import time
import types
import os
import RPi.GPIO as GPIO
from Adafruit_PWM_Servo_Driver import PWM

runState = True

server = OSCServer( ("192.168.0.12", 8000) )#This has to be the IP of the RaspberryPi on the network
client = OSCClient()
pwm = PWM(0x40, debug=True)

neckMin = 140
neckMax = 610

tiltMin = 110
tiltMax = 520

panMin = 60
panMax = 625

pwm.setPWMFreq(60)

#Helper methods
def arduino_map(x, in_min, in_max, out_min, out_max):
     return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# FADERS
#################################################################################################################################################
def fader(path, tags, args, source): 
	value = int(args[0])#Value is the variable that will transform the input from the faders into whole numbers(easier to deal with); it will also get the 'y' value of the XP pads
	#mapped_value = arduino_map(value, 0, 180, servoMin, servoMax) 
	print "Fader: ",value
	#print "Mapped: ",mapped_value
	pwm.setPWM(0, 0, arduino_map(value, 0, 100, neckMin, neckMax))

# XY PADS
###############################################################################################################################################
def xypad(path, tags, args, source):
	yy = int(args[0])
	xx = int(args[1])#Value 2 is used with XP pads, it will get the 'x' value
	print "XYPad: x=",xx,", y=",yy
	pwm.setPWM(1, 0, arduino_map(xx, 0, 100, panMin, panMax))
	pwm.setPWM(2, 0, arduino_map(yy, 0, 100, tiltMin, tiltMax))
 
# BUTTONS
####################################################################################################################################################
def button(path, tags, args, source):
	state=int(args[0])
	print "Button: ",state
	pwm.setPWM(0,0,0)
	pwm.setPWM(1,0,0)
	pwm.setPWM(2,0,0)
	runState = False

# define a message-handler function for the server to call.
def printer(addr, tags, stuff, source):
   	print "---"
    	print "received new osc msg from %s" % OSC.getUrlStr(source)
    	print "with addr : %s" % addr
    	print "typetags %s" % tags
    	print "data %s" % stuff
    	print "---"

#These are all the add-ons that you can name in the TouchOSC layout designer (you can set the values and directories)
server.addMsgHandler("/1/neck", fader)
server.addMsgHandler("/1/head", xypad)
server.addMsgHandler("/1/btn", button)

while runState:
	print "Waiting..."

server.close()
#This will kill the server when the program ends
