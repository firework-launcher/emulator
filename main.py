import serial_mgmt
from flask import Flask, render_template
import flask_socketio
import threading

serial = serial_mgmt.SerialMGMT()

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
    print('Hosting website on http://localhost:3472')
    threading.Thread(target=handle_serial).start()
    socketio.run(app, port=3472)
