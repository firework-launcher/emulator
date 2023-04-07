import os
from selectors import DefaultSelector as Selector, EVENT_READ
import tty
import pty
from contextlib import ExitStack
import threading
import time
import socket

class SerialMGMT:
    def __init__(self):
        self.port = None
    def create_port_(self):
        master_fd, slave_fd = pty.openpty()
        tty.setraw(master_fd)
        os.set_blocking(master_fd, False)
        slave_name = os.ttyname(slave_fd)
        master_file = open(master_fd, 'r+b', buffering=0)

        self.port = slave_name
        self.master_file = master_file

        with Selector() as selector, ExitStack() as stack:
            stack.enter_context(master_file)

            while True:
                for key, events in selector.select():
                    continue

    def create_port(self):
        threading.Thread(target=self.create_port_).start()
        while self.port == None:
            pass
        return self.port
    def check_read(self):
        return self.master_file.read()
    def write_data(self, data):
        self.master_file.write(data) 

class IPMGMT():
    def __init__(self):
        self.port = None
        self.newest_read = None
        self.data_to_write = None
    def create_port_(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        s.bind(('0.0.0.0', 2364))
        s.listen()
        while True:
            self.port, addr = s.accept()
            while True:
                try:
                    self.newest_read = self.port.recv(1024)
                except:
                    self.port.close()
                    self.port = None
                    break
                else:
                    while self.data_to_write == None:
                        time.sleep(0.01)
                    self.port.send(self.data_to_write)
                    self.data_to_write = None
    def create_port(self):
        threading.Thread(target=self.create_port_).start()
    def check_read(self):
        newest_read = self.newest_read
        self.newest_read = None
        return newest_read
    def write_data(self, data):
        self.data_to_write = data
