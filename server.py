#!/usr/bin/env python3.6
import sys
import socket
import threading as th
import time

from parent import parent_class
import conf		

class Server(parent_class):
	def __init__(self):
		super(Server, self).__init__()
		self.threads = []
		self.open_port()

		#
		# runtime tables:
		#	user_or_server : socket
		#	user_or_server : key
		# tables from database:
		#	server_name : [ ip , port ]
		#   

	def __del__(self):
		try:
			self.socket.close()
		except:
			pass

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


	#
	# low-level send msg
	#
	def __send(self,sock,msg):
		if type(msg) == str:
			msg = msg.decode()
		query = asc.b2a_base64(str(len(msg)).encode())[:-1] + b' ' + msg
		self.debug('send: %s'%query)
		sock.send(query)

	#
	# low-level recv msg
	#
	def __recv(self,sock):
		query = b''
		q = b''
		while q != b' ':
			q = sock.recv(1)
			query += q
		msg = sock.recv(int(asc.a2b_base64(query[:-1]).decode()))
		self.debug('recv: %s'%msg)
		return msg

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
	# (и лишь зря занимают записи в таблицах процессов в ядре)
	#
	def run(self):
		delay = conf.delay
		try:
			self.log('Starting working')
			while True: # MAINLOOP
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


