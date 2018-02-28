##################################################
###              GENERAL SETTINGS              ###
##################################################
# port (int)
port 					=	8080
# configuration dir (str)
conf_dir				=	'config/'
# main config with info about user account in JSON formate (str)
conf_main				=	'main.json'
# keeps pares <client_login> : <public_key_filename> (str)
conf_clients			=	'clients.json'
# keeps pares <server_login> : [ <host> , <port> ] (str)
conf_peers				=	'peers.json'
# directory where will be stored all blocks for blockchain (str)
blockchain_dir			=	'blocks/'
# directory where should be keys (str)
key_dir					=	'keys/'
# log file name (str)
log_filename			=	'log/log.txt'
# in case of error ; the best is somewhere in (0.1,1.0) (float)
delay					=	0.5

##################################################
###               EXTRA SETTINGS               ###
##################################################
# timeout in seocnds between cleaning history for old objids (float)
History_clean_timeout	=	2.0
# how long in seconds we should keep objids in history
History_duration		=	24*3600