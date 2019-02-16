"""render dict into tensor.

start mongodb:  mongod --port 27027
"""
# pylint: disable-msg=C0103, C0111, R0913, R0903

import msgpack
import msgpack_numpy
import numpy as np
import table
import common
msgpack_numpy.patch()

import pygame
pygame.init()

pygame_ratio = 50
W = table.Pool8ftDetail.WIDTH * common.DIM_RATIO * pygame_ratio
L = table.Pool8ftDetail.LENGTH * common.DIM_RATIO * pygame_ratio
BALL_R = table.Pool8ftDetail.BALL_R * common.DIM_RATIO * pygame_ratio

state = {
    'Cue_Ball': [[-1.0826488110264874, 2.764484928802653], 0.790575],
    'ball9': [[3.5168628746629067, -9.170075557470645], 0.790575],
    'ball2': [[-2.5578641012245766, 7.596637279128271], 0.790575],
    'ball3': [[1.8803320107302854, 6.816658977025898], 0.790575],
    'ball1': [[0.9049669329801633, 3.874657386963775], 0.790575],
    'ball6': [[0.43009254016771864, 5.895219157147112], 0.790575],
    'ball4': [[-0.9934478168967825, 10.552282262813854], 0.790575],
    'ball7': [[0.0711056113822548, 6.963264845850667], 0.790575],
    'ball5': [[-4.678728292607393, 6.620426333453732], 0.790575],
    'ball8': [[1.1634084847298825, 8.624910705775264], 0.790575]
}


def show_ball(screen, center, ball):
    x = int(center[0] * pygame_ratio + W / 2)
    y = int(L / 2 - center[1] * pygame_ratio)
    pygame.draw.circle(screen, [0, 0, 0], [x, y], int(BALL_R), 0)
    if ball == 'Cue_Ball':
        number = '0'
    else:
        number = ball[-1]
    screen.blit(
        font.render(number, True, (255, 255, 255)),
        [int(x - BALL_R / 2.35), int(y - BALL_R / 1.2)])


screen = pygame.display.set_mode([int(W), int(L)])
font = pygame.font.SysFont('Arial', 25 * pygame_ratio // 50)
pygame.display.set_caption('Draw')
#
# while 1:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT: pygame.quit()
screen.fill([255, 255, 255])
for ball in state:
    if state[ball][1] < 0.5:
        continue
    show_ball(screen, state[ball][0], ball)
pygame.display.update()
pygame.display.flip()
# pygame.image.save(screen, 'test.png')
