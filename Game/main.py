import pygame as pg
import socketio

pg.init()
sio = socketio.Client()
screen = pg.display.set_mode((800, 700))
COLOR_INACTIVE = (0,0,0)
COLOR_ACTIVE = (0,0,0)
FONT = pg.font.Font(None, 32)
pg.display.set_caption('Le pear Loup Garou') 
white = (255,255,255)
black = (0,0,0)
green = (0,255,0)
red = (255,0,0)
blue = (0,0,128)
text = FONT.render('Nom du joueur', True, black) 
textRect = text.get_rect()
textRect.center = (200, 25)
text5 = FONT.render('Pseudo des joueurs présents', True, black) 
textRect5 = text5.get_rect()
textRect5 = (400, 12)

class Listing:
    def __init__(self, x, y, w, h, listing=[]):
        self.rect = pg.Rect(x, y, w, h)
        self.bgColor = black
        self.listing = listing
        self.txt_surfaces = []
        for pseudo in self.listing:
            if pseudo == '':
                self.txt_surfaces.append(FONT.render('En attente', True, red))
            else:
                self.txt_surfaces.append(FONT.render(pseudo, True, green))

    def draw(self, screen):
        y = self.rect.y + 5
        for txt_surface in self.txt_surfaces:
            screen.blit(txt_surface, (self.rect.x, y))
            y += 50
        self.rect.h = y - 50
        pg.draw.rect(screen, white, self.rect, 1)
    def reset(self, screen):
        self.rect.h = len(self.listing) * 50
        pg.draw.rect(screen, white, self.rect)

class Etat:
    def __init__(self):
        self.liste = ''

etat = Etat()
@sio.on('listeJoueurs')
def listeJoueurs(data):
    listing = data[0]
    firstTime = data[1]
    if firstTime == 0:
        etat.liste.reset(screen)
    DataServ = Listing(400,50,300,50,listing)
    DataServ.draw(screen)
    etat.liste = DataServ

class SubmitButton:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.bgColor = green
        self.text = text
        self.txt_surface = FONT.render('GO !', True, green)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                sio.emit("chooseName",{"pseudo":self.state.pseudo})

    def update(self):
        pass
        
    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pg.draw.rect(screen, self.bgColor, self.rect, 2)

    def reset(self,screen):
        pg.draw.rect(screen, white, self.rect)

bouton = SubmitButton(100, 325, 200, 50)
@sio.on('goGame')
def GameStart(data):
    donnees = data
    print(donnees)
    if donnees == 1:
        bouton.draw(screen)
    else :
        bouton.reset(screen)
    

class InputBox:
    def __init__(self, x, y, w, h, id, state, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.surface = pg.Surface((w, h), pg.SRCALPHA)
        self.surface.fill((255,255,255))
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, red)
        self.active = False
        self.state = state
        self.id = id

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    sio.emit("chooseName",{"pseudo":self.state.pseudo})
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                    if self.id == 'pseudo':
                        self.state.pseudo = self.text
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Reset surface
        screen.blit(self.surface, (self.rect.x, self.rect.y))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

class infoInput:
    def __init__(self):
        self.pseudo = ''
        self.room = ''
        self.mdp = ''    

def main():
    sio.connect('http://192.168.43.9:5000')
    clock = pg.time.Clock()
    state = infoInput()
    input_box1 = InputBox(100, 50, 200, 32, 'pseudo', state)
    #input_box2 = InputBox(100, 150, 200, 32, 'room', state)
    #input_box3 = InputBox(100, 250, 200, 32, 'mdp', state)
    input_boxes = [input_box1]
    #, input_box2, input_box3
    boxes = input_boxes
    done = False

    screen.fill((255,255,255))
    screen.blit(text, textRect)
    screen.blit(text5, textRect5)
    #screen.blit(text3, textRect3)
    #screen.blit(text4, textRect4)

    for box in boxes:
        box.draw(screen)
    
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
                sio.disconnect()
            for box in boxes:
                box.handle_event(event)
                box.update()
                box.draw(screen)

        #for box in input_boxes:
        #    box.draw(screen)
        
        pg.display.flip()
        clock.tick(30)



if __name__ == '__main__':
    main()
    pg.quit()
