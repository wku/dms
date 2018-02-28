#!/usr/bin/env python3.5
import sys
from server import Server

HELP_MSG = '''
                                +-----------+                                 .
                                |  D  M  S  |
                                +-----------+

                     Decentralized Messaging System
    $ python3.5 main.py [-h|--help]

    Flags:
      --no-stdout                 - No logs to stdout
      --no-log                    - No logs to log file
      -h | --help                 - See this message again

    src: https://bitbicket.org/riniyar8/dmz.git
'''

def main():
	sv = Server(mcfg)
	sv.run()

if __name__ == '__main__':
	if ('-h' in sys.argv[1:]) or ('--help' in sys.argv[1:]):
		print(HELP_MSG)
	else:
		main()