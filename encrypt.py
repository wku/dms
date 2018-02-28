
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

#
# Generate pare of RSA keys
# return ( private , public )
#
def generate_RSA_key(x=4096):
	private_key = RSA.generate(x)
	public_key  = private_key.publickey()
	return (private_key,public_key)

#
# export keys
# return ( private , public ) # both bytes
# in case of error return None , None
#
def export_keys(private_key,public_key):
	try:
		return ( private_key.exportKey('PEM') , public_key.exportKey('PEM') )
	except Exception as e:
		return None , None

#
# import keys
# return ( private , public ) # both RSA.keyobj
# in case of error raise Exception
#
def import_keys(private_filename,public_filename):
	private = RSA.importKey(open(private_filename).read())
	public  = RSA.importKey(open(public_filename).read())
	return private , public

#
# decrypt message using private_key
#
def decrypt_data(private_key,message):
	cipher = PKCS1_OAEP.new(private_key)
	res = cipher.decrypt(message)
	return res

#
# encrypt message_in_bytes using public_key
#
def encrypt_data(public_key,message_in_bytes):
	cipher = PKCS1_OAEP.new(public_key)
	ciphertext = cipher.encrypt(message_in_bytes)
	return ciphertext

#
# return signature of data
#
def data_to_signature(private_key,data):
	return private_key.sign(data,'')

#
# decrypt signature and return data
#
def verify_signature(public_key,signature,expected_msg):	 	
	return public_key.verify(expected_msg, signature)


