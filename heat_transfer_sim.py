import random
import math
import pygame
import time
import copy

pygame.init()
pygame.font.init()

pygame.display.set_caption('heat transfer basic')
screen_height = 600; screen_width = 600
screen = pygame.display.set_mode((int(screen_width*1.5), screen_height))
clock = pygame.time.Clock()
FPS = 30 # Frames per second
heat_transfer_rate = .01

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (100, 200, 255)
YELLOW = (255, 255, 0)
GRAY = (126, 126, 126)

myfont = pygame.font.SysFont('Comic Sans MS', 15)

cold = 273.15 + 500
hot = 373.15 + 500

min_temp = cold
max_temp = hot
click_temp = 250

N = 21
size = 350//N

all_temps = [[cold for i in range(N)] for j in range(N)]
all_temps[N//2][N//2] = hot*30

enabled = [[True for i in range(N)] for j in range(N)]

class Molecule:
    def __init__(self, pos, temp,i,j,e = True):
        self.pos = pos
        self.temp = temp
        self.set_color()
        self.size = size #height and width of bounding box
        self.i = i
        self.j = j
        self.enabled = e
        return

    def set_color(self):
        R = (self.temp - min_temp)/(max_temp - min_temp)*255
        B = 255 - (self.temp - min_temp)/(max_temp - min_temp)*255
        G = 0

        if R > 255:
            R = 255
        elif R < 0:
            R = 0
        if B > 255:
            B = 255
        elif B < 0:
            B = 0

        self.color = [int(R), int(G), int(B)]
        return

    def update(self, old_molecs):
        if self.enabled:
            i = self.i; j = self.j;
            s = self.temp
            c = 1
            if i!=0:
                adj = old_molecs[i-1][j]
                s = s + adj.temp*heat_transfer_rate
                c = c + 1*heat_transfer_rate
            if i!=(N-1):
                adj = old_molecs[i+1][j]
                s = s + adj.temp*heat_transfer_rate
                c = c + 1*heat_transfer_rate
            if j!=0:
                adj = old_molecs[i][j-1]
                s = s + adj.temp*heat_transfer_rate
                c = c + 1*heat_transfer_rate
            if j!=(N-1):
                adj = old_molecs[i][j+1]
                s = s + adj.temp*heat_transfer_rate
                c = c + 1*heat_transfer_rate
            self.temp = s/c
        return

    def draw(self):
        self.set_color()
        pygame.draw.circle(screen, self.color, self.pos, self.size/2)
        return

def get_dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def compare_molecules(event, molecs):
    if event.button != 1:
        return
    mouse_pos = event.pos
    for row in molecs:
        for m in row:
            dist = get_dist(m.pos, mouse_pos)
            if dist < m.size//2:
                m.temp = click_temp
    return

class Slider:
    def __init__(self, pos, width, min_val, max_val, init_val, label):
        self.pos = pos
        self.width = width
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = init_val
        self.current_pos = [pos[0] + width//2, pos[1]+2.5]
        self.label = label
        self.pressed = False
        return
    def update_mousedown(self, event):
        if event.button == 1:
            mouse_pos = event.pos
            if (abs(mouse_pos[1] - self.pos[1]) < 5) and (mouse_pos[0] > self.pos[0] and mouse_pos[0] < (self.pos[0] + self.width)):
                self.pressed = True
        return
    def update_mouseup(self, event):
        if event.button == 1:
            self.pressed = False
        return
    def update(self):
        if self.pressed:
            mouse_pos = list(pygame.mouse.get_pos())
            if mouse_pos[0] < self.pos[0]:
                mouse_pos[0] = self.pos[0]
            elif mouse_pos[0] > (self.pos[0] + self.width):
                mouse_pos[0] = self.pos[0] + self.width
            self.current_val = (mouse_pos[0] - self.pos[0])/(self.width)*(self.max_val - self.min_val) + self.min_val
            self.current_pos = (mouse_pos[0], self.pos[1]+2.5)
        return
    def draw(self):
        pygame.draw.rect(screen, BLACK, pygame.Rect(self.pos[0], self.pos[1], self.width, 5))
        pygame.draw.circle(screen, RED, self.current_pos, 5)
        label_surface = myfont.render(self.label + " " + str(round(self.current_val, 2)), False, (0, 0, 0))
        screen.blit(label_surface,[self.pos[0], self.pos[1] - 25])
        return

class Button:
    def __init__(self, pos, size, label, trigger_function):
        self.pos = pos
        self.size = size
        self.label = label
        self.width = self.size*2
        self.height = self.size
        self.color = BLACK
        self.trigger_function = trigger_function
        return

    def update_mousedown(self, event):
        if event.button == 1:
            mouse_pos = event.pos
            if mouse_pos[0] > self.pos[0] and mouse_pos[0] < (self.pos[0] + self.width) and mouse_pos[1] > self.pos[1] and mouse_pos[1] < (self.pos[1] + self.height):
                self.trigger_function()
                self.color = RED
        return

    def update_mouseup(self, event):
        self.color = BLACK
        return

    def update(self):
        return

    def draw(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.pos[0], self.pos[1], self.width, self.height))
        label_surface = myfont.render(self.label, False, WHITE)
        rect = label_surface.get_rect()
        rect.centerx = self.pos[0] + self.width//2
        rect.centery = self.pos[1] + self.height//2
        #screen.blit(label_surface,[self.pos[0], self.pos[1]])
        screen.blit(label_surface,rect)
        return

def run_game():
    global N
    global heat_transfer_rate
    global click_temp
    global molecs
    global old_molecs

    dist = 550//N
    offset = (600 - N*dist)/1.5
    molecs = []

    iter = 0

    for i in range(N):
        row = []
        for j in range(N):
            pos = (offset + i*dist, offset + j*dist)
            t = all_temps[i][j]
            m = Molecule(pos, t, i, j, enabled[i][j])
            row.append(m)
        molecs.append(row)

    old_molecs = copy.deepcopy(molecs)

    sliders = []
    speed_slider = Slider((600,50),275,.005, 5,.5,"Transfer Speed"); sliders.append(speed_slider)
    temp_slider = Slider((600,100),275,-max_temp, max_temp*5,click_temp,"Click Temp"); sliders.append(temp_slider)

    def update_molecs(all_temps, enabled):
        global molecs
        global old_molecs
        for i in range(N):
            for j in range(N):
                molecs[i][j].temp = all_temps[i][j]
                old_molecs[i][j].temp = all_temps[i][j]
                molecs[i][j].enabled = enabled[i][j]
                old_molecs[i][j].enabled = enabled[i][j]
        return

    def reset_hot_center():
        all_temps = [[cold for i in range(N)] for j in range(N)]
        all_temps[N//2][N//2] = hot*30
        enabled = [[True for i in range(N)] for j in range(N)]
        update_molecs(all_temps, enabled)
        return
    hot_center_button = Button((600, 150), 50, "Hot Center", reset_hot_center); sliders.append(hot_center_button)

    def reset_cold_center():
        all_temps = [[hot for i in range(N)] for j in range(N)]
        all_temps[N//2][N//2] = -cold*30
        enabled = [[True for i in range(N)] for j in range(N)]
        update_molecs(all_temps, enabled)
        return
    cold_center_button = Button((750, 150), 50, "Cold Center", reset_cold_center); sliders.append(cold_center_button)

    def reset_all_cold():
        all_temps = [[cold for i in range(N)] for j in range(N)]
        enabled = [[True for i in range(N)] for j in range(N)]
        update_molecs(all_temps, enabled)
        return
    all_cold_button = Button((600, 220), 50, "All Cold", reset_all_cold); sliders.append(all_cold_button)

    def reset_all_hot():
        all_temps = [[hot for i in range(N)] for j in range(N)]
        enabled = [[True for i in range(N)] for j in range(N)]
        update_molecs(all_temps, enabled)
        return
    all_hot_button = Button((750, 220), 50, "All Hot", reset_all_hot); sliders.append(all_hot_button)

    def reset_all_mid():
        all_temps = [[(hot + cold)/2 for i in range(N)] for j in range(N)]
        enabled = [[True for i in range(N)] for j in range(N)]
        update_molecs(all_temps, enabled)
        return
    all_mid_button = Button((600, 290), 50, "All Mid", reset_all_mid); sliders.append(all_mid_button)

    def reset_hot_border():
        all_temps = [[cold for i in range(N)] for j in range(N)]
        for i in range(N):
            all_temps[i][0] = hot + 300
            all_temps[i][N-1] = hot + 300
            all_temps[0][i] = hot + 300
            all_temps[N-1][i] = hot + 300
        enabled = [[True for i in range(N)] for j in range(N)]
        update_molecs(all_temps, enabled)
        return
    hot_border_button = Button((750, 290), 50, "Hot Border", reset_hot_border); sliders.append(hot_border_button)

    def reset_cold_border():
        all_temps = [[hot+80 for i in range(N)] for j in range(N)]
        for i in range(N):
            all_temps[i][0] = 0
            all_temps[i][N-1] = 0
            all_temps[0][i] = 0
            all_temps[N-1][i] = 0
        enabled = [[True for i in range(N)] for j in range(N)]
        update_molecs(all_temps, enabled)
        return
    cold_boarder_button = Button((600, 360), 50, "Cold Border", reset_cold_border); sliders.append(cold_boarder_button)



    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for slider in sliders:
                    slider.update_mousedown(event)
                compare_molecules(event, molecs)
            if event.type == pygame.MOUSEBUTTONUP:
                for slider in sliders:
                    slider.update_mouseup(event)

        screen.fill(GRAY)

        for row in molecs:
            for m in row:
                m.update(old_molecs)
                m.draw()

        for slider in sliders:
            slider.update()
            slider.draw()

        heat_transfer_rate = speed_slider.current_val
        click_temp = temp_slider.current_val

        old_molecs = copy.deepcopy(molecs)
        pygame.display.update()  # Or pygame.display.flip()
        iter = iter + 1

while True:
    run_game()
