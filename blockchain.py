#!/usr/bin/env python3.5
import json
import conf
import encrypt

#
# class for one block
#
class Block:
	#
	# n 		- block's number
	# data 		- blocks data
	# prev_hash - hash of previos block
	#
	def __init__(self,n=None,data=None,prev_hash=None,hash_type='md5'):
		self.__n = n
		if n == None:
			return	# not initialized
		self.__prev_hash = prev_hash
		self.__data = data
		self.__hash_type = hash_type
		self.__signature = None

	#
	# return hash for this block
	#
	def get_hash(self):
		if self.__n == None:
			raise RuntimeError('block should be initialized')
		obj = {
			'n':self.n,
			'prev-hash':self.__prev_hash,
			'data':self.__data,
			'hash-type':self.__hash_type,
		}
		if self.__signature != None:
			obj['sign'] = self.__signature
			obj['author'] = self.__author
		return eval('%s(%s)'%(self.__hash_type,json.dumps(obj).encode()),{
			'md5':encrypt.md5,
			'sha256':encrypt.sha256,
			'sha512':encrypt.sha512
		})

	#
	# return block's data
	#
	def get_data(self):
		if self.__n == None:
			raise RuntimeError('block should be initialized')
		return self.__data 

	def get_number(self):
		if self.__n == None:
			raise RuntimeError('block should be initialized')
		return self.__n

	def get_author(self):
		if self.__n == None:
			raise RuntimeError('block should be initialized')
		if self.__signature == None:
			raise RuntimeError('block should be signed')
		return self.__author

	#
	# return JSON-format str
	#
	def _export(self):
		if self.__n == None:
			raise RuntimeError('block should be initialized')
		obj = {
			'n':self.__n,
			'prev-hash':self.__prev_hash,
			'data':self.__data,
			'hash-type':self.__hash_type,
		}
		if self.__signature != None:
			obj['sign'] = self.__signature
			obj['author'] = self.__author
		return json.dumps(obj)

	#
	# takes JSON-format str
	# and reinitialize object
	#
	def _import(self,st):
		obj = json.loads(st)
		self.__init__(obj['n'],obj['data'],obj['prev-hash'],obj['hash-type'])

	#
	# signature this block
	#
	def sign(self,author,priv_key):
		if self.__n == None:
			raise RuntimeError('block should be initialized')
		self.__signature = encrypt.data_to_signature(priv_key,self.get_hash())
		self.__author = author

	#
	# check signature of this block
	# return True in case of successful verification
	# or return False
	#
	def check_signature(self,public_key,prev_hash):
		if self.__n == None:
			raise RuntimeError('block should be initialized')
		if self.__signature == None:
			raise RuntimeError('block should be signed')
		_hash = self.get_hash()
		return _hash == encrypt.verify_signature(public_key,self.__signature,_hash) and prev_hash == self.__prev_hash


#
# class for whole blockchain
#
class Blockchain:
	def __init__(self):
		self.dir = conf.blockchain_dir
		self.blocks = {}
		self.n = 0
		self.user_keys = {}		# username  :  pubkey (RSA.keyobj)
		self.servers = {}		# username  :  [ host , port ]
		self.current_leader = None
		self.current_leaders_key = None
		self.blocks[0]=Block(n=0,data='',prev_hash='')
		boo = True
		while boo:
			try:
				block = Block()
				block._import(open('%s.blck'%(self.n)).read())
				self.blocks[self.n] = block
				self.n += 1
			except:
				boo = False
		self.__check_chain()


	#
	# check each block in chain
	# return True if all right
	# or number of first wrong block
	#
	def __check_chain(self):
		for i in sorted(list(self.blocks.keys())):
			try:
				data = self.blocks[i].get_data()
				if data['type'] == 'user':
					username = data['name']
					usertype = data['usertype']
					if usertype == 'server':
						servers_addr = data['address'] # [ host , port ]
					else:
						servers_addr = None
					userkey = encrypt.import_public_key_from_str(data['key'])
					if current_leader == None:
						self.current_leader = username
						self.current_leaders_key = userkey
					
					if i == 0:
						prev_hash = ''
					else:
						prev_hash = self.blocks[i-1].get_hash()
					if not self.blocks[i].check_signature(self.current_leader,self.current_leaders_key,prev_hash):
						return i
					
					self.user_keys[username] = userkey
					if usertype == 'server':
						self.servers[username] = servers_addr
				else:
					new_leader = data['new_leader']
					if new_leader not in self.user_keys:
						return i
					
					if i == 0:
						prev_hash = ''
					else:
						prev_hash = self.blocks[i-1].get_hash()
					if not self.blocks[i].check_signature(self.current_leader,self.current_leaders_key,prev_hash):
						return i

					self.current_leader = new_leader
					self.current_leaders_key = self.user_keys[new_leader]
			except:
				return i
		return True

	#
	# add's new block at the end of chain
	# return True in case of success
	# return False if block is not verified
	# return None if we don't have earlier block to check this one
	#
	def add_block(self,block):
		try:
			author = block.get_author()
			if author != None:
				if (author != self.current_leader) and (block.get_data()['type'] == 'user'):
					return False
				n = block.get_number()
				if n in self.blocks:
					return False
				if (n-1) not in self.blocks:
					return None 
				if n != 0:
					prev_hash = self.blocks[n-1].get_hash()
				else:
					prev_hash = ''
				if not block.check_signature(author,self.user_keys[author],prev_hash):
					return False
				self.blocks[n] = block
			else:
				return False
		except:
			return False

	#
	# save changes on HDD
	# or SSD :D
	#
	def save(self):
		for i in sorted(list(self.blocks.keys())):
			open(self.dir + '%s.blck'%(i),'w').write(self.blocks[i]._export())

	#
	# return 'client' , 'server' or None
	#
	def peer_status(self,peer):
		if peer in self.servers:
			return 'server'
		elif peer in self.user_keys:
			return 'client'
		else:
			return None

	#
	# return user's public key
	# or raise Error
	#
	def get_key(self,peer):
		return self.user_keys[peer]

	#
	# return server's addr or None
	#
	def get_server_addr(self,peer):
		if peer in self.servers:
			return self.servers[peer]
		else:
			return None