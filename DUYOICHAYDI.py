import pygame
import math
from entity import Entity
from constants import TILE_SIZE, SCORE_HEIGHT_TOP, Direction, YELLOW

class Pacman(Entity):
    def __init__(self, start_x, start_y, speed):
        super().__init__(start_x, start_y, speed)
        self.frame_counter = 0
        self.mouth_open = 0

    def queue_turn(self, direction):
        self.next_direction = direction

    def update(self, game_map):
        self.frame_counter += 1
        if self.frame_counter % 10 == 0:
            self.mouth_open = (self.mouth_open + 1) % 2

        if self.is_at_center():
            # Try to turn if queued
            if self.next_direction != Direction.NONE:
                next_x = self.grid_x + self.next_direction[0]
                next_y = self.grid_y + self.next_direction[1]
                if not game_map.is_wall(next_x, next_y):
                    self.direction = self.next_direction
                    self.next_direction = Direction.NONE
                    self.snap_to_center()

            # Check if can keep moving forward
            if self.direction != Direction.NONE:
                next_x = self.grid_x + self.direction[0]
                next_y = self.grid_y + self.direction[1]
                if game_map.is_wall(next_x, next_y):
                    self.direction = Direction.NONE
                    self.snap_to_center()

        # Update pixel position based on direction
        self.pixel_x += self.direction[0] * self.speed
        self.pixel_y += self.direction[1] * self.speed

        # Update grid position based on pixel
        self.grid_x = int(self.pixel_x / TILE_SIZE)
        self.grid_y = int((self.pixel_y - SCORE_HEIGHT_TOP) / TILE_SIZE)

        # Tunnel wrap
        if self.grid_x < 0:
            self.grid_x = len(game_map.grid[0]) - 1
            self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        elif self.grid_x >= len(game_map.grid[0]):
            self.grid_x = 0
            self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2

    def draw(self, screen):
        radius = TILE_SIZE // 2 - 2
        center = (int(self.pixel_x), int(self.pixel_y))
        
        if self.direction == Direction.NONE:
            pygame.draw.circle(screen, YELLOW, center, radius)
        else:
            angle = 0
            if self.direction == Direction.RIGHT: angle = 0
            elif self.direction == Direction.DOWN: angle = 90
            elif self.direction == Direction.LEFT: angle = 180
            elif self.direction == Direction.UP: angle = 270

            rad_angle = math.radians(angle)
            
            if self.mouth_open == 0:
                # Mouth open
                start_angle = rad_angle + math.radians(30)
                end_angle = rad_angle + math.radians(330)
            else:
                # Mouth almost closed
                start_angle = rad_angle + math.radians(5)
                end_angle = rad_angle + math.radians(355)

            points = [center]
            for i in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)), 5):
                x = center[0] + radius * math.cos(math.radians(i))
                y = center[1] + radius * math.sin(math.radians(i))
                points.append((x, y))
            if len(points) > 2:
                pygame.draw.polygon(screen, YELLOW, points)
            else:
                pygame.draw.circle(screen, YELLOW, center, radius)
