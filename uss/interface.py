import ussserial
import telegram
import pkw
import pzd
from binascii import hexlify

type_to_task={	"U16":(pkw.TaskID.write16,pkw.TaskID.writeArray16),
				"I16":(pkw.TaskID.write16,pkw.TaskID.writeArray16),
				"U32":(pkw.TaskID.write32,pkw.TaskID.writeArray32),
				"I32":(pkw.TaskID.write32,pkw.TaskID.writeArray32),
				"Float":(pkw.TaskID.write32,pkw.TaskID.writeArray32)}
				
type_to_args={	"U16":{"as_unsigned":True},
				"I16":{"as_unsigned":False},
				"U32":{"as_unsigned":True, "as_float":False},
				"I32":{"as_unsigned":False, "as_float":False},
				"Float":{"as_unsigned":False, "as_float":True}}

class USSIncorrectParameterInResponseException(Exception):
	pass

class USSDrive(ussserial.USSserial):
	

	
	def __init__(self, port, baudrate=9600, addr=0, pkw_length=127, pzd_length=2):
		if pkw_length!=127:
			raise NotImplementedError("pkw size other than 127")
		if pzd_length!=2:
			raise NotImplementedError("pzd size other than 2")
			
		self.pkw_length=127
		self.pzd_length=pzd_length
		self.addr = addr
			
		super(USSDrive, self).__init__(port, baudrate)
		
	
	def waitForDrive(self):	
		# test drive communication using noTask
		response_ok = False
		while not response_ok:
			task = pkw.Task(taskID=pkw.TaskID.noTask,  param=0, index=0, pwe=0)
			tel = telegram.MasterTelegram(self.addr, task+"\x00\x00"*self.pzd_length)
			r = self.sendAndReceiveOnce(tel)
			if r is not None:
				r = pkw.Response(r[:-self.pzd_length*2])
				if r.responseID == pkw.ResponseID.noResponse:
					response_ok = True

	
		
	
	""" Read paramter
	 	typ is one of ["U16","I16","U32","I32","Float"]
	 	if the parameter is an array, specify index=0..255
	 	index=255 will transfer all elements in one"""
	def read_param(self, param, typ, index=None, retry_cnt=5):
		if index == None:
			index=0
			taskid = pkw.TaskID.requestParam
		else:
			taskid = pkw.TaskID.readArray
		task = pkw.Task(taskID=taskid,  param=param, index=index, pwe=0, **type_to_args[typ])
		tel = telegram.MasterTelegram(self.addr, task+"\x00\x00"*self.pzd_length)
		for i in range(retry_cnt):
			r = self.sendAndReceive(tel, retry_cnt=retry_cnt)
			r = pkw.Response(r[:-self.pzd_length*2], **type_to_args[typ])
			if r.param == param:
				return r
			
		raise USSIncorrectParameterInResponseException
		
	def read_array(self, param, typ):
		return self.read_param(param, typ, index=255)

	def write_param(self, param, typ, val, index=None):
		taskid=type_to_task[typ]
		if index == None:
			index=0
			taskid = taskid[0]
		else:
			# we write into an array
			taskid = taskid[1]
			if type(val) != list:
				# array writes always take a list
				val = [val]
				
		task = pkw.Task(taskID=taskid,  param=param, pwe=val, index=index, **type_to_args[typ])
		tel = telegram.MasterTelegram(self.addr, task+"\x00\x00"*self.pzd_length)
		r=self.sendAndReceiveOnce(tel)
	
	""" vals are a list of parameter values"""
	def write_array(self, param, typ, vals):
		self.write_param(param,typ,vals,index=255)

	""" control drive via setpoint and control word
		see pzd.ControlWord for possible control flags"""
	def control(self, **args):
		task = pkw.Task(taskID=pkw.TaskID.noTask,  param=0, index=0, pwe=0)
		crtl = pzd.PZDM2S(**args)
		tel = telegram.MasterTelegram(self.addr, task+crtl)
		r=self.sendAndReceiveOnce(tel)

	def status(self, ref_freq=0,retry_cnt=5):
		task = pkw.Task(taskID=pkw.TaskID.noTask,  param=0, index=0, pwe=0)
		tel = telegram.MasterTelegram(self.addr, task+"\x00\x00"*self.pzd_length) # the drive will ignore this ControlWord
		r=self.sendAndReceive(tel,retry_cnt=retry_cnt)
		return pzd.pzds2m(r[-self.pzd_length*2:], ref_freq)		
		
			
	
	

