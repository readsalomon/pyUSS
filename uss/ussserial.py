import serial
from . import telegram
from . import pkw
from binascii import hexlify
import time

STX=0x02

class USSIncorrectSTXException(Exception):
	pass
	
class USSIncorrectLengthException(Exception):
	pass

class USSEmptyResponseException(Exception):
	pass

class USSserial(serial.Serial):
	def __init__(self, port, baudrate=9600, timeout=0.3, parity=serial.PARITY_EVEN):
		super(USSserial, self).__init__(port, baudrate=baudrate, timeout=timeout, parity=parity, stopbits=serial.STOPBITS_ONE)
		
	def sendAndReceive(self, raw_telegram, retry_cnt=1):
			
		for i in range(retry_cnt):
		
			try:
				#start delay
				time.sleep(0.005)

				self.reset_input_buffer()
				
				self.write(raw_telegram)
				c = self.read_until(chr(STX))
				if not c:
					raise USSEmptyResponseException
				if c != chr(STX):
					raise USSIncorrectSTXException
					
				LGE = ord(self.read(1))
				t = bytearray([STX, LGE])+bytearray(self.read(LGE))
				if len(t) != 2+LGE:
					raise USSIncorrectLengthException

				return telegram.SlaveTelegram(t)
			
			except Exception as e:
				if i == retry_cnt-1:
					raise e
				else:
					pass
		
		return None
		
	# This method ensures the telegram is received exactly once by the slave
	# Returns the response iff it has been received uncorrupted
	# otherwise, None is returned
	def sendAndReceiveOnce(self, raw_telegram):

		while True:
			try:
				r = self.sendAndReceive(raw_telegram, retry_cnt=1)
				return r
			except USSEmptyResponseException as e:
				pass
			except Exception as e:
				return None

