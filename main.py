import emulator_io
import argparse
import pygame
import time
import sys
import os
import grid_mgmt


emutype = input('Serial (s), ESP Node (esp), or IP launcher (ip)?: ')
port_count = 16 if emutype == 'esp' else int(input('Port count: '))

class PinData:
    def __init__(self, armed):
        self.pin_data = []
        self.armed = armed

pins = PinData(not emutype == 'esp')

if emutype == 's':
    emulator = emulator_io.SerialMGMT(pins)
elif emutype == 'ip':
    emulator = emulator_io.IPMGMT(pins)
elif emutype == 'esp':
    emulator = emulator_io.ESPMGMT(pins)
else:
    print('Invalid option')
    exit(1)

emulator.create_port()

for pin in range(port_count):
    pin += 1
    pins.pin_data.append({
        'pin': pin,
        'state': 0 if emutype == 'esp' else 1,
        'on': True,
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

def get_img_corners(x, y, w, h):
    corners = {}
    corners['top_left'] = (x-w/2, y-h/2)
    corners['top_right'] = (x+w/2, y-h/2)
    corners['bottom_left'] = (x-w/2, y+h/2)
    corners['bottom_right'] = (x+w/2, y+h/2)
    return corners

def reset_button(x, y, pressed=False):
    w = 100
    h = 30
    color = (255, 0, 0)
    color_hover = (200, 0, 0)
    color_fg = (255, 255, 255)
    color_fg_hover = (220, 220, 220)
    position = pygame.mouse.get_pos()
    corners = get_img_corners(x, y, w, h)
    if position[0] <= corners['top_right'][0] and position[0] >= corners['top_left'][0] and position[1] <= corners['bottom_left'][1] and position[1] >= corners['top_left'][1]:
        if not pressed:
            pygame.draw.rect(display, color_hover, pygame.Rect(x-w/2, y-h/2, w, h))
            blit_text_center(display, x, y, 'Reset', 40, color_fg_hover)
        else:
            pins.pin_data = []
            for pin in range(port_count):
                pin += 1

                pins.pin_data.append({
                    'pin': pin,
                    'state': 0 if emutype == 'esp' else 1,
                    'on': True,
                    'launched': False
                })

            print('Pin Data Reset')
    else:
        if not pressed:
            pygame.draw.rect(display, color, pygame.Rect(x-w/2, y-h/2, w, h))
            blit_text_center(display, x, y, 'Reset', 40, color_fg_hover)

running = True
pygame.init()
pygame.font.init()
display = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

grid = grid_mgmt.GridMGMT(pygame, display, 100, emutype, pins)
grid.create_surfaces(port_count)

while running:
    clock.tick(60)
    display.fill((64, 64, 64))
    width, height = pygame.display.get_surface().get_size()
    emulator.check_read()
    blit_text_center(display, width/2, 30, emulator.top_msg, 30, (255, 255, 255))
    reset_button(width/2, 60)

    for box in grid.box_surfaces:
        surface = grid.box_surfaces[box]
        surface.fill((64, 64, 64))
        if pins.pin_data[box[2]-1]['on']:
            blit_text_center(surface, grid.grid_details['cell_size'][0]/2, grid.grid_details['cell_size'][1]/4, 'Pin {}'.format(box[2]), 30, ((255, 255, 255)))
            if pins.armed:
                blit_text_center(surface, grid.grid_details['cell_size'][0]/2, grid.grid_details['cell_size'][1]/4*2, 'State: {}'.format(pins.pin_data[box[2]-1]['state']), 30, ((255, 255, 255)))
                launched = pins.pin_data[box[2]-1]['launched']
                if launched:
                    blit_text_center(surface, grid.grid_details['cell_size'][0]/2, grid.grid_details['cell_size'][1]/4*3, 'Launched: Yes', 20, ((0, 255, 0)))
                else:
                    blit_text_center(surface, grid.grid_details['cell_size'][0]/2, grid.grid_details['cell_size'][1]/4*3, 'Launched: No', 20, ((255, 0, 0)))

        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect((0, 0), grid.grid_details['cell_size']), 2)
    grid.draw_surfaces()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            grid.create_surfaces(port_count, (event.w, event.h))
        if event.type == pygame.MOUSEBUTTONDOWN:
            reset_button(width/2, 60, pressed=True)
            grid.mousepress()
    pygame.display.update()

os.kill(os.getpid(), 9)
