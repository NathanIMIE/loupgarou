from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import logging
from flask_cors import CORS
import random

roles = {
    6 : ["lg","lg","sorc","chass","vill","ange"],
    7 : ["lg","lg","sorc","chass","vill","voy","ange"],
    8 : ["lg","lg","sorc","chass","vill","vill","voy","cupi"],
    9 : ["lg","lg","lg","sorc","chass","vill","vill","voy","cupi"],
    10 : ["lg","lg","lg","sorc","chass","vill","vill","voy","cupi","gard"]
}

libelleRole = {
    "lg": "Loup-Garou",
    "sorc": "Sorcière",
    "chass": "Chasseur",
    "vill": "Villageois",
    "ange": "Ange",
    "cupi": "Cupidon",
    "gard": "Garde",
    "voy": "Voyante",
}

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
sio = SocketIO(app, cors_allowed_origins="*")

class Room:
    def __init__(self):
        self.players = []
        self.started = 0
        self.jour = 0
        self.nuit = 1
        self.tour = 'cupi'
        self.voteLoup = {}
        self.potionRes = 0
        self.potionMort = 0
        self.vote = {}
        self.voteValide = 0

    def GetListeVivant(self):
        players = []
        for player in self.players:
            if(player.dead == 0):
                players.append(player)
        return players
    
    def GetPlayersByRole(self,role):
        players = []
        for player in self.players:
            if(player.role == role):
                players.append(player)
        return players

    def GetPlayerByPseudo(self, pseudo):
        for player in self.players:
            if(player.pseudo == pseudo):
                return player
        return null
    

    def GetPlayerById(self, id):
        for player in self.players:
            if(player.sid == id):
                return player
        return null
    
    def GameCanStart(self):
        if(len(self.players) < 6 and len(self.players) > 10):
            return 0
        for player in self.players:
            if(player.ready == 0):
                return 0
        return 1

    def DefineRole(self):
        role = roles[len(self.players)]
        random.shuffle(role)
        for i in range(0, len(self.players)):
            self.players[i].role = role[i]

    def hasRoleAlive(self, role):
        for player in self.players:
            if(player.role==role and player.dead == 0):
                return 1
        return 0
        
    def resetVoteLoup(self):
        self.voteLoup = {}
        for player in self.players:
            if(player.role == 'lg' and player.dead == 0):
                self.voteLoup[player.sid] = ''

    def resetVote(self):
        self.vote = {}
        for player in self.players:
            if(player.dead == 0):
                self.vote[player.sid] = ''


    def GetMorts(self):
        morts = []
        for player in self.players:
            if(player.dead == 1):
                morts.append(player)
        return mort

    def GetMortLoup(self):
        for player in self.players:
            if(player.deadLoup == 1):
                return player
        return null
    
    def GetAutreAmour(self, playerAmour):
        for player in self.players:
            if(player.amour == 1 and player.sid != playerAmour.sid):
                return player
        
    def GetPlusVote(self):
        votePlayers = {}
        for player in self.players:
            votePlayers[player.nombreVote] = player.pseudo
        return votePlayers

class Player:
    def __init__(self, sid):
        self.sid = sid
        self.pseudo = ''
        self.ready = 0
        self.role = ''
        self.amour = 0
        self.dead = 0
        self.deadNuit = 0
        self.proteger = 0
        self.deadLoup = 0
        self.nombreVote = 0

room = Room()

def GameStart():
    if(room.GameCanStart() == 1):
        sio.emit('goGame', 1)
    else:
        sio.emit('goGame', 0)

def UpdateListeJoueurs():
    listePseudo = []
    for player in room.players:
        if player.dead == 0:
            listePseudo.append(player.pseudo)
    sio.emit('listeJoueurs',[listePseudo, 0])

def AffichageListe():
    listeAffichage = []
    for player in room.players:
        listeAffichage.append([player.pseudo, player.dead, player.amour, libelleRole[player.role]])
    sio.emit("listePersonne", listeAffichage)

