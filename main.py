import sys
import time
import argparse
from vchat import Video_Server, Video_Client
from achat import Audio_Server, Audio_Client
from wchat import Word_Server, Word_Client

parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, default='10.190.71.238')
parser.add_argument('--port', type=int, default=10087)
parser.add_argument('--noself', type=bool, default=False)
parser.add_argument('--level', type=int, default=4)
parser.add_argument('-v', '--version', type=int, default=4)

args = parser.parse_args()

IP = args.host
PORT = args.port
VERSION = args.version
SHOWME = not args.noself
LEVEL = args.level

if __name__ == '__main__':
    vclient = Video_Client(IP, PORT, SHOWME, LEVEL, VERSION)
    vserver = Video_Server(PORT, VERSION)
    aclient = Audio_Client(IP, PORT+1, VERSION)
    aserver = Audio_Server(PORT+1, VERSION)
    wclient = Word_Client(IP, PORT + 2, VERSION)
    wserver = Word_Server(PORT + 2, VERSION)
    # vclient.start()
    # vserver.start()
    # aclient.start()
    # aserver.start()
    wclient.start()
    wserver.start()
    while True:
        time.sleep(1)
        # if not vserver.isAlive() or not vclient.isAlive():
        #     print("Video connection lost...")
        #     sys.exit(0)
        # if not aserver.isAlive() or not aclient.isAlive():
        #     print("Audio connection lost...")
        #     sys.exit(0)
        if not wserver.isAlive() or not wclient.isAlive():
            print("Word connection lost...")
            sys.exit(0)