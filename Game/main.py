import pygame as pg
import socketio

pg.init()
sio = socketio.Client()
screen = pg.display.set_mode((400, 400))
COLOR_INACTIVE = (0,0,0)
COLOR_ACTIVE = (0,0,0)
FONT = pg.font.Font(None, 32)
pg.display.set_caption('Le pear Loup Garou') 
white = (255,255,255)
black = (0,0,0)
green = (0,255,0)
red = (255,0,0)
blue = (0,0,128)
text = FONT.render('Nombre de joueurs', True, black) 
textRect = text.get_rect()
textRect.center = (200, 25)
text3 = FONT.render('Nom de la room', True, black) 
textRect3 = text3.get_rect()
textRect3.center = (200, 125)
text4 = FONT.render('Mot de passe', True, black) 
textRect4 = text4.get_rect()
textRect4.center = (200, 225)

class SubmitButton:
    def __init__(self, x, y, w, h,state, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.bgColor = green
        self.text = text
        self.txt_surface = FONT.render('GO !', True, green)
        self.state = state

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                print(self.state.joueurs)
                print(self.state.room)
                print(self.state.mdp)
                sio.emit("info",{"joueurs":self.state.joueurs,"room":self.state.room,"mdp":self.state.mdp})

    def update(self):
        pass
        
    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pg.draw.rect(screen, self.bgColor, self.rect, 2)

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
                    print(self.text)
                    print(self.state.joueurs)
                    print(self.state.room)
                    print(self.state.mdp)
                    sio.emit("info",{"joueurs":self.state.joueurs,"room":self.state.room,"mdp":self.state.mdp})
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                    if self.id == 'joueurs':
                        self.state.joueurs = self.text
                    if self.id == 'room':
                        self.state.room = self.text                        
                    if self.id == 'mdp':
                        self.state.mdp = self.text
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
        self.joueurs = ''
        self.room = ''
        self.mdp = ''    

def main():
    sio.connect('http://10.50.1.66:5000')
    clock = pg.time.Clock()
    state = infoInput()
    input_box1 = InputBox(100, 50, 200, 32, 'joueurs', state)
    input_box2 = InputBox(100, 150, 200, 32, 'room', state)
    input_box3 = InputBox(100, 250, 200, 32, 'mdp', state)
    input_boxes = [input_box1, input_box2, input_box3]
    submit = SubmitButton(100, 325, 200, 50, state)
    boxes = input_boxes + [submit]
    done = False 

    screen.fill((255,255,255))
    screen.blit(text, textRect)
    screen.blit(text3, textRect3)
    screen.blit(text4, textRect4)
    
    for box in boxes:
        box.draw(screen)
    
            
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
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
