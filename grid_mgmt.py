import math

class GridMGMT:
    def __init__(self, pygame, display, y_offset):
        self.pygame = pygame
        self.display = display
        self.y_offset = y_offset
        self.grid_details = None
        self.box_surfaces = {}
    
    def get_grid_details(self, resolution):
        screen_width, screen_height = resolution
        num_rows = 4
        num_cols = 8
        cell_size = (round(screen_width/num_cols), round(screen_height/num_rows))
        return {
            'cell_size': cell_size,
            'num_rows': num_rows,
            'num_cols': num_cols
        }
    
    def get_resolution(self, original_res):
        if original_res == None:
            width, height = self.display.get_size()
        else:
            width, height = original_res
        height -= self.y_offset
        print(width, height)
        return width, height

    def create_surfaces(self, original_res=None):
        grid_details = self.get_grid_details(self.get_resolution(original_res))
        self.grid_details = grid_details
        self.box_surfaces = {}
        x = 0
        y = self.y_offset
        pin = 1
        cell_width, cell_height = grid_details['cell_size']
        for row in range(grid_details['num_rows']):
            for col in range(grid_details['num_cols']):
                surface = self.pygame.Surface(grid_details['cell_size'])
                self.box_surfaces[(
                    row,
                    col,
                    pin,
                    x,
                    y
                )] = surface
                pin += 1
                x += cell_width
            x = 0
            y += cell_height

    def draw_surfaces(self):
        for data in self.box_surfaces:
            self.display.blit(self.box_surfaces[data], (data[3], data[4]))
