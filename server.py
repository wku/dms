#!/usr/bin/env python3.6
import sys
import socket
import threading as th
import time
import json

import encrypt
from parent import parent_class
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
		try:
			self.table_clients = json.loads(conf.conf_dir + conf.conf_clients)
		except Exception as e:
			self.log('WARNING: no clients table (%s) : %s'%(conf.conf_dir + conf.conf_clients,e))
			self.table_clients = {}
		try:
			self.servers = json.loads(conf.conf_dir + conf.conf_peers)
		except Exception as e:
			self.log('WARNING: no peers table (%s) : %s'%(conf.conf_dir + conf.conf_clients,e))
			self.servers = {}

		#
		# list of msgs that cannot be send at the moment as there are not peer public key 
		# username : [ msg0 , msg1 , ... ]
		#
		self.promise = {}

	def __del__(self):
		try:
			self.socket.close()
		except:
			pass

	def save_cfg(self):
		try:
			open(conf.conf_dir + conf.conf_clients,'w').write(json.dumps(self.table_clients))
		except Exception as e:
			self.log('WARNING: couldn\'t save clients table to %s : %s'%(conf.conf_dir + conf.conf_clients,e))
		try:
			open(conf.conf_dir + conf.conf_peers,'w').write(json.dumps(self.servers))
		except Exception as e:
			self.log('WARNING: couldn\'t save peers table to %s : %s'%(conf.conf_dir + conf.conf_peers,e))

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
	def send_2lv(self,peer,msg):
		pass # FIXME

	#
	# recv msg from peer & decrypt it 
	#
	def recv_2lv(self,peer,msg):
		pass # FIXME


	######################################
	##   THIRD LEVEL OF DMS PROTOCOL    ##
	######################################

	#
	# should send request for user's public key
	# 
	def request_key(self,username):
		pass # FIXME


	#
	# registrate new user
	#
	def registrate(self,username):
		pass # FIXME
		
	#
	# send message to user
	#
	def send_user_message(self,username,message):
		# FIXME
		if username not in self.table_clients:
			self.make_promise(username,message)
		else:
			pass # FIXME

	#####################################
	##              OTHERS             ##
	#####################################

	def make_promise(self,username,message):
		if username not in self.promise:
			self.promise[username] = [message]
		else:
			self.promise[username].append(message)
		self.request_key(username)
	#
	# handle single connection
	#
	def connection_handle(self,conn,addr):
		self.log("%s _ %s"%(conn,addr))

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