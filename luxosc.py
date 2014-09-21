# Imports
import sys
import time
import types
import threading
import OSC

from time import sleep
from OSC import OSCServer,OSCClient, OSCMessage
from Adafruit_PWM_Servo_Driver import PWM

# Welcome
print r" ___       ___  ___     ___    ___ ________  ________  ________      "
print r"|\  \     |\  \|\  \   |\  \  /  /|\   __  \|\   ____\|\   ____\     "
print r"\ \  \    \ \  \\\  \  \ \  \/  / | \  \|\  \ \  \___|\ \  \___|     "
print r" \ \  \    \ \  \\\  \  \ \    / / \ \  \\\  \ \_____  \ \  \        "
print r"  \ \  \____\ \  \\\  \  /     \/   \ \  \\\  \|____|\  \ \  \____   "
print r"   \ \_______\ \_______\/  /\   \    \ \_______\____\_\  \ \_______\ "
print r"    \|_______|\|_______/__/ /\ __\    \|_______|\_________\|_______| "
print r"                       |__|/ \|__|             \|_________|          "
print r"                                                                     "                                                                    

# Variables
address = '192.168.0.12',8000

neckMin = 140
neckMax = 610
tiltMin = 110
tiltMax = 520
panMin  = 60
panMax  = 625

server = OSCServer(address)
#server.addDefaultHandlers()

pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)

# Helper methods
def arduino_map(x, in_min, in_max, out_min, out_max):
     return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Handlers
def elbow(path, tags, args, source): 
	value = int(args[0]) 
	print "Elbow: ",value
	pwm.setPWM(0, 0, arduino_map(value, 0, 100, neckMin, neckMax))

def head(path, tags, args, source):
	yy = int(args[0])
	xx = int(args[1])
	print "Head: ",xx,",",yy
	pwm.setPWM(1, 0, arduino_map(xx, 0, 100, panMin, panMax))
	pwm.setPWM(2, 0, arduino_map(yy, 0, 100, tiltMin, tiltMax))
 
def btn(path, tags, args, source):
	state=int(args[0])
	print "Btn: ",state
	if state == 1:
		pwm.setPWM(0,0,0)
		pwm.setPWM(1,0,0)
		pwm.setPWM(2,0,0)

def printer(addr, tags, stuff, source):
   	print "---"
    	print "received new osc msg from %s" % OSC.getUrlStr(source)
    	print "with addr : %s" % addr
    	print "typetags %s" % tags
    	print "data %s" % stuff
    	print "---"

# Hookup handlers
server.addMsgHandler("/1/elbow", elbow)
server.addMsgHandler("/1/head", head)
server.addMsgHandler("/1/btn", btn)

# Main 
print "\nRegistered Callback Functions:"
for addr in server.getOSCAddressSpace():
    print addr

print "\nStarting OSCServer. Use Ctrl-C to quit."
st = threading.Thread( target = server.serve_forever )
st.start()

try:
	while 1:
		#print "Waiting..."
		sleep(5)

except KeyboardInterrupt:
	print "\nClosing OSCServer."
	server.close()
	print "Waiting for Server thread to finish."
	st.join()
	print "Done!"