def Tour():
    listePseudoEnVie = []
    for player in room.players:
        if player.dead == 0:
            listePseudoEnVie.append(player.pseudo)

    if(room.tour == "cupi"):
        if(room.hasRoleAlive('cupi') == 1 and room.jour == 0):
            sio.emit('nouveauMessage', ['MDJ', "Cupidon se réveille et va réunir deux âmes."])
            sio.emit('CUPI', listePseudoEnVie)
        else:
            room.tour = 'gard'
            Tour()

    if(room.tour == "gard"):
        if(room.hasRoleAlive('gard')):
            sio.emit('nouveauMessage', ["MDJ", "Le garde se réveille et va accorder sa protection à un joueur !"])
            sio.emit('GARDE',listePseudoEnVie)
        else:
            room.tour = 'lg'
            Tour()

    if(room.tour == 'lg'):
        sio.emit('nouveauMessage', ["MDJ", "AHOUU ! Les loups se réveillent et vont choisir une cible à dévorer !"])
        players = room.GetPlayersByRole('lg')
        for player in players:
            listePseudoEnVie.remove(player.pseudo)
        sio.emit('LG', listePseudoEnVie)
        room.resetVoteLoup()
    
    if(room.tour == 'sorc'):
        if(room.hasRoleAlive('sorc')):
            sio.emit('nouveauMessage', ["MDJ", "C'est au tour de la sorcière de se réveiller, elle a le pouvoir de vie et de mort sur chaqu'un d'entre vous !"])
            mortLoupPseudo = room.GetMortLoup().pseudo
            players = room.GetPlayersByRole('sorc')
            for player in players:
                listePseudoEnVie.remove(player.pseudo)
            listePseudoEnVie.remove(mortLoupPseudo)
            sio.emit('SORC', [listePseudoEnVie, mortLoupPseudo, room.potionRes, room.potionMort])
        else:
            room.tour = 'voy'
            Tour()

    if(room.tour == 'voy'):
        if(room.hasRoleAlive('voy')):
            sio.emit('nouveauMessage', ["MDJ", "La voyante va ouvrir les yeux et prendre connaissance du rôle d'un de vous !"])
            players = room.GetPlayersByRole('voy')
            for player in players:
                listePseudoEnVie.remove(player.pseudo)
            sio.emit("VOY", listePseudoEnVie)
        else :
            room.tour = "jour"
            room.jour += 1
            Tour()
    if(room.tour == 'jour'):
        chasseurMort = 0
        sio.emit('nouveauMessage', ["MDJ", "*Baille* Le jour se lève sur le village tout le monde se réveille !"])
        for player in room.players:
            if(player.deadLoup == 1 and player.proteger == 0 or player.deadNuit == 1 and player.deadLoup == 0):
                player.dead = 1
                if(player.role == 'chass'):
                    chasseurMort = 1
                sio.emit('nouveauMessage', ["MDJ", "Triste nouvelle nous avons perdu " + player.pseudo + " qui est mort cette nuit. Il était " + libelleRole[player.role] + " !"])
                if(player.amour == 1):
                    playerAmoureux = room.GetAutreAmour(player)
                    playerAmoureux.dead = 1
                    if(playerAmoureux.role == "chass"):
                        chasseurMort = 1
                    sio.emit('nouveauMessage', ["MDJ", playerAmoureux.pseudo + " était fou amoureux de " + player.pseudo + ", il a décidé de la rejoindre dans la mort, il était " + libelleRole[playerAmoureux.role] + " !"])

        AffichageListe()
        if(chasseurMort == 1):
            listePseudoEnVieChass = []
            for player in room.players:
                if player.dead == 0:
                    listePseudoEnVieChass.append(player.pseudo)

            sio.emit('CHASS', listePseudoEnVieChass)
            sio.emit('nouveauMessage', ["MDJ", "Le chasseur est mort, il va prendre sa revanche avant de s'éteindre !"])
        else:
            sio.emit('JOUR', listePseudoEnVie)
            


@sio.on('RespCUPI')
def RespCUPI(data):
    sio.emit('nouveauMessage', ['MDJ', 'Cupidon a tiré ses flèches ! Il se rendort.'])
    
    firstPlayer = room.GetPlayerByPseudo(data[0])
    secondPlayer = room.GetPlayerByPseudo(data[1])

    firstPlayer.amour = 1
    secondPlayer.amour = 1

    sio.emit('nouveauMessage', ['MDJ', "Cupidon t'a touché avec sa flèche ! Tu es fou amoureux de " + secondPlayer.pseudo + " !"], room=firstPlayer.sid)
    sio.emit('nouveauMessage', ['MDJ', "Cupidon t'a touché avec sa flèche ! Tu es fou amoureux de " + firstPlayer.pseudo + " !"], room=secondPlayer.sid)
    
    sio.emit('amoureux', 1,room=firstPlayer.sid)
    sio.emit('amoureux', 1,room=secondPlayer.sid)

    AffichageListe()
    room.tour = 'gard'
    Tour()

