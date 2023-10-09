import pygame
import os
import random
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.quantum_info import Statevector
import numpy as np
from qiskit.visualization import plot_histogram

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('module://pygame_matplotlib.backend_pygame')

plt.margins(x=0)
plt.gca().spines[['right', 'top']].set_visible(False)

player_lives = 3
score = 0
fruits = ['cnot', 'h', 'x', 'u', 'measure']
WIDTH = 1200
HEIGHT = 800
FPS = 12

NUM_QUBITS = 4
q = QuantumRegister(NUM_QUBITS)
c = ClassicalRegister(NUM_QUBITS)
qc = QuantumCircuit(q, c)
fig = qc.draw('mpl', scale=0.5, vertical_compression="tight")

def apply_fruit(fruit_dict):
    
    if fruit_dict["gate_type"] == "x":
        qc.x(fruit_dict["qubit_list"][0])

    elif fruit_dict["gate_type"] == "h":
        qc.h(fruit_dict["qubit_list"][0])

    elif fruit_dict["gate_type"] == "u":
        thet = np.pi/(random.randint(1, 12))
        phi = np.pi/(random.randint(1, 12))
        lamb = np.pi/(random.randint(1, 12))
        qc.u(thet, phi, lamb, fruit_dict["qubit_list"][0])

    elif fruit_dict["gate_type"] == "cnot":
        qc.cx(fruit_dict["qubit_list"][0], fruit_dict["qubit_list"][1])

    elif fruit_dict["gate_type"] == "measure":
        qc.measure(qc.qubits, qc.clbits)
    
    
def measure_qubits():
    backend = Aer.get_backend('qasm_simulator') #tell it where to simulate
    job = execute(qc, backend, shots=1024)
    results = job.result()
    counts = results.get_counts(qc)
    sample = []
    for key in counts:
        for i in range(counts[key]):
            sample.append(key)

    res = random.choice(sample)
    return int(res, 2)

pygame.init()
pygame.display.set_caption('Fruity Computy')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

gameDisplay.fill((BLACK))
background = pygame.image.load('images/backgound.jpg')
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 32)
score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
lives_icon = pygame.image.load('images/white_lives.png')


def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"

    # getting qubits for gate
    qubits = [random.randint(0, NUM_QUBITS -  1)]
    if fruit == "cnot":
        second_qubit = qubits[0]
        while second_qubit == qubits[0]:
            second_qubit = random.randint(0, NUM_QUBITS -  1)

        qubits.append(second_qubit)
        
    data[fruit] = {
        'img': pygame.image.load(fruit_path),
        'x' : random.randint(100,500),               
        'y' : 800,
        'speed_x': random.randint(-10,10),    
        'speed_y': random.randint(-80, -60),    
        'throw': False,                       
        't': 0,                               
        'hit': False,
        'gate_type': fruit,
        'qubit_list': qubits

    }
    if random.random() >= 0.75:     
        data[fruit]['throw'] = True
    else:
        data[fruit]['throw'] = False
data = {}

for fruit in fruits:
    generate_random_fruits(fruit)


font_name = pygame.font.match_font('comic.ttf')

def draw_text(display, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    gameDisplay.blit(text_surface, text_rect)


def draw_lives(display, x, y, lives, image) :
    for i in range(lives) :
        img = pygame.image.load(image)
        img_rect = img.get_rect()      
        img_rect.x = int(x + 35 * i)   
        img_rect.y = y                 
        display.blit(img, img_rect)

def hide_cross_lives(x, y):
    gameDisplay.blit(pygame.image.load("images/red_lives.png"), (x, y))


def show_gameover_screen(measured_score):
    gameDisplay.blit(background, (0,0))
    draw_text(gameDisplay, "FRUITY COMPUTY!", 64, WIDTH / 2, HEIGHT / 4)
    if not game_over :
        # draw_text(gameDisplay,"Score : " + str(score), 40, WIDTH / 2, 250)
        draw_text(gameDisplay,"Measured Score : " + str(measured_score), 40, WIDTH / 2, 250)


    draw_text(gameDisplay, "Press a key to begin!", 24, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


first_round = True
game_over = True        
game_running = True    
while game_running :
    if game_over :
        if first_round :
            show_gameover_screen(measured_score=0)
            first_round = False
        game_over = False
        player_lives = 3
        draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')
        score = 0

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            game_running = False

    gameDisplay.blit(background, (0, 0))
    gameDisplay.blit(score_text, (0, 0))
    draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

    for key, value in data.items():
        if value['throw']:
            value['x'] += value['speed_x']
            value['y'] += value['speed_y']
            value['speed_y'] += (1 * value['t'])
            value['t'] += 1

            if value['y'] <= 800:
                gameDisplay.blit(value['img'], (value['x'], value['y']))
            else:
                generate_random_fruits(key)

            current_position = pygame.mouse.get_pos()

            # checking if we hit the fruit
            if not value['hit'] and current_position[0] > value['x'] and current_position[0] < value['x']+60 \
                    and current_position[1] > value['y'] and current_position[1] < value['y']+60:
                

                # apply the gate
                apply_fruit(value)

                if key == 'measure':
                    score = measure_qubits
                    half_fruit_path = "explosion.png"
                    show_gameover_screen(measured_score=score)
                    game_over = True
                    
                else:
                    half_fruit_path = "images/" + "half_" + key + ".png"

                value['img'] = pygame.image.load(half_fruit_path)
                value['speed_x'] += 10
                if key != 'bomb' :
                    score += 1
                score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
                value['hit'] = True
        else:
            generate_random_fruits(key)

    fig = qc.draw('mpl', scale=0.5, vertical_compression="tight")
    # fig.set_figheight(100)
    # fig.set_figwidth(200)
    fig.canvas.draw()
    gameDisplay.blit(fig, (10, 10))
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()