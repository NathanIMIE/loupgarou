from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app)

sio.run(app)

class Room:
    def __init__(self):
        self.players = []
    
    def GetPlayerById(self, id):
        for player in self.players:
            if(player.sid == id):
                return player
        return null

class Player:
    def __init__(self, sid):
        self.sid = sid
        self.pseudo = ''
        self.ready = 0


room = Room()

@app.route('/')
def hello_world():
    return 'Hello, Worlddd!'

@sio.on("chooseName")
def chooseName(data):
    player = room.GetPlayerById(request.sid)
    print(player.pseudo)
    player.pseudo = data['pseudo']
    print(player.pseudo)

@sio.on('connect')
def connect():
    room.players.append(Player(request.sid))
    listePseudo = []
    for player in room.players:
        listePseudo.append(player.pseudo)
    print(listePseudo)
    print(room.players)
    emit('listeJoueurs',listePseudo)

@sio.on('disconnect')
def disconnect():
    player = room.GetPlayerById(request.sid)
    room.players.remove(player)