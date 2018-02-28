#!/usr/bin/env python3.5
import conf
import encrypt

#
# class for one block
#
class Block:
	def __init__(self):
		pass

	#
	# FIXME 
	# should be smth how to fill this block with data
	#

	#
	# return hash for this block
	#
	def get_hash(self):
		pass

#
# class for whole blockchain
#
class Blockchain:
	def __init__(self):
		self.dir = conf.blockchain_dir

	#
	# check each block in chain
	#
	def __check_chain(self):
		pass

	#
	# add's block at the end of chain
	#
	def add_block(self,block):
		pass

	#
	# return 'client' , 'server' or None
	#
	def peer_status(self,peer):
		pass

	#
	# return user's public key
	#
	def get_key(self,peer):
		pass