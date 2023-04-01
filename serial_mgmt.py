import os
from selectors import DefaultSelector as Selector, EVENT_READ
import tty
import pty
from contextlib import ExitStack
import threading
import time

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
