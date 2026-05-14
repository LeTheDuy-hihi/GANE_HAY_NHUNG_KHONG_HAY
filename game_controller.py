import pygame
from map import Map
from DUYOICHAYDI import Pacman
from ghost import Ghost, GhostState
from particles import SparkParticle, FloatingText
from search_algorithms import pacman_auto_ai_logic
from constants import (PACMAN_START, BLINKY_START, PINKY_START, INKY_START, CLYDE_START, 
                       PACMAN_SPEED, GHOST_SPEED, RED, PINK, INKY_CYAN, ORANGE, 
                       BLINKY_SCATTER, PINKY_SCATTER, INKY_SCATTER, CLYDE_SCATTER, 
                       Direction, WHITE, YELLOW, PEACH, TILE_SIZE, SCORE_HEIGHT_TOP, SCORE_HEIGHT_BOTTOM, WIDTH, HEIGHT)

from menu import MenuManager

class GameController:
    def __init__(self, level=1):
        self.level = level
        if self.level > 1:
            from map_generator import generate_symmetric_map
            import random
            raw_map, starts, w, h = generate_symmetric_map(self.level)
            self.map = Map(raw_map)
            
            # Use starts for initial positions if map generator is used
            px, py = starts["PACMAN"]
            self.pacman_start = (px, py)
        else:
            self.map = Map()
            self.pacman_start = PACMAN_START
        
        self.p_speed = PACMAN_SPEED
        self.g_speed = GHOST_SPEED
        
        self.pacman = Pacman(self.pacman_start[0], self.pacman_start[1], self.p_speed)
        
        # Determine ghost starts based on map type
        if self.level > 1:
            from map_generator import generate_symmetric_map
            raw_map, starts, w, h = generate_symmetric_map(self.level)
            b_start = starts.get("BLINKY", BLINKY_START)
            p_start = starts.get("PINKY", PINKY_START)
            i_start = starts.get("INKY", INKY_START)
            c_start = starts.get("CLYDE", CLYDE_START)
        else:
            b_start = BLINKY_START
            p_start = PINKY_START
            i_start = INKY_START
            c_start = CLYDE_START
            
        import random
        algorithms = ["BFS", "DFS", "A*"]
        
        self.ghosts = [
            Ghost(b_start[0], b_start[1], self.g_speed, RED, "BLINKY", BLINKY_SCATTER, random.choice(algorithms)),
            Ghost(p_start[0], p_start[1], self.g_speed, PINK, "PINKY", PINKY_SCATTER, random.choice(algorithms)),
            Ghost(i_start[0], i_start[1], self.g_speed, INKY_CYAN, "INKY", INKY_SCATTER, random.choice(algorithms)),
            Ghost(c_start[0], c_start[1], self.g_speed, ORANGE, "CLYDE", CLYDE_SCATTER, random.choice(algorithms))
        ]
        
        from constants import PURPLE, GRAY, WHITE, LEMON, GREEN, DARK_GRAY, GOLD, DARK_RED
        
        extra_ghosts_info = [
            ("PATROLLER", PURPLE),
            ("LURKER", GRAY),
            ("MIMIC", WHITE),
            ("TRAPPER", LEMON),
            ("PREDICTOR", GREEN),
            ("TELEPORTER", DARK_GRAY),
            ("COMMANDER", GOLD),
            ("SHADOW", DARK_RED)
        ]
        
        num_ghosts = 4 + (self.level - 1) * 2
        for i in range(min(num_ghosts - 4, len(extra_ghosts_info))):
            name, color = extra_ghosts_info[i]
            scatter = (random.randint(0, self.map.width-1), random.randint(0, self.map.height-1))
            self.ghosts.append(Ghost(p_start[0], p_start[1], self.g_speed, color, name, scatter, random.choice(algorithms)))
            
        self.pacman_history = []
            
        self.particles = []
        self.score = 0
        self.lives = 3
        pygame.font.init()
        self.font = pygame.font.SysFont('segoeui', 36, bold=True)
        self.small_font = pygame.font.SysFont('segoeui', 24)
        self.game_over = False
        self.state_timer = 0
        self.current_ghost_state = GhostState.SCATTER
        
        self.ready_timer = 120 # 2 seconds ready state
        self.is_ready = True
        self.quit_to_menu = False
        self.auto_ai_mode = "OFF"
        self.ghosts_killed = 0
        self.level_complete = False
        self.level_complete_timer = 120
        self.hack_mode = False
        self.pacman_algo = "BFS"

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.quit_to_menu = True
            elif event.key == pygame.K_SPACE:
                if self.auto_ai_mode == "OFF":
                    self.auto_ai_mode = "ON"
                else:
                    self.auto_ai_mode = "OFF"
            elif event.key == pygame.K_h:
                self.hack_mode = not self.hack_mode
                if self.hack_mode:
                    self.auto_ai_mode = "ON"
                    self.pacman.speed = 20
                else:
                    self.pacman.speed = self.p_speed
            elif event.key == pygame.K_a:
                algos = ["BFS", "DFS", "A*"]
                idx = algos.index(self.pacman_algo)
                self.pacman_algo = algos[(idx + 1) % len(algos)]
                
        if self.is_ready or self.game_over:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.pacman.queue_turn(Direction.UP)
            elif event.key == pygame.K_DOWN:
                self.pacman.queue_turn(Direction.DOWN)
            elif event.key == pygame.K_LEFT:
                self.pacman.queue_turn(Direction.LEFT)
            elif event.key == pygame.K_RIGHT:
                self.pacman.queue_turn(Direction.RIGHT)

    def check_collisions(self):
        # Pellet collision
        if (self.pacman.grid_x, self.pacman.grid_y) in self.map.pellets:
            if self.pacman.is_at_center():
                self.map.pellets.remove((self.pacman.grid_x, self.pacman.grid_y))
                self.score += 10
                # Spawn sparks
                for _ in range(3):
                    self.particles.append(SparkParticle(self.pacman.pixel_x, self.pacman.pixel_y, PEACH))

        # Power Pellet collision
        if (self.pacman.grid_x, self.pacman.grid_y) in self.map.power_pellets:
            if self.pacman.is_at_center():
                self.map.power_pellets.remove((self.pacman.grid_x, self.pacman.grid_y))
                self.score += 50
                for _ in range(10):
                    self.particles.append(SparkParticle(self.pacman.pixel_x, self.pacman.pixel_y, YELLOW))
                for ghost in self.ghosts:
                    ghost.set_frightened()
                self.spawn_new_power_pellet()

        # Ghost collision
        for ghost in self.ghosts[:]:
            dist_x = abs(self.pacman.pixel_x - ghost.pixel_x)
            dist_y = abs(self.pacman.pixel_y - ghost.pixel_y)
            if dist_x <= 12 and dist_y <= 12:
                if ghost.state == GhostState.FRIGHTENED or self.hack_mode:
                    self.score += 200
                    # Spawn floating text
                    self.particles.append(FloatingText("200", ghost.pixel_x, ghost.pixel_y, self.small_font, WHITE))
                    for _ in range(8):
                        self.particles.append(SparkParticle(ghost.pixel_x, ghost.pixel_y, WHITE))
                        
                    self.ghosts.remove(ghost)
                    
                    self.ghosts_killed += 1
                    if len(self.ghosts) == 0:
                        self.game_over = True
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.reset_entities()
                        self.is_ready = True
                        self.ready_timer = 120

    def spawn_new_power_pellet(self):
        import random
        empty_spots = []
        for y in range(self.map.height):
            for x in range(self.map.width):
                if getattr(self.map, 'raw_map', None):
                    char = self.map.raw_map[y][x]
                    if char in ['.', 'O']:
                        if (x, y) not in self.map.pellets and (x, y) not in self.map.power_pellets:
                            if (x, y) != (self.pacman.grid_x, self.pacman.grid_y):
                                empty_spots.append((x, y))
                                
        if empty_spots:
            self.map.power_pellets.append(random.choice(empty_spots))

    def reset_entities(self):
        self.pacman.reset_position()
        for ghost in self.ghosts:
            ghost.reset_position()
            ghost.state = self.current_ghost_state

    def update_ghost_states(self):
        self.state_timer += 1
        if self.current_ghost_state == GhostState.SCATTER and self.state_timer > 60 * 7:
            self.current_ghost_state = GhostState.CHASE
            self.state_timer = 0
            for ghost in self.ghosts:
                if ghost.state != GhostState.FRIGHTENED:
                    ghost.state = GhostState.CHASE
        elif self.current_ghost_state == GhostState.CHASE and self.state_timer > 60 * 20:
            self.current_ghost_state = GhostState.SCATTER
            self.state_timer = 0
            for ghost in self.ghosts:
                if ghost.state != GhostState.FRIGHTENED:
                    ghost.state = GhostState.SCATTER

    def update(self):
        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)
                
        if self.level_complete:
            self.level_complete_timer -= 1
            return
            
        if self.game_over:
            return

        if self.is_ready:
            self.ready_timer -= 1
            if self.ready_timer <= 0:
                self.is_ready = False
            return

        self.update_ghost_states()
        
        if self.pacman.is_at_center():
            if self.auto_ai_mode == "ON":
                # Auto AI uses selected logic for best survival and pellet gathering
                ai_dir = pacman_auto_ai_logic((self.pacman.grid_x, self.pacman.grid_y), self.map, self.pacman.direction, self.ghosts, self.pacman.speed, self.g_speed, self.pacman_algo)
                self.pacman.queue_turn(ai_dir)
        self.pacman.update(self.map)
        
        current_pos = (self.pacman.grid_x, self.pacman.grid_y)
        if not self.pacman_history or self.pacman_history[-1] != current_pos:
            self.pacman_history.append(current_pos)
            if len(self.pacman_history) > 5:
                self.pacman_history.pop(0)

        blinky = next((g for g in self.ghosts if g.name == "BLINKY"), None)
        for ghost in self.ghosts:
            ghost.update(self.map, self.pacman, blinky, pacman_history=self.pacman_history, controller=self)
            
        self.check_collisions()
        
        if len(self.map.pellets) == 0:
            self.level_complete = True



    def get_width(self):
        return self.map.width * TILE_SIZE

    def get_height(self):
        return self.map.height * TILE_SIZE + SCORE_HEIGHT_TOP + SCORE_HEIGHT_BOTTOM

    def draw(self, screen):
        self.map.draw(screen)
        
        if not self.is_ready or (self.is_ready and self.ready_timer % 30 > 10):
            self.pacman.draw(screen)
            for ghost in self.ghosts:
                ghost.draw(screen)

        for p in self.particles:
            p.draw(screen)

        # UI Top
        up_text = self.small_font.render(f"MÀN {self.level}", True, WHITE)
        score_val = self.font.render(str(self.score), True, WHITE)
        
        screen.blit(up_text, (self.get_width() // 4 - up_text.get_width() // 2, 5))
        screen.blit(score_val, (self.get_width() // 4 - score_val.get_width() // 2, 25))

        # UI Bottom Lives
        for i in range(self.lives - 1):
            x = 20 + i * 30
            y = self.get_height() - SCORE_HEIGHT_BOTTOM // 2
            radius = TILE_SIZE // 2 - 2
            # Draw simple pacman icon
            pygame.draw.circle(screen, YELLOW, (x, y), radius)
            pygame.draw.polygon(screen, (0,0,0), [(x, y), (x+radius, y-radius), (x+radius, y+radius)])

        if self.auto_ai_mode == "ON":
            text = self.small_font.render(f"AI: BẬT ({self.pacman_algo})", True, (0, 255, 0))
            screen.blit(text, (self.get_width() // 2 - text.get_width() // 2, self.get_height() - SCORE_HEIGHT_BOTTOM // 2 - 10))

        if getattr(self, 'hack_mode', False):
            from constants import RED
            hack_text = self.small_font.render(f"HACK: TỐC ĐỘ BÀN THỜ", True, RED)
            screen.blit(hack_text, (self.get_width() // 2 - hack_text.get_width() // 2, self.get_height() - SCORE_HEIGHT_BOTTOM // 2 + 10))

        if self.is_ready and not self.game_over:
            ready_msg = self.font.render("CHUẨN BỊ!", True, YELLOW)
            screen.blit(ready_msg, (self.get_width() // 2 - ready_msg.get_width() // 2, self.get_height() // 2 + 20))

        if self.level_complete:
            from constants import GREEN
            msg = self.font.render("QUA MÀN!", True, GREEN)
            screen.blit(msg, (self.get_width() // 2 - msg.get_width() // 2, self.get_height() // 2 + 20))
        elif self.game_over:
            if self.lives <= 0:
                msg = self.font.render("THUA RỒI - BẤM ESC ĐỂ THOÁT", True, RED)
            else:
                msg = self.font.render("THẮNG RỒI! BẤM ESC ĐỂ THOÁT", True, PINK)
            screen.blit(msg, (self.get_width() // 2 - msg.get_width() // 2, self.get_height() // 2 + 20))
