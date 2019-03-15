import sys
import struct


STX=0x02

def get_bcc(telegram_bytes):
	bcc = 0
	for c in telegram_bytes:
		bcc = bcc ^ c
	return bcc

class USSUndefinedAddressException(Exception):
	pass

class USSEmptyNetDataException(Exception):
	pass

class USSIncorrectBCCException(Exception):
	pass
	
		
class MasterTelegram(bytearray):

	"""
	net_data is of tpye bytearray
	"""
	def __init__(self, addr, net_data, mirror=False):
		
		if len(net_data) == 0:
			raise  USSEmptyNetDataException
		
		if addr > 31:
			raise USSUndefinedAddressException

		_raw = bytearray(len(net_data)+4)
		_raw[3:-1] = net_data
		_raw[0] = STX					#STX
		_raw[1] = len(net_data)+2		#LGE
		_raw[2] = addr					#ADR
		
		if mirror:
			_raw[2] = _raw[2] | 0b01000000
		
		_raw[-1] = 0 					#BCC
		_raw[-1] = get_bcc(_raw)
		
		super(MasterTelegram, self).__init__( _raw )		
			
		
		
class SlaveTelegram(bytearray):
	def __init__(self, raw):
		
		if get_bcc(raw) != 0x0:
			raise USSIncorrectBCCException
			
		self.LGE = raw[1]
		self.ADR = raw[2]
		super(SlaveTelegram, self).__init__( raw[3:-1] )
