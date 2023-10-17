# imports
import pygame
import os
import random
import time
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

# print instructions
print("Welcome to Fruity Computy!")
time.sleep(2)
print("This is a game based on Fruit Ninja, but with a quantum twist...")
time.sleep(2)
print("The different fruits represent a different quantum gate - NOT, Hadamard, C-NOT, random unitary, and measurement.")
time.sleep(4)
print("The top left shows two important things: which qubits you're acting on, and what the circuit looks like at the moment.")
time.sleep(4)
print("At random moments, the value from a random qubit will be teleported to another.")
time.sleep(3)
print("Hitting the bomb fruit will end the game and display your score.")
time.sleep(2)
print("Make sure that the pygame, numpy, qiskit, qiskit-aer, pylatexenc, and matplotlib libraries are pip installed on your computer!")
time.sleep(4)

# game window settings
plt.margins(x=0)
plt.gca().spines[['right', 'top']].set_visible(False)
pygame.init()

# function for choosing two random, different qubits
def choose_qubits():
    qb1 = random.randint(0, NUM_QUBITS - 1)
    qb2 = qb1
    while (qb2 == qb1):
        qb2 = random.randint(0, NUM_QUBITS - 1)

    return [qb1, qb2]

# initialize variables at start
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

# function for applying quantum gates
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
    
# function to measure qubits and get score
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

# function that randomly teleports a qubit's value to another qubit
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

# start the game
pygame.init()
pygame.display.set_caption('Fruity Computy')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255,255,255)
BLACK = (0,0,0)
gameDisplay.fill((BLACK))
background = pygame.image.load('images/backgound.jpg')
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 32)
qb_text = font.render('Qubits : [' + str(qubits_to_apply[0]) + ", " + str(qubits_to_apply[1]) + "]", True, (255, 255, 255))
lives_icon = pygame.image.load('images/white_lives.png')

# function that spawns fruits
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

# function for drawing text on screen
def draw_text(display, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    gameDisplay.blit(text_surface, text_rect)

# function for showing score at end
def show_gameover_screen(measured_score):
    gameDisplay.blit(background, (0,0))
    draw_text(gameDisplay, "FRUITY COMPUTY!", 64, WIDTH / 2, HEIGHT / 4)
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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

    gameDisplay.blit(background, (0, 0))
    gameDisplay.blit(qb_text, (0, 0))

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

                # end the game if measurement hit
                if key == 'measure':
                    score = measure_qubits()
                    half_fruit_path = "images/explosion.png"
                    show_gameover_screen(score)
                    q = QuantumRegister(NUM_QUBITS + 1)
                    c = ClassicalRegister(NUM_QUBITS)
                    qc = QuantumCircuit(q, c)

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

    # resize, reshape, and display circuit diagram
    matplotlib.pyplot.close()
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
