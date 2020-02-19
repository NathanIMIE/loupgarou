from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app)

sio.run(app)

@app.route('/')
def hello_world():
    return 'Hello, Worlddd!'

@sio.on("messageSend")
def messageSend(data):
    print(data)