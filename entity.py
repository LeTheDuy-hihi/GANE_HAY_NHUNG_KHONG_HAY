import pygame
from constants import TILE_SIZE, SCORE_HEIGHT_TOP, Direction

class Entity:
    def __init__(self, start_grid_x, start_grid_y, speed):
        self.grid_x = start_grid_x
        self.grid_y = start_grid_y
        self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2 + SCORE_HEIGHT_TOP
        self.speed = speed
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
        self.start_grid_x = start_grid_x
        self.start_grid_y = start_grid_y
        
    def is_at_center(self):
        target_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        target_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2 + SCORE_HEIGHT_TOP
        return abs(self.pixel_x - target_x) < 0.01 and abs(self.pixel_y - target_y) < 0.01

    def snap_to_center(self):
        self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2 + SCORE_HEIGHT_TOP

    def reset_position(self):
        self.grid_x = self.start_grid_x
        self.grid_y = self.start_grid_y
        self.snap_to_center()
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
