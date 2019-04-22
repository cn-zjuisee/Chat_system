from socket import *
import threading
import sys
from turling import auto_reply
import datetime


def now_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class Word_Server(threading.Thread):
    def __init__(self, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = ('', port)
        if version == 4:
            self.sock = socket()
        else:
            self.sock = socket(AF_INET6)

    def run(self):
        print("WORD server starts...")
        self.sock.bind(self.ADDR)
        self.sock.listen(1)
        conn, addr = self.sock.accept()

        while True:

            buf = conn.recv(1024).decode('UTF-8')
            print(now_time(), "Client: ", buf)
            data = input("Sever: ")
            if data == 'exit':
                print("Dialogue Over")
                conn.close()
                sys.exit(0)
            if data == 'auto':
                data = auto_reply(buf)
            conn.send(data.encode('utf-8'))


class Word_Client(threading.Thread):
    def __init__(self, ip, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = (ip, port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        print("WORD client starts...")

    def run(self):

        self.sock.connect(self.ADDR)
        print("WORD client connected...")

        buf = 'Hello!'
        while True:
            data = input("Client: ")
            if data == 'exit':
                print("Dialogue Over")
                self.sock.close()
                sys.exit(0)
            if data == 'auto':
                data = auto_reply(buf)
            self.sock.send(data.encode('UTF-8'))

            buf = self.sock.recv(1024).decode('UTF-8')
            print(now_time(), "Sever: ", buf)