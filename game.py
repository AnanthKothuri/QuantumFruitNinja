import pygame
import os
import random
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.quantum_info import Statevector
import numpy as np
from qiskit.visualization import plot_histogram

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import matplotlib.backends.backend_agg as agg
matplotlib.use('module://pygame_matplotlib.backend_pygame')

plt.margins(x=0)
plt.gca().spines[['right', 'top']].set_visible(False)

def choose_qubits():
    qb1 = random.randint(0, NUM_QUBITS - 1)
    qb2 = qb1
    while (qb2 == qb1):
        qb2 = random.randint(0, NUM_QUBITS - 1)

    return [qb1, qb2]

player_lives = 3
fruits = ['cnot', 'h', 'x', 'u', 'measure']
WIDTH = 1200
HEIGHT = 800
FPS = 12

NUM_QUBITS = 4
qubits_to_apply = choose_qubits()
q = QuantumRegister(NUM_QUBITS + 1)
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
        qc.measure(qc.qubits[:-1], qc.clbits)
    
    
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

def random_teleport():
    qubit_to_teleport = random.randint(0, NUM_QUBITS - 1)
    qubit_dst = qubit_to_teleport
    qc.reset(qubit_dst)
    while (qubit_dst == qubit_to_teleport):
        qubit_dst = random.randint(0, NUM_QUBITS - 1)
    
    qc.barrier()
    qc.h(NUM_QUBITS)
    qc.cx(NUM_QUBITS, qubit_dst)

    qc.barrier()
    qc.cx(qubit_to_teleport, NUM_QUBITS)
    qc.h(qubit_to_teleport)

    qc.barrier()
    qc.cx(NUM_QUBITS, qubit_dst)
    qc.cz(qubit_to_teleport, qubit_dst)
    qc.reset(NUM_QUBITS)

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
qb_text = font.render('Qubits : [' + str(qubits_to_apply[0]) + ", " + str(qubits_to_apply[1]) + "]", True, (255, 255, 255))
lives_icon = pygame.image.load('images/white_lives.png')


def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
        
    data[fruit] = {
        'img': pygame.image.load(fruit_path),
        'x' : random.randint(100,WIDTH - 100),               
        'y' : 800,
        'speed_x': random.randint(-10,10),    
        'speed_y': random.randint(-65, -50),    
        'throw': False,                       
        't': 0,                               
        'hit': False,
        'gate_type': fruit,
        'qubit_list': qubits_to_apply

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
ticks = 0
old_tick = 0
teleport_time = random.randint(100, 200)

increment_text_time = False
text_time = 50

while game_running:
    if increment_text_time:
        if text_time > 0:
            draw_text(gameDisplay, "Teleportation", 64, WIDTH / 2, HEIGHT / 4)
            text_time -= 1
        else:
            increment_text_time = False

    # ticking logic
    if ticks == teleport_time + old_tick:
        random_teleport()
        draw_text(gameDisplay, "Teleportation", 64, WIDTH / 2, HEIGHT / 4)
        increment_text_time = True
        text_time = 50
        
        pygame.display.flip()
        teleport_time = random.randint(100, 200)
        old_tick = ticks

    ticks += 1
    
    if game_over :
        if first_round :
            show_gameover_screen(measured_score=0)
            first_round = False
        game_over = False
        player_lives = 3
        draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            game_running = False

    gameDisplay.blit(background, (0, 0))
    gameDisplay.blit(qb_text, (0, 0))
    #draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

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
                    score = measure_qubits()
                    half_fruit_path = "images/explosion.png"
                    show_gameover_screen(measured_score=score)
                    q = QuantumRegister(NUM_QUBITS + 1)
                    c = ClassicalRegister(NUM_QUBITS)
                    qc = QuantumCircuit(q, c)
                    game_over = True
                    
                    
                else:
                    half_fruit_path = "images/" + "half_" + key + ".png"

                value['img'] = pygame.image.load(half_fruit_path)
                value['speed_x'] += 10
                if key != 'bomb' :
                    qubits_to_apply = choose_qubits()
                qb_text = font.render('Qubits : [' + str(qubits_to_apply[0]) + ", " + str(qubits_to_apply[1]) + "]", True, (255, 255, 255))
                value['hit'] = True
        else:
            generate_random_fruits(key)

    fig = qc.draw('mpl', scale=0.4, vertical_compression="tight")
    fig.patch.set_alpha(0.1) 
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()

    size = canvas.get_width_height()
    image = pygame.image.frombuffer (raw_data, size, "RGBA")

    gameDisplay.blit(image, (10, 10))
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()