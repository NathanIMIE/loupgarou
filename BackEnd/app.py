from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import logging
from flask_cors import CORS

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
sio = SocketIO(app, cors_allowed_origins="*")

class Room:
    def __init__(self):
        self.players = []
        self.started = 0
    
    def GetPlayerById(self, id):
        for player in self.players:
            if(player.sid == id):
                return player
        return null
    
    def GameCanStart(self):
        if(len(self.players) < 2 or len(self.players) > 10):
            return 0
        for player in self.players:
            if(player.ready == 0):
                return 0
        return 1

class Player:
    def __init__(self, sid):
        self.sid = sid
        self.pseudo = ''
        self.ready = 0
        self.role = ''
        self.amour = 0

room = Room()

def GameStart():
    if(room.GameCanStart() == 1):
        sio.emit('goGame', 1)
    else:
        sio.emit('goGame', 0)

def UpdateListeJoueurs():
    listePseudo = []
    for player in room.players:
        listePseudo.append(player.pseudo)
    sio.emit('listeJoueurs',[listePseudo, 0])

@sio.on('startGame')
def startGame():
    room.started = 1
    sio.emit('zeParti')

@sio.on('chooseName')
def chooseName(data):
    player = room.GetPlayerById(request.sid)
    player.pseudo = data['pseudo']
    player.ready = 1

    UpdateListeJoueurs()
    GameStart()

@sio.on('connect')
def connect():
    if(room.started == 1):
        emit('gameStarted')

    room.players.append(Player(request.sid))
    listePseudo = []
    for player in room.players:
        listePseudo.append(player.pseudo)
    emit('listeJoueurs', [listePseudo, 1])
    sio.emit('listeJoueurs', [listePseudo, 0])

    GameStart()

@sio.on('disconnect')
def disconnect():
    player = room.GetPlayerById(request.sid)
    room.players.remove(player)

    UpdateListeJoueurs()