#!/usr/bin/env python3.5
import sys
import json

from server import Server
import encrypt
import conf

HELP_MSG = '''
                                +-----------+                                 .
                                |  D  M  S  |
                                +-----------+

                     Decentralized Messaging System
    $ python3.5 main.py <Command> [ <Flag> ]
    
    Command:
      --server
          Запсутить сервер

      --gen-keypair
          Сгенерировать пару ключей

      --registrate
          Регистрирует пользователя. Первоначально надо сгенерировать ключи.

      --upd-blckchn=<host>:<port>
          Обновить базу данных (блокчейн) от конкретного узла. При этом 
          необходимо использовать -k для указания публичного ключа узла -l для
          указания логина узла

    Flags:
      -h | --help
          Увидеть это сообщение еще раз

      -k <key filename>
          Использовать ключ из конкретного файла. Цель использования явно 
          зависит от <Command>

      -l <login>
          Использовать конкретный логин. Цель использования явно зависит 
          от <Command>

      --no-stdout
          Не выводить лог в stdout

      --no-log
          Не записывать лог в logfile

      --client
          Запустить дополнительно клиентскую часть
      
      --debug
          Отладочная печать

      --extra-output
          Выводить больше данных

    src: https://bitbicket.org/riniyar8/dms.git
'''

def generate_pair():
	priv,pub = encrypt.generate_RSA_key()
	priv,pub = encrypt.export_keys(priv,pub)
	open(conf.key_dir + json.load(open(conf.conf_dir + conf.conf_main))['private_key'],'wb').write(priv)
	open(conf.key_dir + json.load(open(conf.conf_dir + conf.conf_main))['public_key'],'wb').write(pub)

def main():
	sv = Server()
	sv.run()

if __name__ == '__main__':
	if ('-h' in sys.argv[1:]) or ('--help' in sys.argv[1:]):
		print(HELP_MSG)
	elif '--gen-keypair' in sys.argv[1:]:
		generate_pair()
	elif '--server' in sys.argv[1:]:
		main()
	elif '--registrate' in sys.argv[1:]:
		Server().registrate(input('new username: '))
	elif len(list(filter(lambda x:x.startswith('--upd-blckchn='),sys.argv[1:])))>0:
		Server().upd_blockchain(list(filter(lambda x:x.startswith('--upd-blckchn='),sys.argv[1:]))[0][len('--upd-blckchn='):].split(':'))
	else:
		print('ERROR: expected command. Try -h for more info')