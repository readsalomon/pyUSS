from struct import pack, unpack
from enumhelper import *

class StatusWord(object):
	MAX = 11
	readyToSwitchOn, readyToRun, running, fault, noOff2, noOff3, switchOnInhibit, alarm, setpointInTolerance, controlRequested, fReached = range(MAX) 

class ControlWord(object):
	MAX = 11
	on, noOFF2, noOFF3, pulseEnable, rampEnable, rampStart, setpointEnable, faultAck, jogRight, jogLeft, controlFromPLC = range(MAX)

class USSUnknownPZDControlWordBitException(Exception):
    def __init__(self, message):
        super(USSUnknownPZDControlWordBitException, self).__init__(message)

class Control(bytearray):
	def __init__(self,**args):
		
		control_word=0
		
		for a in args:
			try:
				bit = ControlWord.__dict__[a]
			except:
				raise USSUnknownPZDControlWordBitException(a)
			
			if args[a]:
				control_word = control_word | 0b1<<bit
		
		super(Control, self).__init__(pack(">H", control_word))

class PZDM2S(bytearray):
	def __init__(self,setpoint=0,ref_freq=0,**args):
		if ref_freq:
			#assuming setpoint is absolute freq
			rel_setp = int( (setpoint/ref_freq)*0x4000 )
		else:
			rel_setp = int(setpoint)
		
		if abs(rel_setp) > 0x7fff:
			raise ValueError
			
		crtl = Control(**args)
			
		super(PZDM2S, self).__init__(crtl+pack(">h",rel_setp))
		
def pzds2m(raw, ref_freq=0):
	
	status = Status(raw[:2])
	
	actual = unpack(">h",raw[2:])[0]
	
	if ref_freq:
		#assuming setpoint is absolute freq
		actual = ((1.0*actual)/0x4000)*ref_freq
	
	return (status, actual)

class Status(list):
	def __init__(self,raw_status_word):
		status_word = unpack(">H", raw_status_word[:2])[0]
		
		l = [(status_word>>i)&0b1 for i in range(StatusWord.MAX)]
		
		for i in range(StatusWord.MAX):
			self.__dict__[getEnumString(StatusWord, i)] = l[i]
			
		super(Status, self).__init__(l)
