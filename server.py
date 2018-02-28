#!/usr/bin/env python3.6
import sys
import socket
import threading as th
import time
import json
import random

import encrypt
from parent import parent_class
from history import History
from blockchain import Blockchain
import conf		

class Server(parent_class):
	def __init__(self):
		super(Server, self).__init__()
		self.threads = []
		self.open_port()

		#
		# user keys
		#
		mcfg = json.load(open(conf.conf_dir + conf.conf_main))
		self.my_name = mcfg['username']
		self.private,self.public = encrypt.import_keys(conf.key_dir+mcfg['private_key'],conf.key_dir+mcfg['public_key'])


		#
		# runtime tables:
		#	socket : client              # current active connections
		# tables from database:
		#	client : key                 # database of public keys
		#	server_name : [ ip , port ]  # database of other peers
		#
		self.table_socket  = {}
		self.blockchain = Blockchain()

		self.network_state = 0
		self.history = History()

	def __del__(self):
		try:
			self.socket.close()
		except:
			pass


	def generate_body_id(self):
		def random_item(az):
			i = int(random.random()*(len(az)-1))
			return az[i]
		CHARS =  ''
		for i in ( range(65,91) + range(48,58) + range(97,123) ):
			CHARS += chr(i)
		st = ''
		for i in range(10):
			st += random_item(CHARS)
		return st

	#
	# create listening socket
	#
	def open_port(self):
		port = conf.port
		host = '' # here we can make some restrictions on connections # but we will not
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((host, port))
		self.socket.listen(5)
		self.socket.settimeout(30*3600)


	def check_threads(self):
		if len(self.threads) <= 0:
			return
		i = 0
		while i < len(self.threads):
			if not self.threads[i].is_alive():
				self.threads.pop(i).join()
			else:
				i += 1

	#######################################
	##    FIRST LEVEL OF DMS PROTOCOL    ##
	#######################################
	#
	# low-level send msg
	#
	def __send(self,sock,msg,pub_key):
		max_size = 500
		if type(msg) == str:
			msg = msg.decode()
		if len(msg) <= max_size:
			msg = [encrypt.encrypt_data(pub_key,msg)]
		else:
			n = int(len(msg) / max_size) + 1
			_msg = []
			for i in range(n+1):
				st = ''
				for k in range(max_size):
					if len(msg) > 0:
						st += msg.pop(0)
					else:
						break
				if len(st)>0:
					_msg.append(encrypt.encrypt_data(pub_key,st))
			msg = msg
		query = ''
		for i in range(len(msg)):
			query += asc.b2a_base64(str(len(msg[i])).encode())[:-1] 
			if i == len(msg):
				query += b','
			else:
				query += b'.'
			query += msg[i]
		self.debug('send: %s'%query)
		sock.send(query)

	#
	# low-level recv msg 
	#
	def __recv(self,sock,priv_key):
		query = b''
		q = b''
		boo = True
		while boo:
			while q not in [b'.',b',']:
				q = sock.recv(1)
				query += q
			boo = q == b','
			msg = sock.recv(int(asc.a2b_base64(encrypt.decrypt_data(priv_key,query[:-1])).decode()))
		self.debug('recv: %s'%msg)
		return msg

	#######################################
	##   SECOND LEVEL OF DMS PROTOCOL    ##
	#######################################

	#
	# send msg in plaintext to peer
	#
	def send_2lv(self,peer,obj):
		pass # FIXME

	#
	# recv msg from peer & decrypt it 
	#
	def recv_2lv(self):
		pass # FIXME


	######################################
	##   THIRD LEVEL OF DMS PROTOCOL    ##
	######################################

	def crypt_and_send(body_obj):
		peer = body_obj['to']
		if self.blockchain.peer_status(peer) != None: 
			pub = self.blockchain.get_key(peer)
			pass # FIXME

			return True
		else:
			return False
	
	#
	# registrate new user
	#
	def registrate(self,username):
		pass # FIXME

	# 
	# gets 2lv package and decide to reg or auth
	# 
	def auth_ot_reg(self,data):
		pass # FIXME
		
	#
	# send message to user
	#
	def send_user_message(self,username,message):
		pass # FIXME

	#####################################
	##              OTHERS             ##
	#####################################

	#
	# handle single connection
	#
	def connection_handle(self,conn,addr):
		self.log("%s _ %s"%(conn,addr))
		SHOULD_BE_OPENED = True
		while SHOULD_BE_OPENED:
			send_box = []
			try:
				package = self.recv_2lv()
				_from	= package['from']
				_to		= package['to']
				_data	= package['data']
				_flow	= package['flow-controll']
				
				AUTH_REG = _flow % (2**0) > 0 # auth or registrate
				SHOULD_BE_OPENED = _flow % (2**1) == 0 # close connection
				if (_flow % (2**2+2**3)) >> 2 != self.network_state:
					pass # should do s0mething

				if AUTH_REG:
					AUTH_REG = not self.auth_ot_reg(_data)
				if AUTH_REG:
					for body_object in _data:
						body_id = body_object['body-id']
						data = body_object['data']
						to = body_object['to']
						if not self.history.exists(body_id):
							self.history.add(body_id)
							if to == self.my_name:
								self.third_level_handler(data)
							else:
								obj = {
									'from':self.my_name,
									'to':to,
									'data':data
								}
								send_box.append(obj)
			except Exception as e:
				self.log('ERROR: handler <%s> %s'%(addr,e))
			finally:
				flow = 0x0C & _flow
				for body_obj in send_box:
					body_obj['flow'] = _flow
					self.crypt_and_send(body_obj)
		conn.close()




	#
	# main loop
	# create lots of threads and listen to socket
	#
	# Магия (идиотизм) питона в том, что есть GIL
	# Из-за которого все потоки превращаются в корутины
	# (и лишь зря занимают записи в таблицах процессов в ядре ОС)
	#
	def run(self):
		self.mainloop = True
		if '--client' in sys.argv[1:]:
			self.fork_client()
		delay = conf.delay
		try:
			self.log('Starting working')
			while self.mainloop: # MAINLOOP
				try:
					
					conn , addr = self.socket.accept()
					#
					# check for len of self.threads and kill one in case of need
					#
					_t = th.Thread( target = self.connection_handle, args = [conn,addr] )
					_t.start()
					self.threads.append(_t)
					self.check_threads()

				except socket.timeout as e: # time to reopen port
					try:
						self.socket.close()
					except Exception as e:
						self.log('Err while opennig port')
						time.sleep(delay*5)
					finally:
						self.open_port()
				except Exception as e:
					self.log('mainloop: %s'%e)
				finally:
					time.sleep(delay)
		except KeyboardInterrupt as e:
			self.log('Finish working')

	#####################################################
	##                 USERS INTERFACE                 ##
	#####################################################

	#
	# here will be forked thread for working with user
	#
	def fork_client(self):
		def client(self):
			CMDS = '''ENTER COMMAND:\n0 - exit\n1 - send msg\n2 - registrate new user\n'''
			while True:
				try:
					cmd = int(input(CMDS))
					if cmd == 0:
						self.mainloop = False
						return
					elif cmd == 1:
						username = input('peer-name: ')
						msg = input('message: ')
						self.send_user_message(username,msg)
					elif cmd == 2:
						username = input('new username: ')
						self.registrate(username)
					else:
						raise RuntimeError('unknown command %s'%cmd)
				except:
					print('ERROR client: %s'%e)
		_t = th.Thread(target=client,args=[self])
		_t.start()
		self.threads.append(_t)