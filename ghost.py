import pygame
import math
import random
from entity import Entity
from constants import TILE_SIZE, SCORE_HEIGHT_TOP, Direction, BLUE_GHOST, WHITE_GHOST, RED, PINK, WHITE, GOLD, PURPLE
from search_algorithms import bfs, dfs, a_star

class GhostState:
    CHASE = "CHASE"
    SCATTER = "SCATTER"
    FRIGHTENED = "FRIGHTENED"

class Ghost(Entity):
    def __init__(self, grid_x, grid_y, speed, color, name, scatter_target, algorithm):
        super().__init__(grid_x, grid_y, speed)
        self.color = color
        self.name = name
        self.scatter_target = scatter_target
        self.algorithm = algorithm
        self.state = GhostState.SCATTER
        self.frightened_timer = 0
        self.frightened_flash = False
        self.wave_counter = 0
        self.patrol_points = []
        self.patrol_idx = 0
        self.teleporting = False
        self.teleport_timer = 0
        
    def get_target(self, game_map, pacman, blinky=None, pacman_history=None, controller=None):
        if self.state == GhostState.SCATTER:
            return self.scatter_target
            
        commander = next((g for g in controller.ghosts if g.name == "COMMANDER" and getattr(g, 'state', None) != GhostState.FRIGHTENED), None) if controller else None
        
        if self.state == GhostState.CHASE:
            if commander and self.name in ["BLINKY", "PINKY", "INKY"]:
                if self.name == "BLINKY":
                    return (pacman.grid_x, pacman.grid_y)
                elif self.name == "PINKY":
                    return (pacman.grid_x - pacman.direction[0]*4, pacman.grid_y - pacman.direction[1]*4)
                elif self.name == "INKY":
                    return (pacman.grid_x + pacman.direction[1]*4, pacman.grid_y - pacman.direction[0]*4)
                    
            if self.name == "BLINKY":
                return (pacman.grid_x, pacman.grid_y)
            elif self.name == "PINKY":
                tx = pacman.grid_x + pacman.direction[0] * 4
                ty = pacman.grid_y + pacman.direction[1] * 4
                return (tx, ty)
            elif self.name == "INKY":
                if blinky:
                    px = pacman.grid_x + pacman.direction[0] * 2
                    py = pacman.grid_y + pacman.direction[1] * 2
                    dx = px - blinky.grid_x
                    dy = py - blinky.grid_y
                    return (blinky.grid_x + dx * 2, blinky.grid_y + dy * 2)
                return (pacman.grid_x, pacman.grid_y)
            elif self.name == "CLYDE":
                dist = abs(self.grid_x - pacman.grid_x) + abs(self.grid_y - pacman.grid_y)
                if dist > 8:
                    return (pacman.grid_x, pacman.grid_y)
                else:
                    return self.scatter_target
            elif self.name == "PATROLLER":
                if not self.patrol_points:
                    return self.scatter_target
                target = self.patrol_points[self.patrol_idx]
                if self.grid_x == target[0] and self.grid_y == target[1]:
                    self.patrol_idx = 1 - self.patrol_idx
                # Check line of sight
                if self.grid_x == pacman.grid_x:
                    min_y, max_y = min(self.grid_y, pacman.grid_y), max(self.grid_y, pacman.grid_y)
                    wall_found = any(game_map.is_wall(self.grid_x, y) for y in range(min_y, max_y+1))
                    if not wall_found:
                        return (pacman.grid_x, pacman.grid_y)
                if self.grid_y == pacman.grid_y:
                    min_x, max_x = min(self.grid_x, pacman.grid_x), max(self.grid_x, pacman.grid_x)
                    wall_found = any(game_map.is_wall(x, self.grid_y) for x in range(min_x, max_x+1))
                    if not wall_found:
                        return (pacman.grid_x, pacman.grid_y)
                return self.patrol_points[self.patrol_idx]
            elif self.name == "LURKER":
                dist = abs(self.grid_x - pacman.grid_x) + abs(self.grid_y - pacman.grid_y)
                if dist <= 4:
                    return self.scatter_target
                return (pacman.grid_x, pacman.grid_y)
            elif self.name == "MIMIC":
                tx = self.grid_x + pacman.direction[0] * 2
                ty = self.grid_y + pacman.direction[1] * 2
                return (tx, ty)
            elif self.name == "TRAPPER":
                if controller and controller.map.power_pellets:
                    best_pp = None
                    best_d = float('inf')
                    for pp in controller.map.power_pellets:
                        d = abs(self.grid_x - pp[0]) + abs(self.grid_y - pp[1])
                        if d < best_d:
                            best_d = d
                            best_pp = pp
                    if best_pp:
                        return best_pp
                return self.scatter_target
            elif self.name == "PREDICTOR":
                if pacman_history and len(pacman_history) >= 2:
                    dx = pacman_history[-1][0] - pacman_history[-2][0]
                    dy = pacman_history[-1][1] - pacman_history[-2][1]
                    return (pacman.grid_x + dx * 10, pacman.grid_y + dy * 10)
                return (pacman.grid_x, pacman.grid_y)
            elif self.name == "TELEPORTER":
                return (pacman.grid_x, pacman.grid_y)
            elif self.name == "COMMANDER":
                return (pacman.grid_x, pacman.grid_y)
            elif self.name == "SHADOW":
                if pacman_history:
                    return pacman_history[0]
                return (pacman.grid_x, pacman.grid_y)
                
        return (pacman.grid_x, pacman.grid_y)

    def update(self, game_map, pacman, blinky=None, pacman_history=None, controller=None):
        self.wave_counter += 1
        
        if self.name == "PATROLLER" and not self.patrol_points:
            empty = []
            for y in range(game_map.height):
                for x in range(game_map.width):
                    if not game_map.is_wall(x, y):
                        empty.append((x, y))
            if empty:
                self.patrol_points = [random.choice(empty), random.choice(empty)]
                
        if self.name == "TELEPORTER" and self.state != GhostState.FRIGHTENED:
            if self.teleporting:
                self.teleport_timer -= 1
                if self.teleport_timer <= 0:
                    self.teleporting = False
                    spots = []
                    for dy in range(-4, 5):
                        for dx in range(-4, 5):
                            if abs(dx) + abs(dy) == 4:
                                nx, ny = pacman.grid_x + dx, pacman.grid_y + dy
                                if 0 <= nx < game_map.width and 0 <= ny < game_map.height:
                                    if not game_map.is_wall(nx, ny):
                                        spots.append((nx, ny))
                    if spots:
                        spot = random.choice(spots)
                        self.grid_x, self.grid_y = spot
                        self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
                        self.pixel_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2 + SCORE_HEIGHT_TOP
                return # Don't move while teleporting
            else:
                dist = abs(self.grid_x - pacman.grid_x) + abs(self.grid_y - pacman.grid_y)
                if dist > 10 and random.random() < 0.01:
                    self.teleporting = True
                    self.teleport_timer = 120
                    return
                    
        if self.name == "COMMANDER":
            self.speed = 1.0 # Slow
            
        if self.name == "SHADOW":
            self.algorithm = "A*"
            
        if self.state == GhostState.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.state = GhostState.CHASE
                self.speed = 2
            elif self.frightened_timer < 120:
                if self.frightened_timer % 15 == 0:
                    self.frightened_flash = not self.frightened_flash

        if self.is_at_center():
            self.snap_to_center()
            if self.state == GhostState.FRIGHTENED:
                directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]
                valid_dirs = []
                for d in directions:
                    nx, ny = self.grid_x + d[0], self.grid_y + d[1]
                    if not game_map.is_wall(nx, ny, is_ghost=True) and d != (-self.direction[0], -self.direction[1]):
                        valid_dirs.append(d)
                if not valid_dirs:
                    for d in directions:
                        nx, ny = self.grid_x + d[0], self.grid_y + d[1]
                        if not game_map.is_wall(nx, ny, is_ghost=True):
                            valid_dirs.append(d)
                if valid_dirs:
                    self.direction = random.choice(valid_dirs)
            else:
                target = self.get_target(game_map, pacman, blinky, pacman_history, controller)
                
                # Snap target to nearest non-wall to prevent ghosts from running in circles
                if game_map.is_wall(target[0], target[1]):
                    best_t = target
                    best_d = float('inf')
                    for dy in range(-5, 6):
                        for dx in range(-5, 6):
                            nx, ny = target[0]+dx, target[1]+dy
                            if 0 <= nx < len(game_map.grid[0]) and 0 <= ny < len(game_map.grid):
                                if not game_map.is_wall(nx, ny):
                                    dist = abs(dx) + abs(dy)
                                    if dist < best_d:
                                        best_d = dist
                                        best_t = (nx, ny)
                    target = best_t
                
                # Execute Pathfinding based on chosen Algorithm
                start_pos = (self.grid_x, self.grid_y)
                if self.algorithm == "BFS":
                    next_dir = bfs(start_pos, target, game_map, self.direction)
                elif self.algorithm == "DFS":
                    next_dir = dfs(start_pos, target, game_map, self.direction)
                else:
                    next_dir = a_star(start_pos, target, game_map, self.direction)
                
                if next_dir != Direction.NONE:
                    self.direction = next_dir

        self.pixel_x += self.direction[0] * self.speed
        self.pixel_y += self.direction[1] * self.speed

        self.grid_x = int(self.pixel_x / TILE_SIZE)
        self.grid_y = int((self.pixel_y - SCORE_HEIGHT_TOP) / TILE_SIZE)
        
        if self.grid_x < 0:
            self.grid_x = len(game_map.grid[0]) - 1
            self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        elif self.grid_x >= len(game_map.grid[0]):
            self.grid_x = 0
            self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2

    def set_frightened(self):
        if self.state != GhostState.FRIGHTENED:
            self.state = GhostState.FRIGHTENED
            self.frightened_timer = 60 * 7
            self.speed = 1
            self.frightened_flash = False
            if self.direction != Direction.NONE:
                self.direction = (-self.direction[0], -self.direction[1])

    def draw(self, screen):
        if self.teleporting:
            if (self.teleport_timer // 10) % 2 == 0:
                return # Flash effect

        radius = TILE_SIZE // 2 - 2
        center = (int(self.pixel_x), int(self.pixel_y))
        
        if self.name == "COMMANDER" and not self.teleporting:
            pygame.draw.circle(screen, GOLD, center, radius + (self.wave_counter % 20), 1)

        current_color = self.color
        if self.state == GhostState.FRIGHTENED:
            current_color = WHITE if self.frightened_flash else PURPLE

        rect_y = center[1]
        
        # Wavy bottom
        wave_offset = (self.wave_counter // 5) % 2
        points = []
        for angle in range(180, 361, 10):
            rad = math.radians(angle)
            x = center[0] + radius * math.cos(rad)
            y = center[1] + radius * math.sin(rad)
            points.append((x, y))
            
        bottom_y = center[1] + radius
        left_x = center[0] - radius
        right_x = center[0] + radius
        w = radius * 2
        
        if wave_offset == 0:
            points.append((right_x, bottom_y))
            points.append((right_x - w/4, bottom_y - 3))
            points.append((right_x - w/2, bottom_y))
            points.append((right_x - 3*w/4, bottom_y - 3))
            points.append((left_x, bottom_y))
        else:
            points.append((right_x, bottom_y - 3))
            points.append((right_x - w/4, bottom_y))
            points.append((right_x - w/2, bottom_y - 3))
            points.append((right_x - 3*w/4, bottom_y))
            points.append((left_x, bottom_y - 3))

        pygame.draw.polygon(screen, current_color, points)

        eye_offset_x = self.direction[0] * 3
        eye_offset_y = self.direction[1] * 3

        if self.state != GhostState.FRIGHTENED:
            left_eye = (center[0] - 4, center[1] - 2)
            right_eye = (center[0] + 4, center[1] - 2)
            pygame.draw.circle(screen, WHITE, left_eye, 3)
            pygame.draw.circle(screen, WHITE, right_eye, 3)

            left_pupil = (center[0] - 4 + eye_offset_x, center[1] - 2 + eye_offset_y)
            right_pupil = (center[0] + 4 + eye_offset_x, center[1] - 2 + eye_offset_y)
            pygame.draw.circle(screen, (0, 0, 150), left_pupil, 1)
            pygame.draw.circle(screen, (0, 0, 150), right_pupil, 1)
        else:
            left_eye = (center[0] - 4, center[1] - 2)
            right_eye = (center[0] + 4, center[1] - 2)
            pygame.draw.circle(screen, (255, 150, 150), left_eye, 1)
            pygame.draw.circle(screen, (255, 150, 150), right_eye, 1)
