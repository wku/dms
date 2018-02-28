import sys
import time

import conf
class parent_class:
	def __init__(self):
		self.logfile =  conf.log_filename

	def log(self,msg):
		msg = "%s -:- %s "%(time.ctime(),msg)
		if '--no-stdout' not in sys.argv[1:]:
			print(msg)
		if '--no-log' not in sys.argv[1:]:
			open(self.logfile,'a').write(msg + '\n')

	def debug(self,msg):
		if '--debug' in sys.argv[1:]:
			print('DEBUG: %s'%str(msg))
