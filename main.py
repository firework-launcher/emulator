import serial_mgmt
import argparse
import pygame
import time
import sys
import os
import grid_mgmt

serial = serial_mgmt.SerialMGMT()
serial.create_port()
pin_data = []

for pin in range(32):
    pin += 1
    pin_data.append({
        'pin': pin,
        'state': 1,
        'launched': False
    })

def blit_text_center(display, x, y, text, font_size, color):
    font = pygame.font.SysFont('Sans Serif', font_size)
    text_surface = font.render(text, False, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    display.blit(text_surface, text_rect)

def blit_text(surface, text, font_size, pos, color=(255, 255, 255)):
    font = pygame.font.SysFont('Sans Serif', font_size)
    lines = text.split('\n')
    x, y = pos
    for line in lines:
        line_surface = font.render(line, 0, color)
        line_width, line_height = line_surface.get_size()
        surface.blit(line_surface, (x, y))
        y += line_height

running = True
pygame.init()
pygame.font.init()
display = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

grid = grid_mgmt.GridMGMT(pygame, display, 100)
grid.create_surfaces()

while running:
    clock.tick(60)
    display.fill((64, 64, 64))
    width, height = pygame.display.get_surface().get_size()
    read = serial.check_read()
    blit_text_center(display, width/2, 30, 'Serial port: {}'.format(serial.port), 40, (255, 255, 255))
    for box in grid.box_surfaces:
        surface = grid.box_surfaces[box]
        surface.fill((64, 64, 64))
        blit_text_center(surface, grid.grid_details['cell_size'][0]/2, grid.grid_details['cell_size'][1]/4, 'Pin {}'.format(box[2]), 30, ((255, 255, 255)))
        blit_text_center(surface, grid.grid_details['cell_size'][0]/2, grid.grid_details['cell_size'][1]/4*2, 'State: {}'.format(pin_data[box[2]-1]['state']), 30, ((255, 255, 255)))
        launched = pin_data[box[2]-1]['launched']
        if launched:
            blit_text_center(surface, grid.grid_details['cell_size'][0]/2, grid.grid_details['cell_size'][1]/4*3, 'Launched: Yes', 20, ((0, 255, 0)))
        else:
            blit_text_center(surface, grid.grid_details['cell_size'][0]/2, grid.grid_details['cell_size'][1]/4*3, 'Launched: No', 20, ((255, 0, 0)))

        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect((0, 0), grid.grid_details['cell_size']), 2)
    grid.draw_surfaces()
    if not read == None:
        read = read.decode('utf-8')
        if read.startswith('/digital'):
            pin = str(int(read.split('/')[2])-1)
            state = int(read.split('/')[3].replace('\r\n', ''))
            pin_data[int(pin)-1]['state'] = state
            if state == 0:
                pin_data[int(pin)-1]['launched'] = True
            serial.write_data(b'0')
        else:
            serial.write_data(b'1')
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            grid.create_surfaces((event.w, event.h))
    pygame.display.update()

os.kill(os.getpid(), 9)
