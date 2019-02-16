import pygame
import random
import numpy as np
from multiprocessing import Process, Queue
from zmqlib import Pull
pygame.init()
screen = pygame.display.set_mode((640, 960))
clock = pygame.time.Clock()
done = False

dataqueue = Queue()
stats = [-999, 0, -1, 0]
actions = [0, 0, 0, 0, 0]
pocket = -1
A = 0
cb = 1
nb = 2
font = pygame.font.SysFont("comicsansms", 40)

COLORS = {
    1: (255, 255, 0),
    2: (0, 0, 255),
    3: (255, 0, 0),
    4: (155, 48, 255),
    5: (255, 165, 0),
    6: (0, 255, 0),
    7: (188, 143, 143),
    8: (0, 0, 0),
    9: (255, 255, 0)
}


class PullStat(Process, Pull):
    def __init__(self):
        super().__init__()

    def run(self):
        global stats
        global actions
        global pocket
        self.build_record_socket()
        while True:
            cb, nb, A, a, s, p = self.recv_player()
            for i in range(5):
                actions[i] = a[i]
            for i in range(4):
                stats[i] = s[i]
            pocket = p
            cb = int(cb[-1])
            nb = int(nb[-1])
            dataqueue.put((cb, nb, A, actions, stats, pocket))


puller = PullStat()
puller.start()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True

    screen.fill((255, 255, 255))
    if dataqueue.qsize():
        cb, nb, A, actions, stats, pocket = dataqueue.get()
        pocket = pocket

    text = font.render('MACRO POCKET: %d - ANGLE: %0.3f' % (pocket, A), True,
                       (0, 128, 0))
    screen.blit(text, (10, 50))

    text = font.render('MICRO ACTIONS:', True, (0, 128, 0))
    screen.blit(text, (10, 150))
    text = font.render('angle:     %0.3f' % actions[0], True, (0, 128, 0))
    screen.blit(text, (100, 200))
    text = font.render('speed:     %0.3f' % actions[1], True, (0, 128, 0))
    screen.blit(text, (100, 300))
    text = font.render('lift:        %0.3f' % actions[2], True, (0, 128, 0))
    screen.blit(text, (400, 200))
    text = font.render('top/back: %0.3f' % actions[3], True, (0, 128, 0))
    screen.blit(text, (100, 250))
    text = font.render('left/right:%0.3f' % actions[4], True, (0, 128, 0))
    screen.blit(text, (400, 250))

    text = font.render('RENEWAL ALGORITHM', True, (0, 128, 0))
    screen.blit(text, (10, 500))

    v_star, v, l_star, l = stats
    text = font.render('V*:        %0.3f' % (v_star / 3), True, (0, 128, 0))
    screen.blit(text, (100, 550))
    text = font.render('V :        %0.3f' % (v / 3), True, (0, 128, 0))
    screen.blit(text, (100, 600))
    text = font.render('l*:        %d' % l_star, True, (0, 128, 0))
    screen.blit(text, (100, 650))
    text = font.render('l :        %d' % l, True, (0, 128, 0))
    screen.blit(text, (100, 700))

    text = font.render('CUR', True, (0, 128, 0))
    screen.blit(text, (150, 750))
    text = font.render('NEXT', True, (0, 128, 0))
    screen.blit(text, (350, 750))
    pygame.draw.circle(screen, COLORS[cb], (200, 850), 50, 0)
    pygame.draw.circle(screen, COLORS[nb], (400, 850), 50, 0)
    pygame.display.flip()
    clock.tick(60)
