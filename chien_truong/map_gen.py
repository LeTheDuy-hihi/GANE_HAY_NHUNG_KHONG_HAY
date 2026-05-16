import random
import math
from constants import (TILE_SIZE, MAP_W, MAP_H,
                       TILE_EMPTY, TILE_WALL, TILE_COVER, TILE_TUNNEL, TILE_EXIT, TILE_BARREL,
                       FLOOR_COLOR, TREE_COLOR, COVER_COLOR, TUNNEL_COLOR, EXIT_COLOR, BARREL_COLOR,
                       JUNGLE_DARK, JUNGLE_MID, JUNGLE_LIGHT, DARK_BG, WHITE, BLACK, YELLOW)
import pygame


class GameMap:
    def __init__(self, level=1):
        self.level       = level
        self.width       = MAP_W
        self.height      = MAP_H
        self.pixel_w     = MAP_W * TILE_SIZE
        self.pixel_h     = MAP_H * TILE_SIZE
        self.grid        = [[TILE_EMPTY]*MAP_W for _ in range(MAP_H)]
        self.detail_grid = [[0]*MAP_W for _ in range(MAP_H)] # 0: Mud, 1: Path, 2: Crater, 3: Grass
        self.player_spawn  = (3*TILE_SIZE + TILE_SIZE//2, 3*TILE_SIZE + TILE_SIZE//2)
        self.enemy_spawns  = []
        self.item_spawns   = []
        self._surface      = None
        self._generate(level)
        self._bake_surface()

    # ── Generation ──────────────────────────────────────────────────────────
    def _generate(self, level):
        W, H = self.width, self.height

        # Border
        for x in range(W):
            self.grid[0][x] = TILE_WALL
            self.grid[H-1][x] = TILE_WALL
        for y in range(H):
            self.grid[y][0] = TILE_WALL
            self.grid[y][W-1] = TILE_WALL

        # Tree clusters — sparse, scattered (open battlefield)
        n_trees = 25 + level * 5
        for _ in range(n_trees):
            cx = random.randint(2, W-3)
            cy = random.randint(2, H-3)
            radius = random.randint(1, 2)
            for dy in range(-radius, radius+1):
                for dx in range(-radius, radius+1):
                    if dx*dx + dy*dy <= radius*radius:
                        nx, ny = cx+dx, cy+dy
                        if 1 <= nx < W-1 and 1 <= ny < H-1:
                            if random.random() < 0.6:
                                self.grid[ny][nx] = TILE_WALL

        # Bunkers — tactical cover points (not too many)
        n_bunkers = 4 + level
        for _ in range(n_bunkers):
            bx = random.randint(5, W-10)
            by = random.randint(5, H-10)
            shape = random.choice(["L", "U", "I", "box"])
            if shape == "L":
                for dx in range(4):
                    self._set_cover(bx+dx, by)
                for dy in range(3):
                    self._set_cover(bx, by+dy)
            elif shape == "U":
                for dx in range(4):
                    self._set_cover(bx+dx, by)
                for dy in range(3):
                    self._set_cover(bx, by+dy)
                    self._set_cover(bx+3, by+dy)
            elif shape == "I":
                for dy in range(4):
                    self._set_cover(bx, by+dy)
            elif shape == "box":
                for dx in range(3):
                    self._set_cover(bx+dx, by)
                    self._set_cover(bx+dx, by+2)
                for dy in range(3):
                    self._set_cover(bx, by+dy)
                    self._set_cover(bx+2, by+dy)

        # Corridor cuts — wide open paths across the map
        n_corridors = 12
        for _ in range(n_corridors):
            if random.random() < 0.5:  # horizontal
                cy = random.randint(3, H-4)
                cx1, cx2 = sorted(random.sample(range(2, W-2), 2))
                width = random.randint(2, 4)
                for x in range(cx1, cx2+1):
                    for w in range(width):
                        if 0 < cy+w < H-1:
                            self.grid[cy+w][x] = TILE_EMPTY
            else:  # vertical
                cx = random.randint(3, W-4)
                cy1, cy2 = sorted(random.sample(range(2, H-2), 2))
                width = random.randint(2, 4)
                for y in range(cy1, cy2+1):
                    for w in range(width):
                        if 0 < cx+w < W-1:
                            self.grid[y][cx+w] = TILE_EMPTY

        # Tunnel entries (pairs)
        n_tunnels = 2
        for _ in range(n_tunnels):
            tx1, ty1 = random.randint(3, W//2-2), random.randint(3, H-4)
            tx2, ty2 = random.randint(W//2+2, W-3), random.randint(3, H-4)
            if self._in_bounds(tx1, ty1) and self._in_bounds(tx2, ty2):
                self.grid[ty1][tx1] = TILE_TUNNEL
                self.grid[ty2][tx2] = TILE_TUNNEL

        # Clear player spawn area (larger safe zone)
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                ny, nx = 4+dy, 4+dx
                if 0 < ny < H-1 and 0 < nx < W-1:
                    self.grid[ny][nx] = TILE_EMPTY
        self.player_spawn = (4*TILE_SIZE + TILE_SIZE//2, 4*TILE_SIZE + TILE_SIZE//2)

        # Place Exit Door (bottom-right zone)
        exit_placed = False
        for _ in range(100):
            ex = random.randint(W-10, W-3)
            ey = random.randint(H-10, H-3)
            if self.grid[ey][ex] == TILE_EMPTY:
                self.grid[ey][ex] = TILE_EXIT
                exit_placed = True
                break
        if not exit_placed:
            self.grid[H-4][W-4] = TILE_EXIT

        # Enemy spawns
        self.enemy_spawns = []
        n_spawns = 15 + level * 5
        for _ in range(n_spawns):
            for _ in range(30):
                ex = random.randint(W//3, W-3)
                ey = random.randint(2, H-3)
                if self.grid[ey][ex] == TILE_EMPTY:
                    self.enemy_spawns.append((
                        ex*TILE_SIZE + TILE_SIZE//2,
                        ey*TILE_SIZE + TILE_SIZE//2
                    ))
                    break

        # Item spawns
        self.item_spawns = []
        for _ in range(30 + level*5):
            for _ in range(20):
                ix = random.randint(2, W-3)
                iy = random.randint(2, H-3)
                if self.grid[iy][ix] == TILE_EMPTY:
                    self.item_spawns.append((ix, iy))
                    break
                    
        # Explosive Barrels (fewer)
        n_barrels = 5 + level * 2
        for _ in range(n_barrels):
            for _ in range(20):
                bx = random.randint(5, W-5)
                by = random.randint(5, H-5)
                if self.grid[by][bx] == TILE_EMPTY:
                    self.grid[by][bx] = TILE_BARREL
                    break

        # ── Detail Generation ────────────────────────────────────────────────
        # 1. Dirt Paths (Wandering paths)
        for _ in range(5):
            cur_x, cur_y = random.randint(0, W-1), random.randint(0, H-1)
            for _ in range(200):
                if 0 <= cur_x < W and 0 <= cur_y < H:
                    if self.grid[cur_y][cur_x] == TILE_EMPTY:
                        self.detail_grid[cur_y][cur_x] = 1 # Path
                cur_x += random.choice([-1, 0, 1])
                cur_y += random.choice([-1, 0, 1])

        # 2. Craters (Bomb sites)
        for _ in range(15 + level * 2):
            cx, cy = random.randint(5, W-5), random.randint(5, H-5)
            rad = random.randint(1, 2)
            for dy in range(-rad, rad+1):
                for dx in range(-rad, rad+1):
                    if dx*dx + dy*dy <= rad*rad:
                        nx, ny = cx+dx, cy+dy
                        if 0 <= nx < W and 0 <= ny < H:
                            if self.grid[ny][nx] == TILE_EMPTY:
                                self.detail_grid[ny][nx] = 2 # Crater

        # 3. Dense Grass
        for _ in range(40):
            gx, gy = random.randint(0, W-1), random.randint(0, H-1)
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if random.random() < 0.6:
                        nx, ny = gx+dx, gy+dy
                        if 0 <= nx < W and 0 <= ny < H:
                            if self.grid[ny][nx] == TILE_EMPTY and self.detail_grid[ny][nx] == 0:
                                self.detail_grid[ny][nx] = 3 # Grass

    def _set_cover(self, x, y):
        if 1 <= x < self.width-1 and 1 <= y < self.height-1:
            self.grid[y][x] = TILE_COVER

    def _in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    # ── Surface bake ────────────────────────────────────────────────────────
    def _bake_surface(self):
        """Pre-render map to a Surface for fast blitting."""
        self._surface = pygame.Surface((self.pixel_w, self.pixel_h))
        self._surface.fill(JUNGLE_DARK)
        ts = TILE_SIZE
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x*ts, y*ts, ts, ts)
                t = self.grid[y][x]
                if t == TILE_EMPTY:
                    # Base Muddy Ground
                    pygame.draw.rect(self._surface, FLOOR_COLOR, rect)
                    
                    det = self.detail_grid[y][x]
                    if det == 1: # Path (Lighter dirt)
                        pygame.draw.rect(self._surface, (45, 40, 25), rect)
                        if random.random() > 0.8:
                            pygame.draw.circle(self._surface, (60, 55, 35), (rect.x+16, rect.y+16), 2)
                    elif det == 2: # Crater (Darker scorched earth)
                        pygame.draw.rect(self._surface, (15, 10, 5), rect)
                        pygame.draw.circle(self._surface, (10, 5, 0), rect.center, ts//2 - 2)
                        # Rim
                        pygame.draw.circle(self._surface, (40, 30, 20), rect.center, ts//2, 1)
                    elif det == 3: # Dense Grass (Realistic Tufts)
                        pygame.draw.rect(self._surface, (25, 35, 15), rect) # Dark base
                        for _ in range(8):
                            gx = rect.x + random.randint(4, ts-4)
                            gy = rect.y + random.randint(4, ts-4)
                            h = random.randint(5, 10)
                            # Draw a tuft of 3 blades
                            color = random.choice([JUNGLE_MID, JUNGLE_LIGHT, (80, 100, 40), (100, 120, 50)])
                            for off in [-2, 0, 2]:
                                pygame.draw.line(self._surface, color, (gx, gy), (gx + off, gy - h), 1)
                    else: # Standard Mud
                        if (x + y) % 3 == 0:
                            pygame.draw.circle(self._surface, JUNGLE_MID, (rect.x + 8, rect.y + 8), 1)
                elif t == TILE_WALL:
                    # Jungle Tree (Realistic layering)
                    # 1. Ground Shadow
                    pygame.draw.circle(self._surface, (5, 10, 5), (rect.centerx+4, rect.centery+4), ts//2)
                    
                    # 2. Trunk
                    pygame.draw.rect(self._surface, (55, 35, 15), (rect.centerx-3, rect.centery-3, 6, 12))
                    
                    # 3. Layered Canopy
                    colors = [TREE_COLOR, (40, 80, 30), (60, 100, 40), (20, 50, 15)]
                    for i in range(5):
                        off_x = random.randint(-6, 6)
                        off_y = random.randint(-6, 6)
                        r = random.randint(ts//3, ts//2)
                        c = random.choice(colors)
                        pygame.draw.circle(self._surface, c, (rect.centerx + off_x, rect.centery + off_y), r)
                    # Top highlight
                    pygame.draw.circle(self._surface, (80, 120, 60), (rect.centerx-4, rect.centery-4), ts//4)
                elif t == TILE_COVER:
                    # Sandbag Bunker
                    pygame.draw.rect(self._surface, (60, 55, 45), rect) # Darker base
                    # Draw sandbag rows
                    for i in range(3):
                        by = rect.y + i * 10
                        pygame.draw.rect(self._surface, COVER_COLOR, (rect.x+2, by+2, ts-4, 8), border_radius=3)
                        pygame.draw.rect(self._surface, (80, 70, 50), (rect.x+2, by+2, ts-4, 8), 1, border_radius=3)
                elif t == TILE_TUNNEL:
                    # Dirt Tunnel Entrance
                    pygame.draw.rect(self._surface, (40, 30, 20), rect)
                    pygame.draw.circle(self._surface, BLACK, rect.center, ts//2 - 4)
                    # Wooden support beams
                    pygame.draw.rect(self._surface, (80, 60, 40), (rect.x, rect.y, 4, ts))
                    pygame.draw.rect(self._surface, (80, 60, 40), (rect.right-4, rect.y, 4, ts))
                    pygame.draw.rect(self._surface, (80, 60, 40), (rect.x, rect.y, ts, 4))
                elif t == TILE_EXIT:
                    # Military Heliport / Gate
                    pygame.draw.rect(self._surface, (50, 50, 50), rect)
                    pygame.draw.rect(self._surface, EXIT_COLOR, rect, 2)
                    # "H" for Helipad
                    pygame.draw.line(self._surface, WHITE, (rect.x+10, rect.y+8), (rect.x+10, rect.bottom-8), 3)
                    pygame.draw.line(self._surface, WHITE, (rect.right-10, rect.y+8), (rect.right-10, rect.bottom-8), 3)
                    pygame.draw.line(self._surface, WHITE, (rect.x+10, rect.centery), (rect.right-10, rect.centery), 3)
                elif t == TILE_BARREL:
                    # Rusty Fuel Barrel
                    pygame.draw.rect(self._surface, (80, 30, 20), rect)
                    pygame.draw.rect(self._surface, BARREL_COLOR, rect, 2)
                    pygame.draw.circle(self._surface, BARREL_COLOR, rect.center, ts//2 - 4)
                    pygame.draw.circle(self._surface, (40, 10, 5), rect.center, ts//2 - 8)
                    # Danger symbol (X)
                    pygame.draw.line(self._surface, YELLOW, (rect.x+10, rect.y+10), (rect.right-10, rect.bottom-10), 2)
                    pygame.draw.line(self._surface, YELLOW, (rect.right-10, rect.y+10), (rect.x+10, rect.bottom-10), 2)

    # ── Collision ────────────────────────────────────────────────────────────
    def is_wall(self, tx, ty):
        if tx < 0 or tx >= self.width or ty < 0 or ty >= self.height:
            return True
        return self.grid[ty][tx] in (TILE_WALL, TILE_COVER)

    def is_wall_pixel(self, px, py):
        return self.is_wall(int(px // TILE_SIZE), int(py // TILE_SIZE))

    def is_wall_pixel_radius(self, px, py, r=10):
        """Check collision with a circular radius."""
        for dx, dy in [(r,0),(-r,0),(0,r),(0,-r),(r,r),(-r,-r),(r,-r),(-r,r)]:
            if self.is_wall_pixel(px+dx, py+dy):
                return True
        return False

    def get_tile(self, tx, ty):
        if 0 <= tx < self.width and 0 <= ty < self.height:
            return self.grid[ty][tx]
        return TILE_WALL

    def find_path_bfs(self, start_px, start_py, target_tile):
        """Find path from pixel coordinates to a specific tile type using BFS."""
        from collections import deque
        start_tx = int(start_px // TILE_SIZE)
        start_ty = int(start_py // TILE_SIZE)
        
        if self.get_tile(start_tx, start_ty) == target_tile:
            return [(start_tx, start_ty)]
            
        queue = deque([(start_tx, start_ty, [])])
        visited = {(start_tx, start_ty)}
        
        while queue:
            tx, ty, path = queue.popleft()
            
            # Check if reached target
            if self.get_tile(tx, ty) == target_tile:
                return path + [(tx, ty)]
                
            # Neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited and self.grid[ny][nx] not in (TILE_WALL, TILE_COVER):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + [(tx, ty)]))
        return None

    def find_path_to_point_list(self, start_px, start_py, target_pixels):
        """Find path from pixel to the nearest of several pixel targets."""
        from collections import deque
        start_tx = int(start_px // TILE_SIZE)
        start_ty = int(start_py // TILE_SIZE)
        
        target_tiles = set()
        for px, py in target_pixels:
            target_tiles.add((int(px // TILE_SIZE), int(py // TILE_SIZE)))
            
        if (start_tx, start_ty) in target_tiles:
            return [(start_tx, start_ty)]
            
        queue = deque([(start_tx, start_ty, [])])
        visited = {(start_tx, start_ty)}
        
        while queue:
            tx, ty, path = queue.popleft()
            
            if (tx, ty) in target_tiles:
                return path + [(tx, ty)]
                
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited and self.grid[ny][nx] not in (TILE_WALL, TILE_COVER):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + [(tx, ty)]))
        return None

    def tunnel_partner(self, tx, ty):
        """Find the other tunnel entrance if standing on one."""
        if self.get_tile(tx, ty) != TILE_TUNNEL:
            return None
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) != (tx, ty) and self.grid[y][x] == TILE_TUNNEL:
                    return (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2)
        return None

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self, screen, camera_x, camera_y):
        screen.blit(self._surface, (-camera_x, -camera_y))
