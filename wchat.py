from socket import *
import threading
import cv2
import sys
import struct
import pickle
import time
import zlib
import numpy as np


class Word_Server(threading.Thread):
    def __init__(self, port, version) :
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = ('', port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)

    def run(self):
        print("WORD server starts...")
        self.sock.bind(self.ADDR)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        # print("remote WORD client success connected...")
        while 1:
            try:
                buf = conn.recv(1024)
                if len(buf):
                    print("Client: ", buf)
                data = input("Sever: ")
                conn.sendall(data)
            except:
                print("Dialogue Over")
                conn.close()
                sys.exit(0)


class Word_Client(threading.Thread):
    def __init__(self ,ip, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = (ip, port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        print("WORD client starts...")

    def run(self):
        while True:
            try:
                self.sock.connect(self.ADDR)
                break
            except:
                time.sleep(3)
                continue

        while 1:
            try:
                data = input("Client: ")
                self.sock.send(data)
                buf = self.sock.recv(1024)
                if len(buf):
                    print("Sever: ", buf)
            except:
                print("Dialogue Over")
                self.sock.close()
                sys.exit(0)
