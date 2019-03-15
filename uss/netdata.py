import telegram
from struct import pack, unpack
from binascii import hexlify

class TaskID(object):
	noTask, requestParam, write16, write32, readDesc, writeDesc, readArray, writeArray16, writeArray32, numArray, _, writeArrayEEPROM32, writeArrayEEPROM16, writeEEPROM32, writeEEPROM16, rwText = range(16)

class ResponseID(object):
	noResponse, xferParam16, xferParam32, xferDesc, xferArray16, xferArray32, xferNum, cannotExec, noPKWRights, changeReport16, changeReport32, changeReportArray16, changeReportArray32 ,_,_,transferText = range(16)

class ErrorID(object):
	illegalPNU, paramConnotBeChanged, limitViolated, wrongID, noArray, incorrectDataType, notPermitted, descNoChange = range(8)


class USSInsufficientPKWSizeException(Exception):
	pass


class PKWTask(bytearray):
	
	def __init__(self, taskID=0, param=0, pwe=0, index=0, pkw_number=127):
		PKE = taskID<<12 | param
		
		f_IND, f_PWE = {
			TaskID.noTask : (lambda x: 0, lambda x: "\x00\x00"),
			TaskID.requestParam : (lambda x: 0, lambda x: "\x00\x00"),
			TaskID.write16 : (lambda x: 0, lambda x: pack(">H",x)),
			TaskID.write32 : (lambda x: 0, lambda x: pack(">I",x)),
			TaskID.readDesc : (lambda x: x, lambda x: "\x00\x00")
		}.get(taskID)
		
		IND = f_IND(index)
		PWE = f_PWE(pwe)
		
		if pkw_number -2 < len(PWE):
			raise USSInsufficientPKWSizeException
		if pkw_number != 127:
			PWE = PWE + "\x00\x00"*(pkw_number-2-len(PKE)/2)	#pad to fixed size PKW
			
		super(PKWTask, self).__init__( pack(">H", PKE) + pack(">H", IND) + PWE )
		

	
	
class PKWResponse(list):
	
	def __init__(self, response_bytes):
		PKE,IND = unpack(">HH", response_bytes)
		self.responseID = PKE>>12
		PWE = response_bytes[4:]
		
		#	noResponse, xferParam16, xferParam32, xferDesc, xferArray16, xferArray32, xferNum
		f_pwe = {
			noResponse : lambda x: ["\x00\x00"],
			xferParam16 : lambda x: [unpack(">H",x)],
			xferParam32 : lambda x: [unpack(">I",x)],
			xferDesc : lambda x: [unpack(">H",x)],
			xferArray16 : lambda x: [unpack(">H",x)],
			cannotExec : lambda x: [unpack(">H",x)]
		}.get(self.responseID)
		
		super(PKWResponse, self).__init__(f_pwe(PWE))
		"""
	def __getitem__(self, i):
		
	def next(self):
		if self.i > len(self.pwe):
			raise StopIteration
		else:
			self.i += 1
			return self.pwe[i - 1]	"""


		
		
		