@sio.on('RespGARDE')
def RespGARDE(data):
    sio.emit('nouveauMessage', ['MDJ', 'Le garde a accordé sa protection ! Il se rendort.'])
    
    player = room.GetPlayerByPseudo(data)
    player.proteger = 1

    room.tour = 'lg'
    Tour()

@sio.on('RespLG')
def RespLG(data):
    player = room.GetPlayerById(request.sid)
    
    sio.emit('nouveauMessageLG', ['MDJ', player.pseudo + " a voté pour manger " + data + " !"])
    room.voteLoup[request.sid] = data

    ok = 1
    okButDiff = 1
    vote = ''

    for value in room.voteLoup.values():
        if(value == ''):
            okButDiff = 0
        vote = value

    for value in room.voteLoup.values():
        if(value != vote):
            ok = 0

    if(okButDiff == 1 and ok == 0):
        sio.emit('nouveauMessageLG', ['MDJ', "Les loups doivent être d'accord sur la cible."])

    if(ok == 1):
        sio.emit('nouveauMessage', ['MDJ', "Les loups ont choisis leurs proies, ils retournent se coucher."])
        room.tour = "sorc"
        mort = room.GetPlayerByPseudo(vote)
        mort.deadNuit = 1
        mort.deadLoup = 1
        Tour()

@sio.on('RespSORC')
def RespSORC(data):
    sauve = data[0]
    potionMort = data[1]

    if(sauve == 'oui'):
        joueurSauve = room.GetMortLoup()
        joueurSauve.dead = 0
        room.potionRes = 1

    if(potionMort != ''):
        joueurMort = room.GetPlayerByPseudo(potionMort)
        joueurMort.deadNuit = 1
        room.potionMort = 1

    sio.emit('nouveauMessage', ['MDJ', "La sorcière a lancé sa magie sur le village, elle se rendort."])

    room.tour = "voy"
    Tour()

@sio.on('RespVOY')
def RespVOY(data):
    player = room.GetPlayerByPseudo(data)
    emit('nouveauMessage', ["MDJ", "Le role de " + data + " est " + libelleRole[player.role] + " !"])

    sio.emit('nouveauMessage', ["MDJ", "La voyante en a appris beaucoup sur une personne, elle ferme les yeux."])
    room.tour = 'jour'
    room.jour += 1
    Tour()

@sio.on('RespCHASS')
def RespCHASS(data):
    player = room.GetPlayerByPseudo(data)
    sio.emit('nouveauMessage', ["MDJ", "Le chasseur a décidé d'exécuter " + player.pseudo + ", il était " + libelleRole[player.role] + " !"])
    player.dead = 1

    listePseudoEnVie = []
    for player in room.players:
        if player.dead == 0:
            listePseudoEnVie.append(player.pseudo)

    AffichageListe()
    sio.emit('JOUR', listePseudoEnVie)

@sio.on('RespJOUR')
def RespJOUR(data):
    player = room.GetPlayerByPseudo(data)
    playerVotant = room.GetPlayerById(request.sid)
    sio.emit('nouveauMessage', ["MDJ", playerVotant.pseudo + " a voté contre " + player.pseudo + " !"])
    room.vote[request.sid] = player.pseudo


@sio.on('RespJOURFIN')
def RespJOURFIN(data):
    player = room.GetPlayerByPseudo(data)
    playerVotant = room.GetPlayerById(request.sid)
    if(room.vote[playerVotant.sid] != player.pseudo):
        sio.emit('nouveauMessage', ["MDJ", playerVotant.pseudo + " a voté contre " + player.pseudo + " !"])
        room.vote[request.sid] = player.pseudo
    
    player.nombreVote += 1
    room.voteValide += 1

    if(len(room.GetListeVivant()) == room.voteValide):
        

@sio.on('Chat')
def messageRecu(data):
    player = room.GetPlayerById(request.sid)
    sio.emit('nouveauMessage', [player.pseudo, data])

@sio.on('ChatLG')
def messageRecuLG(data):
    player = room.GetPlayerById(request.sid)
    sio.emit('nouveauMessageLG', [player.pseudo, data])

@sio.on('informations')
def informations():
    player = room.GetPlayerById(request.sid)
    emit('role', [player.pseudo, player.role])

@sio.on('startGame')
def startGame():
    room.started = 1
    room.DefineRole()
    sio.emit('zeParti')
    AffichageListe()
    sio.emit("nouveauMessage",["MDJ", "C'est le début de la partie, la nuit tombe sur l'école 404 tout le monde s'endort."])
    Tour()

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