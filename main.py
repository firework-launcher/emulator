import serial_mgmt
from flask import Flask, render_template
import flask_socketio
import argparse
import threading

serial = serial_mgmt.SerialMGMT()

parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, help='Host emulator website on specific IP address', required=False)
parser.add_argument('--port', type=int, help='Host emulator website on specific port', required=False)

args = parser.parse_args()

serial.create_port()

app = Flask(__name__)
socketio = flask_socketio.SocketIO(app)

def handle_serial():
    while True:
        read = serial.read_data().decode('utf-8')
        if read.startswith('/digital'):
            pin = str(int(read.split('/')[2])-1)
            state = int(read.split('/')[3].replace('\r\n', ''))
            socketio.emit('pin_update', {'pin': pin, 'state': state})
            serial.write_data(b'0')
        else:
            serial.write_data(b'1')

@app.route('/')
def home():
    return render_template('home.html', port=serial.port)

if __name__ == '__main__':
    threading.Thread(target=handle_serial).start()
    port = args.port
    if port == None:
        port = 3472
    host = args.host
    if host == None:
        host='127.0.0.1'
    print('Hosting website on http://{}:{}'.format(host, port))
    socketio.run(app, host=host, port=port)
