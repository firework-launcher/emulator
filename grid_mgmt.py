import math

class GridMGMT:
    def __init__(self, pygame, display, y_offset):
        self.pygame = pygame
        self.display = display
        self.y_offset = y_offset
        self.grid_details = None
        self.box_surfaces = {}
    
    def closest_factors(self, num):
        factors = []
        for i in range(1, num + 1):
            if num % i == 0:
                factors.append(i)
        middle = len(factors) // 2
        return [factors[middle-1], factors[middle]] if len(factors) % 2 == 0 else [factors[middle], factors[middle]]
 

    def get_grid_details(self, resolution, count):
        screen_width, screen_height = resolution
        num_rows, num_cols = self.closest_factors(count)
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
        return width, height

    def create_surfaces(self, count, original_res=None):
        grid_details = self.get_grid_details(self.get_resolution(original_res), count)
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
