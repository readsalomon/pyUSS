import uss
from uss.g110 import quick_params as q
import sys
import struct
from binascii import hexlify
import time


# define parameters values for a G110 inverter drive
g110_params = {
	"cmdsrc":5,
	"setpointsrc":5,
	"voltage":220,
	"current":8.5,
	"power":2.2,
	"freq":50.0,
	"speed":2900,
	"minfreq":25.0,
	"maxfreq":400.0,
	"cooling":1,
}


def f32(f):
	return struct.unpack("f",struct.pack("f",f))[0]

def check_param(p,q):
	if type(p)==float:
		return f32(p) == f32(q)
	else:
		return p == q


if __name__ == "__main__":
	if len(sys.argv)!=2:
		print("Usage: %s <serial port>"%sys.argv[0])
		exit()
	
	port = sys.argv[1]

	ser = uss.USSDrive(port)  # open serial port
	print("Connecting to %s"%(ser.name))    # check which port was really used

	# wait for serial communication
	ser.waitForDrive()

	# read parameter number 1234 (Float):
	print(ser.read_param(1234,"Float"))
	
	# read parameter 974 (U16 array of size 7) 
	print(ser.read_array(974,"U16"))
	
	# write parameter 810 (U16) , value=2
	ser.write_param(810,"U16",2)
	

	# do a quick commissioning of a G110 drive
	ser.write_param(*q["accesslevel"], val=3)
	ser.write_param(*q["commission"], val=1)
	for n, v in g110_params.iteritems():
		ser.write_param(*q[n], val=v)
	ser.write_param(*q["quickcomm"], val=1)

	time.sleep(2)

	# verify all parameters just commissioned
	for n, v in g110_params.iteritems():
		r = ser.read_param(*q[n])[0]
		if not check_param(r, v):
			print("Param %s incorrect: %s %s"%(n, str(v),  str(r)))
			exit(1)


	# control drive --> turn it off
	ser.control(on=0,noOFF2=1,noOFF3=1,pulseEnable=1,rampEnable=1,rampStart=1,setpointEnable=0, faultAck=0, jogRight=0, controlFromPLC=1)

	# get the drive status
	s=ser.status()
	# print the drive status bits and the actual setpoint
	print(s[0].__dict__, s[1])
	
	# control drive --> turn it on	, setpoint = 0x3000 (relative)
	ser.control(setpoint=0x3000,on=1,noOFF2=1,noOFF3=1,pulseEnable=1,rampEnable=1,rampStart=1,setpointEnable=1, faultAck=0, jogRight=0, controlFromPLC=1)
	
	# get and print status and actual setpoint
	s=ser.status()
	print(s[0].__dict__, s[1])
	
	time.sleep(3)
	
	# control drive --> turn it off
	ser.control(on=0,noOFF2=1,noOFF3=1,pulseEnable=1,rampEnable=1,rampStart=1,setpointEnable=0, faultAck=0, jogRight=0, controlFromPLC=1)
	
	ser.close()
