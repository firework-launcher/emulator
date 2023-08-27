import os
from selectors import DefaultSelector as Selector, EVENT_READ
import tty
import pty
from contextlib import ExitStack
import threading
import time
import json
import socket

mappings = [4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13]

def handle_serialip_msgs(msg, pins):
    if not msg == None:
        msg = msg.decode('utf-8')
        read_full = msg.split('\r\n')
        for read in read_full:
            if read.startswith('/digital'):
                pin = str(int(msg.split('/')[2])-1)
                state = int(msg.split('/')[3].replace('\r\n', ''))
                pins.pin_data[int(pin)-1]['state'] = state
                if state == 0:
                    pins.pin_data[int(pin)-1]['launched'] = True
                return b'{"message": "Pin D' + pin.encode() + b' set to ' + str(state).encode() + b'", "id": "2", "name": "serial", "hardware": "emulator", "connected": true}'
            else:
                return b'{"message": "Failed to set pin", "id": "2", "name": "serial", "hardware": "emulator", "connected": true}'

def get_inputs(pin_data):
    data = ''
    for pin in pin_data:
        data += '1' if pin['on'] else '0'
    
    data1 = list('00000000')
    data2 = list('00000000')
    
    x = 0
    for mapping in mappings:
        mapping -= 1
        if mapping < 8:
            data1[mapping] = data[x]
        else:
            mapping -= 8
            data2[mapping] = data[x]
        x += 1

    data1 = int(''.join(data1), 2)
    data2 = int(''.join(data2), 2)
    return [data1, data2]

class SerialMGMT:
    def __init__(self, pins):
        self.port = None
        self.pins = pins
        self.top_msg = 'Serial Port: {}'.format(self.port)
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
        self.top_msg = 'Serial Port: {}'.format(self.port)
        return self.port
    def check_read(self):
        self.write_data(handle_serialip_msgs(self.master_file.read(), self.pins))
    def write_data(self, data):
        if not data == None:
            self.master_file.write(data)

class IPMGMT():
    def __init__(self, pins):
        self.port = None
        self.pins = pins
        self.newest_read = None
        self.data_to_write = None
        self.top_msg = 'IP: {}'.format(socket.gethostbyname(socket.gethostname()))
    def create_port_(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        s.bind(('0.0.0.0', 2364))
        s.listen()
        while True:
            self.port, addr = s.accept()
            while True:
                try:
                    self.newest_read = self.port.recv(1048576)
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
        self.write_data(handle_serialip_msgs(newest_read, self.pins))
    def write_data(self, data):
        self.data_to_write = data

class ESPMGMT():
    def __init__(self, pins):
        self.port = None
        self.send_port = None
        self.newest_read = None
        self.pins = pins
        self.top_msg = 'IP: {}'.format(socket.gethostbyname(socket.gethostname()))
        self.send_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.recv_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

    def send_thread(self):
        while True:
            self.send_port, addr = self.send_obj.accept()
            while True:
                inputData = get_inputs(self.pins.pin_data)
                self.send_port.send(json.dumps({'inputData': inputData}).encode())
                time.sleep(1)

    def launch_firework(self, payload):
        payload[0] -= 1
        print('Launch firework called')
        self.pins.pin_data[payload[0]]['state'] = 1
        self.pins.pin_data[payload[0]]['launched'] = payload[1]
        time.sleep(0.5)
        self.pins.pin_data[payload[0]]['state'] = 0
    
    def run_step(self, payload):
        x = 0
        for firework in payload[0]:
            firework -= 1
            self.pins.pin_data[firework]['state'] = 1
            self.pins.pin_data[firework]['launched'] = payload[1][x]
            x += 1
        time.sleep(0.5)
        for firework in payload[0]:
            firework -= 1
            self.pins.pin_data[firework]['state'] = 0

    def create_port_(self):
        self.send_obj.bind(('0.0.0.0', 4444))
        self.recv_obj.bind(('0.0.0.0', 3333))
        self.send_obj.listen()
        self.recv_obj.listen()
        threading.Thread(target=self.send_thread).start()
        while True:
            self.port, addr = self.recv_obj.accept()
            while True:
                try:
                    self.newest_read = self.port.recv(4096)
                except Exception as e:
                    print('Read failed: {}'.format(str(e)))
                    self.port.close()
                    self.port = None
                    break
    def create_port(self):
        threading.Thread(target=self.create_port_).start()
    def check_read(self):
        newest_read = self.newest_read
        self.newest_read = None
        if not newest_read == None:
            newest_read = newest_read.decode('utf-8')
            for read in newest_read.split('\r\n'):
                if not read == '':
                    read = json.loads(read)
                    if read['code'] == 1:
                        threading.Thread(target=self.launch_firework, args=[read['payload']]).start()
                    elif read['code'] == 2:
                        self.pins.armed = True
                    elif read['code'] == 3:
                        self.pins.armed = False
                    elif read['code'] == 4:
                        threading.Thread(target=self.run_step, args=[read['payload']]).start()
