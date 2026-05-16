import pygame
import sys
import math
from constants import *
from map_gen import GameMap
from player import Player
from enemy import EnemyManager
from bullet import BulletManager
from effects import EffectManager
from items import ItemManager
from sound_manager import sound_manager
from hud import HUD
from upgrade_menu import UpgradeMenu
from menu import MainMenu
from video_player import play_video


class GameApp:
    def __init__(self):
        pygame.init()
        # Cửa sổ game 1200x800
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Fonts
        pygame.font.init()
        # Dùng font segoe ui hoặc arial để hỗ trợ tốt tiếng Việt
        self.font_large = pygame.font.SysFont("segoeui", 32, bold=True)
        self.font_title = pygame.font.SysFont("segoeui", 64, bold=True)
        self.font_normal = pygame.font.SysFont("segoeui", 24, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 16, bold=True)
        
        # Systems
        self.menu = MainMenu(self.font_title, self.font_normal, self.font_small)
        self.upgrade_menu = UpgradeMenu(self.font_title, self.font_normal, self.font_small)
        self.hud = HUD(self.font_large, self.font_small)
        
        self.state = "MENU" # MENU, GAME, UPGRADE, GAMEOVER, WIN
        self.level = 1
        
        # Game objects
        self.player = None
        self.game_map = None
        self.enemy_manager = None
        self.bullet_manager = None
        self.effect_manager = None
        self.item_manager = None
        
        # Raw scancode tracking (bypass Unikey)
        self.raw_keys = {
            "W": False, "A": False, "S": False, "D": False,
            "Q": False, "R": False, "G": False, "LShift": False
        }
        
        # Fog of War Setup (Balanced Darkness)
        self.view_radius = 250
        self.fog_gradient = pygame.Surface((self.view_radius * 2, self.view_radius * 2), pygame.SRCALPHA)
        for r in range(self.view_radius, 0, -2):
            # Softer gradient for a "moody" look
            alpha = int(225 * (r / self.view_radius)**1.4)
            pygame.draw.circle(self.fog_gradient, (0, 0, 0, alpha), (self.view_radius, self.view_radius), r)
            
        # Camera
        self.cam_x, self.cam_y = 0, 0
        
        # CRT Overlay Surface
        self.crt_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for y in range(0, SCREEN_H, 2):
            pygame.draw.line(self.crt_surf, (0, 0, 0, 40), (0, y), (SCREEN_W, y))

    def start_game(self, new_campaign=True):
        if new_campaign:
            self.level = 1
            # Initial player
            self.player = Player(0, 0)
            
        # Init level
        self.game_map = GameMap(self.level)
        self.player.x, self.player.y = self.game_map.player_spawn
        
        self.bullet_manager = BulletManager()
        self.effect_manager = EffectManager()
        self.item_manager = ItemManager(self.game_map.item_spawns, self.level)
        self.enemy_manager = EnemyManager(self.game_map.enemy_spawns, self.level)
        
        self.state = "GAME"

    def run(self):
        # 1. Play Intro Video first (using absolute path)
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.join(base_dir, "ANH", "video_intro.mp4")
        
        play_video(self.screen, video_path)
        
        # 2. Start Background Music after Video
        sound_manager.play_bg_music()
        
        # 3. Enter Main Game Loop
        while True:
            self.handle_events()
            self.update()
            self.draw()
            # Standard tick removed from here, handled in update for slow-mo

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Track raw scancodes for WASD (bypass Unikey)
            if event.type == pygame.KEYDOWN:
                scancode = getattr(event, 'scancode', None)
                # Scancode-based (bypass Unikey)
                if scancode == 26: self.raw_keys["W"] = True
                elif scancode == 4: self.raw_keys["A"] = True
                elif scancode == 22: self.raw_keys["S"] = True
                elif scancode == 7: self.raw_keys["D"] = True
                elif scancode == 20: self.raw_keys["Q"] = True
                elif scancode == 21: self.raw_keys["R"] = True
                elif scancode == 10: self.raw_keys["G"] = True
                elif scancode in [225, 229]: self.raw_keys["LShift"] = True
                # Fallback: also track via event.key
                if event.key == pygame.K_w: self.raw_keys["W"] = True
                elif event.key == pygame.K_a: self.raw_keys["A"] = True
                elif event.key == pygame.K_s: self.raw_keys["S"] = True
                elif event.key == pygame.K_d: self.raw_keys["D"] = True
                elif event.key == pygame.K_q: self.raw_keys["Q"] = True
                elif event.key == pygame.K_r: self.raw_keys["R"] = True
                elif event.key == pygame.K_g: self.raw_keys["G"] = True
                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT): self.raw_keys["LShift"] = True
                
            elif event.type == pygame.KEYUP:
                scancode = getattr(event, 'scancode', None)
                if scancode == 26: self.raw_keys["W"] = False
                elif scancode == 4: self.raw_keys["A"] = False
                elif scancode == 22: self.raw_keys["S"] = False
                elif scancode == 7: self.raw_keys["D"] = False
                elif scancode == 20: self.raw_keys["Q"] = False
                elif scancode == 21: self.raw_keys["R"] = False
                elif scancode == 10: self.raw_keys["G"] = False
                elif scancode in [225, 229]: self.raw_keys["LShift"] = False
                if event.key == pygame.K_w: self.raw_keys["W"] = False
                elif event.key == pygame.K_a: self.raw_keys["A"] = False
                elif event.key == pygame.K_s: self.raw_keys["S"] = False
                elif event.key == pygame.K_d: self.raw_keys["D"] = False
                elif event.key == pygame.K_q: self.raw_keys["Q"] = False
                elif event.key == pygame.K_r: self.raw_keys["R"] = False
                elif event.key == pygame.K_g: self.raw_keys["G"] = False
                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT): self.raw_keys["LShift"] = False
                
            if self.state == "GAME":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    self.menu.state = "MAIN"
                    
            elif self.state == "MENU":
                action = self.menu.handle_input(event)
                if action == "QUIT":
                    pygame.quit()
                    sys.exit()
                elif action == "START":
                    self.start_game(new_campaign=True)
                    
            elif self.state == "UPGRADE":
                done = self.upgrade_menu.handle_input(event, self.player)
                if done:
                    self.level += 1
                    if self.level > MAX_LEVEL:
                        self.state = "WIN"
                    else:
                        self.start_game(new_campaign=False)
                        
            elif self.state in ("GAMEOVER", "WIN"):
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                    self.state = "MENU"
                    self.menu.state = "MAIN"

    def update(self):
        if self.state != "GAME":
            self.clock.tick(FPS)
            
        if self.state == "GAME":
            # Input
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            
            # Pass raw_keys to player instead of just keys
            keys_dict = {"pygame_keys": keys, "raw_keys": self.raw_keys}
            
            # Update systems
            self.player.update(keys_dict, mouse_pos, self.cam_x, self.cam_y, 
                               self.game_map, self.bullet_manager, 
                               self.effect_manager, sound_manager)
            
            self.enemy_manager.update(self.player, self.game_map, 
                                      self.bullet_manager, self.effect_manager, 
                                      sound_manager)
            
            self.bullet_manager.update(self.game_map, self.effect_manager, sound_manager)
            self.item_manager.update()
            self.effect_manager.update()
            self.effect_manager.update_ambient(self.cam_x, self.cam_y)
            
            # ── Slow Motion Update ──────────────────────────────────────────
            if self.player.is_focusing:
                self.clock.tick(int(FPS * TIME_SLOW_FACTOR))
            else:
                self.clock.tick(FPS)
            # Override standard tick at end of loop, so we remove it from there
            
            # Check bullet collisions with entities
            for b in self.bullet_manager.bullets:
                if b.is_enemy:
                    # Check player
                    dist = math.hypot(b.x - self.player.x, b.y - self.player.y)
                    if dist < self.player.radius + 2:
                        self.player.take_damage(b.damage, self.effect_manager, sound_manager)
                        b.alive = False
                else:
                    # Check enemies
                    for e in self.enemy_manager.enemies:
                        dist = math.hypot(b.x - e.x, b.y - e.y)
                        if dist < e.radius + 2:
                            e.take_damage(b.damage, self.effect_manager, sound_manager)
                            b.alive = False
                            break
                            
            # Check explosion damage
            for ex_x, ex_y in [g for g in self.bullet_manager.grenades if getattr(g, 'exploded', False)]:
                # Handle grenade explosion damage inside bullet_manager update, 
                # but we need to deal damage here. Let's do it via effect manager's explosions briefly
                pass
                
            for exp in self.effect_manager.explosions:
                if exp.lifetime == exp.max_lt - 1: # Just spawned
                    # Player
                    dist = math.hypot(exp.x - self.player.x, exp.y - self.player.y)
                    if dist < exp.radius:
                        dmg = int(GRENADE_DAMAGE * (1 - dist/exp.radius))
                        self.player.take_damage(dmg, self.effect_manager, sound_manager)
                    # Enemies
                    for e in self.enemy_manager.enemies:
                        dist = math.hypot(exp.x - e.x, exp.y - e.y)
                        if dist < exp.radius:
                            dmg = int(GRENADE_DAMAGE * (1 - dist/exp.radius))
                            e.take_damage(dmg, self.effect_manager, sound_manager)

            # Check items
            picked = self.item_manager.check_pickup(self.player)
            for item in picked:
                sound_manager.play('pickup')
                heal, ammo, armor, gre = item.get_effect()
                self.player.heal(heal)
                self.player.ammo += ammo
                self.player.max_armor += armor
                self.player.armor += armor
                self.player.grenades += gre
                
            # Update camera
            target_cx = self.player.x - SCREEN_W / 2
            target_cy = self.player.y - SCREEN_H / 2
            # Clamp to map bounds
            target_cx = max(0, min(target_cx, self.game_map.pixel_w - SCREEN_W))
            target_cy = max(0, min(target_cy, self.game_map.pixel_h - SCREEN_H))
            
            # Smooth follow
            self.cam_x += (target_cx - self.cam_x) * 0.1
            self.cam_y += (target_cy - self.cam_y) * 0.1
            
            # Check level complete (Touch exit door)
            px, py = int(self.player.x // TILE_SIZE), int(self.player.y // TILE_SIZE)
            if self.game_map.get_tile(px, py) == TILE_EXIT:
                sound_manager.play('pickup')
                self.upgrade_menu.roll_choices()
                self.state = "UPGRADE"
                
            # Check game over
            if self.player.hp <= 0:
                self.state = "GAMEOVER"

    def draw(self):
        if self.state == "MENU":
            self.menu.draw(self.screen)
            
        elif self.state in ("GAME", "UPGRADE", "GAMEOVER", "WIN"):
            self.screen.fill(BLACK)
            
            # Apply Screen Shake to Camera
            cam_draw_x, cam_draw_y = self.effect_manager.shake.apply(self.cam_x, self.cam_y)
            
            # Draw game objects
            self.game_map.draw(self.screen, cam_draw_x, cam_draw_y)
            self.item_manager.draw(self.screen, cam_draw_x, cam_draw_y)
            self.enemy_manager.draw(self.screen, cam_draw_x, cam_draw_y)
            self.player.draw(self.screen, cam_draw_x, cam_draw_y)
            self.bullet_manager.draw(self.screen, cam_draw_x, cam_draw_y)
            self.effect_manager.draw(self.screen, cam_draw_x, cam_draw_y)
            
            # ── BFS Pathfinding Line (The Quest Path) ──────────────────────────
            # Only calculate/draw occasionally or if level is not cleared
            path = self.game_map.find_path_bfs(self.player.x, self.player.y, TILE_EXIT)
            if path and len(path) > 1:
                points = []
                for tx, ty in path:
                    px = tx * TILE_SIZE + TILE_SIZE // 2 - cam_draw_x
                    py = ty * TILE_SIZE + TILE_SIZE // 2 - cam_draw_y
                    points.append((px, py))
                
                # Draw neon path line with pulse effect
                pulse = int(100 + 50 * math.sin(pygame.time.get_ticks() / 200))
                color = (0, 255, 255, pulse) # Cyan neon
                
                if len(points) >= 2:
                    path_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                    pygame.draw.lines(path_surf, color, False, points, 3)
                    self.screen.blit(path_surf, (0, 0))
            
            # ── Emergency Paths (Health/Ammo) ──────────────────────────────────
            emergency_paths = []
            
            # 1. Health Path (if < 50%)
            if self.player.hp < self.player.max_hp * 0.5:
                h_targets = [(item.x, item.y) for item in self.item_manager.items if item.type == ITEM_HEALTH]
                if h_targets:
                    h_path = self.game_map.find_path_to_point_list(self.player.x, self.player.y, h_targets)
                    if h_path: emergency_paths.append((h_path, (255, 50, 50))) # Bright Red
            
            # 2. Ammo Path (if 0 ammo)
            if self.player.ammo <= 0:
                a_targets = [(item.x, item.y) for item in self.item_manager.items if item.type == ITEM_AMMO]
                if a_targets:
                    a_path = self.game_map.find_path_to_point_list(self.player.x, self.player.y, a_targets)
                    if a_path: emergency_paths.append((a_path, (255, 200, 0))) # Bright Orange/Yellow
                    
            for path, color in emergency_paths:
                if path and len(path) > 1:
                    pts = []
                    for tx, ty in path:
                        pts.append((tx * TILE_SIZE + TILE_SIZE // 2 - cam_draw_x, 
                                    ty * TILE_SIZE + TILE_SIZE // 2 - cam_draw_y))
                    
                    # Draw with pulse and glow
                    pulse = int(150 + 100 * math.sin(pygame.time.get_ticks() / 150))
                    path_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                    # Glow effect
                    pygame.draw.lines(path_surf, (*color, pulse // 4), False, pts, 8)
                    # Core line
                    pygame.draw.lines(path_surf, (*color, pulse), False, pts, 3)
                    self.screen.blit(path_surf, (0, 0))
            # ──────────────────────────────────────────────────────────────────
            
            # ── Fog of War with Flashlight Effect ──────────────────────────────────
            fog_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            fog_surf.fill((0, 0, 0, 160)) # Reduced darkness for better visibility
            
            player_screen_x = int(self.player.x - cam_draw_x)
            player_screen_y = int(self.player.y - cam_draw_y)
            
            # 1. Draw small ambient circle around player
            ambient_radius = 150 # Increased radius
            ambient_grad = pygame.Surface((ambient_radius * 2, ambient_radius * 2), pygame.SRCALPHA)
            for r in range(ambient_radius, 0, -4):
                alpha = int(255 * (r / ambient_radius)**1.2)
                pygame.draw.circle(ambient_grad, (0, 0, 0, alpha), (ambient_radius, ambient_radius), r)
            fog_surf.blit(ambient_grad, (player_screen_x - ambient_radius, player_screen_y - ambient_radius), special_flags=pygame.BLEND_RGBA_MIN)
            
            # 2. Draw Flashlight Cone pointing to mouse
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - player_screen_y, mx - player_screen_x)
            
            cone_length = 500
            cone_spread = 0.5 # radians (approx 30 degrees)
            
            # Create a cone mask
            cone_points = [
                (player_screen_x, player_screen_y),
                (player_screen_x + math.cos(angle - cone_spread) * cone_length, player_screen_y + math.sin(angle - cone_spread) * cone_length),
                (player_screen_x + math.cos(angle) * cone_length * 1.1, player_screen_y + math.sin(angle) * cone_length * 1.1),
                (player_screen_x + math.cos(angle + cone_spread) * cone_length, player_screen_y + math.sin(angle + cone_spread) * cone_length)
            ]
            
            # Draw several overlapping triangles with decreasing alpha for a soft cone
            for i in range(10, 0, -1):
                alpha = int(255 * (i / 10))
                # Slightly shrink or just use alpha
                pygame.draw.polygon(fog_surf, (0, 0, 0, alpha), cone_points, 0)
                # Actually, BLEND_RGBA_MIN with black makes it transparent
            
            # Re-blit the ambient to ensure center is clear
            fog_surf.blit(ambient_grad, (player_screen_x - ambient_radius, player_screen_y - ambient_radius), special_flags=pygame.BLEND_RGBA_MIN)
            
            # Final blit to screen
            self.screen.blit(fog_surf, (0, 0))
            # ──────────────────────────────────────────────────────────────────────
            
            # Draw HUD
            self.hud.draw(self.screen, self.player, self.level, self.game_map, self.enemy_manager.enemies)
            
            if self.state == "UPGRADE":
                self.upgrade_menu.draw(self.screen)
                
            elif self.state == "GAMEOVER":
                # Dark overlay
                surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                surf.fill((100, 0, 0, 150))
                self.screen.blit(surf, (0, 0))
                
                txt = self.font_title.render("NHIỆM VỤ THẤT BẠI", True, WHITE)
                sub = self.font_normal.render("Nhấn SPACE để về Menu", True, YELLOW)
                self.screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, SCREEN_H//2 - 50))
                self.screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, SCREEN_H//2 + 20))
                
            elif self.state == "WIN":
                surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                surf.fill((0, 50, 0, 150))
                self.screen.blit(surf, (0, 0))
                
                txt = self.font_title.render("CHIẾN THẮNG!", True, GOLD)
                sub1 = self.font_normal.render("Bạn đã hoàn thành xuất sắc nhiệm vụ.", True, WHITE)
                sub2 = self.font_normal.render("Nhấn SPACE để về Menu", True, YELLOW)
                self.screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, SCREEN_H//2 - 80))
                self.screen.blit(sub1, (SCREEN_W//2 - sub1.get_width()//2, SCREEN_H//2 + 10))
                self.screen.blit(sub2, (SCREEN_W//2 - sub2.get_width()//2, SCREEN_H//2 + 50))
                
            # ── CRT Overlay ───────────────────────────────────────────────────
            self.screen.blit(self.crt_surf, (0, 0))
            # ──────────────────────────────────────────────────────────────────
                
        pygame.display.flip()

if __name__ == "__main__":
    app = GameApp()
    app.run()
