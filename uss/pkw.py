from struct import pack, unpack, Struct
from binascii import hexlify
from enumhelper import *


class TaskID(object):
	noTask, requestParam, write16, write32, readDesc, writeDesc, readArray, writeArray16, writeArray32, numArray, _, writeArrayEEPROM32, writeArrayEEPROM16, writeEEPROM32, writeEEPROM16, rwText = range(16)

class ResponseID(object):
	noResponse, xferParam16, xferParam32, xferDesc, xferArray16, xferArray32, xferNum, cannotExec, noPKWRights, changeReport16, changeReport32, changeReportArray16, changeReportArray32 ,_,_,transferText = range(16)

class ErrorID(object):
	illegalPNU, paramConnotBeChanged, limitViolated, wrongID, noArray, incorrectDataType, notPermitted, descNoChange = range(8)

TaskID2ResponseID={
	TaskID.noTask: (ResponseID.noResponse,),
	TaskID.requestParam: (ResponseID.xferParam16, ResponseID.xferParam32),
	TaskID.readArray: (ResponseID.xferArray16, ResponseID.xferArray32)
}


def pnu_extension(pnu):
	if pnu < 2000:
		return (pnu, 0x0)
	if 2000 <= pnu < 4000:
		return (pnu-2000, 0x80)
	if 4000 <= pnu < 6000:
		return (pnu-4000, 0x10)
	if 6000 <= pnu < 8000:
		return (pnu-6000, 0x90)
	if 8000 <= pnu < 10000:
		return (pnu-8000, 0x20)
		
pnu_offset = {
	0x0:0,
	0x80:2000,
	0x10:4000,
	0x90:6000,
	0x20:8000
}
		
class Task(bytearray):
	
	def __init__(self, taskID=0, param=0, pwe=0, index=0, as_float=False, as_unsigned=True, pkw_number=127):
		self.taskID = taskID
		self.taskIDstr = getEnumString(TaskID, taskID)
		self.index = index
		self.pwe = pwe
		self.param = param

		(pnu, ext ) = pnu_extension(param)
		
		PKE = taskID<<12 | pnu
		
		f_IND, f_PWE = {
			TaskID.noTask : (lambda x: 0, lambda x: "\x00\x00"),
			TaskID.requestParam : (lambda x: x, lambda x: "\x00\x00"),
			TaskID.write16 : (lambda x: 0, lambda x: pack(">H",x) if as_unsigned else pack(">h",x)),
			TaskID.write32 : (lambda x: 0, lambda x: pack(">f", x) if as_float else pack(">I",x) if as_unsigned else pack(">i",x)),
			TaskID.readDesc : (lambda x: x, lambda x: "\x00\x00"),
			TaskID.readArray: (lambda x: x, lambda x: "\x00\x00"),
			TaskID.writeArray16: (lambda x: x, lambda x: pack(">"+str(len(x))+"H",*x) if as_unsigned else pack(">"+str(len(x))+"h",*x)),
			TaskID.writeArray32: (lambda x: x, lambda x: pack(">"+str(len(x))+"f", *x) if as_float else pack(">"+str(len(x))+"I",*x) if as_unsigned else pack(">"+str(len(x))+"i",*x))
		}.get(taskID)
		
		IND = f_IND(index) | ext<<8
		PWE = f_PWE(pwe)
		
		if pkw_number != 127:
			raise NotImplementedError("pkw size other than 127")
			
		super(Task, self).__init__( pack(">H", PKE) + pack(">H", IND) + PWE )
		

	
	
class Response(list):
	
	def __init__(self, response_bytes, as_float=False, as_unsigned=True):
		PKE,IND = unpack(">HH", response_bytes[:4])
		self.responseID = PKE>>12
		self.responseIDstr = getEnumString(ResponseID, self.responseID)
		
		pnu = PKE & 0b11111111111
		ext = (IND>>8)&0b11111100
		try:
			self.param = pnu+pnu_offset[ext]
		except:
			self.param = 0

		PWE = response_bytes[4:]
		
		nPWE = str(len(PWE)/2)
		
		#	noResponse, xferParam16, xferParam32, xferDesc, xferArray16, xferArray32, xferNum
		pwe_interpreter = {
			ResponseID.noResponse : "",
			ResponseID.xferParam16 : ">H" if as_unsigned else ">h",
			ResponseID.xferParam32 :">f" if as_float else ">I" if as_unsigned else ">i",
			ResponseID.xferDesc : ">H",
			ResponseID.xferArray16 :">"+nPWE+"H" if as_unsigned else ">"+nPWE+"h",
			ResponseID.xferArray32 :">"+nPWE+"f" if as_float else ">"+nPWE+"I" if as_unsigned else ">"+nPWE+"i",
			ResponseID.cannotExec : ">H",
			ResponseID.noPKWRights : ">H",
			ResponseID.changeReport16: ">H",
			ResponseID.changeReport32: ">H",
			ResponseID.changeReportArray16: ">H",
			ResponseID.changeReportArray32 : ">H",
			ResponseID.transferText: ">H",
		}.get(self.responseID)

		pwe_struct = Struct(pwe_interpreter)
		self.bytesize = pwe_struct.size
		
		super(Response, self).__init__(pwe_struct.unpack_from(PWE))


		
		
		
