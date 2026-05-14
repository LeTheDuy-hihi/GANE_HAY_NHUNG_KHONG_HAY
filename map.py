import pygame
from constants import RAW_MAP, TILE_SIZE, CYAN, PEACH, WHITE, SCORE_HEIGHT_TOP, BLACK

class Map:
    def __init__(self, raw_map=None):
        if raw_map is None:
            raw_map = RAW_MAP
        self.raw_map = raw_map
        self.grid = []
        self.pellets = []
        self.power_pellets = []
        self.width = len(raw_map[0])
        self.height = len(raw_map)
        self.parse_map()

    def parse_map(self):
        self.grid = []
        self.pellets = []
        self.power_pellets = []
        for y, row in enumerate(self.raw_map):
            grid_row = []
            for x, char in enumerate(row):
                if char == 'W':
                    grid_row.append(1)
                elif char == '-':
                    grid_row.append(4) # Ghost gate
                elif char == '.':
                    grid_row.append(0)
                    self.pellets.append((x, y))
                elif char == 'O':
                    grid_row.append(0)
                    self.power_pellets.append((x, y))
                else:
                    grid_row.append(0)
            self.grid.append(grid_row)

    def is_wall(self, grid_x, grid_y, is_ghost=False):
        # Handle wrap around tunnel
        if grid_x < 0 or grid_x >= len(self.grid[0]):
            if is_ghost:
                return True
            return False
        if grid_y < 0 or grid_y >= len(self.grid):
            return True
        val = self.grid[grid_y][grid_x]
        if val == 1:
            return True
        if val == 4 and not is_ghost:
            return True
        return False

    def draw(self, screen):
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                if val == 1:
                    # Draw neon wall
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + SCORE_HEIGHT_TOP, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, CYAN, rect, 1, border_radius=2)
                elif val == 4:
                    # Draw ghost gate
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + SCORE_HEIGHT_TOP + TILE_SIZE//2, TILE_SIZE, 4)
                    pygame.draw.rect(screen, WHITE, rect)
                    
        # Draw pellets
        for px, py in self.pellets:
            center_x = px * TILE_SIZE + TILE_SIZE // 2
            center_y = py * TILE_SIZE + TILE_SIZE // 2 + SCORE_HEIGHT_TOP
            rect = pygame.Rect(center_x - 2, center_y - 2, 4, 4)
            pygame.draw.rect(screen, PEACH, rect)

        # Draw power pellets
        for px, py in self.power_pellets:
            center_x = px * TILE_SIZE + TILE_SIZE // 2
            center_y = py * TILE_SIZE + TILE_SIZE // 2 + SCORE_HEIGHT_TOP
            pygame.draw.circle(screen, PEACH, (center_x, center_y), TILE_SIZE // 2 - 2)
