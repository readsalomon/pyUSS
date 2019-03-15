from . import pkw
from . import pzd
from .telegram import *
import serial
import subprocess
from binascii import hexlify
import traceback

class TestFailedException(Exception):
	def __init__(self, reason, test):
		super(TestFailedException, self).__init__("Reason: %s\nOn following test:\n%s"%(reason, str(test)))

list_test_pkw = [
	#Set P0700 to value 5 (0700 = 2BC (hex))
	( bytearray.fromhex("22BC00000005") , bytearray.fromhex("12BC00000005") , 
	dict(taskID=pkw.TaskID.write16,  param=700, pwe=5),
	lambda r: r.responseID == 1 and r.param == 700 and r[0] == 5 )

]

def test_pkw(s1, s2):
	
	for t in list_test_pkw:
		m2s, s2m, task, check_r = t
		try:
			mt = pkw.Task(**task) 
		except Exception as e:
			raise TestFailedException( traceback.format_exc(), t )			
		if not mt == m2s:
			raise TestFailedException("Master2Slave Task telegram incorrect", t)
		try:	
			s2.write( MasterTelegram(0x1,s2m) )
			r = pkw.Response( s1.sendAndReceive( MasterTelegram(0x1,mt)	 ) )
		except Exception as e:
			raise TestFailedException( traceback.format_exc(), t )
		if not check_r( r ):
			raise TestFailedException("Response check incorrect", t)
			
		


def setup_socat_VSP():
	return subprocess.Popen(["socat", "-d", "-d", "pty,raw,echo=0", "pty,raw,echo=0"],stderr=subprocess.PIPE)
	
def get_socat_serials(socat_proc):
	l1 = socat_proc.stderr.readline()
	l2 = socat_proc.stderr.readline()
	p1 = l1.split()[-1]
	p2 = l2.split()[-1]
	
	###
	print("P1: %s P2: %s"%(p1, p2))
	###
	
	return ( USSserial(p1), USSserial(p2) )

def main():
	
	socat_proc = setup_socat_VSP()
	s1, s2 = get_socat_serials(socat_proc)
	
	test_pkw(s1,s2)
	
	socat_proc.terminate()


if __name__ == "__main__":
    # execute only if run as a script
    main()
