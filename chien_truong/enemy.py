import pygame
import math
import random
from constants import *
import ai_logic

class Enemy:
    def __init__(self, x, y, enemy_type, level=1):
        self.x, self.y = float(x), float(y)
        self.type = enemy_type
        self.level = level
        
        # Difficulty scaling factors
        hp_scale = 1.0 + (level - 1) * 0.15
        dmg_scale = 1.0 + (level - 1) * 0.1
        spd_scale = 1.0 + (level - 1) * 0.05
        
        if enemy_type == "patrol":
            self.hp = PATROL_HP * hp_scale
            self.speed = PATROL_SPEED * spd_scale
            self.damage = PATROL_DAMAGE * dmg_scale
            self.range = PATROL_RANGE
            self.max_cooldown = PATROL_COOLDOWN
            self.color = PATROL_COLOR
        elif enemy_type == "sniper":
            self.hp = SNIPER_HP * hp_scale
            self.speed = SNIPER_SPEED * spd_scale
            self.damage = SNIPER_DAMAGE * dmg_scale
            self.range = SNIPER_RANGE
            self.max_cooldown = SNIPER_COOLDOWN
            self.color = SNIPER_COLOR
        elif enemy_type == "assault":
            self.hp = ASSAULT_HP * hp_scale
            self.speed = ASSAULT_SPEED * spd_scale
            self.damage = ASSAULT_DAMAGE * dmg_scale
            self.range = ASSAULT_RANGE
            self.max_cooldown = ASSAULT_COOLDOWN
            self.color = ASSAULT_COLOR
        else: # boss
            # Bosses scale even harder
            self.hp = BOSS_HP * (1.0 + (level-1)*0.5)
            self.speed = BOSS_SPEED * (1.0 + (level-1)*0.08)
            self.damage = BOSS_DAMAGE * (1.0 + (level-1)*0.2)
            self.range = BOSS_RANGE + (level * 20)
            self.max_cooldown = max(20, BOSS_COOLDOWN - (level * 2))
            self.color = BOSS_COLOR
            self.skill_timer = 0
            self.skill_mode = 0 # 0: Normal, 1: Circular, 2: Spiral, 3: Rapid
            
        self.max_hp = self.hp
        self.cooldown = random.randint(0, int(self.max_cooldown))
        self.alive = True
        self.radius = 12
        if self.type == "boss":
            self.radius = 20 # Bosses are bigger
            
        self.angle = 0.0
        self.path = []
        self.path_timer = 0
        
        # DFS specific
        self.visited_tiles = set()

    def update(self, player, game_map, bullet_manager, effect_manager, sound_manager):
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
        has_los = ai_logic.has_line_of_sight(self.x, self.y, player.x, player.y, game_map)
        
        # ── Pathfinding / AI ────────────────────────────────────────────────
        self.path_timer -= 1
        
        if self.type == "patrol":
            if not has_los or dist_to_player > self.range:
                if self.path_timer <= 0:
                    self.path_timer = 20
                    nx, ny = ai_logic.dfs_patrol_step(self.x, self.y, self.visited_tiles, game_map)
                    tx, ty = ai_logic.tile(nx, ny)
                    self.visited_tiles.add((tx, ty))
                    if len(self.visited_tiles) > 30:
                        self.visited_tiles.clear()
                    self.path = [(nx, ny)]
            else:
                self.path = [] # Stop and shoot
                
        elif self.type == "sniper":
            if self.path_timer <= 0:
                self.path_timer = 30
                # Try to maintain optimal distance
                if dist_to_player < 200:
                    # Run away
                    self.path = ai_logic.astar_path(self.x, self.y, self.x + (self.x - player.x), self.y + (self.y - player.y), game_map)
                elif not has_los or dist_to_player > self.range:
                    self.path = ai_logic.astar_path(self.x, self.y, player.x, player.y, game_map)
                else:
                    self.path = []
                    
        elif self.type == "assault":
            if self.path_timer <= 0:
                self.path_timer = 15
                if dist_to_player > 50:
                    self.path = ai_logic.bfs_path(self.x, self.y, player.x, player.y, game_map)
                else:
                    self.path = []
                    
        elif self.type == "boss":
            if self.path_timer <= 0:
                self.path_timer = 10
                pred_x, pred_y = ai_logic.predict_player_pos(player, 30)
                self.path = ai_logic.bfs_path(self.x, self.y, pred_x, pred_y, game_map)

        # ── Movement ────────────────────────────────────────────────────────
        if self.path:
            tx, ty = self.path[0]
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist < 5:
                self.path.pop(0)
            else:
                vx = dx / dist * self.speed
                vy = dy / dist * self.speed
                
                if not game_map.is_wall_pixel_radius(self.x + vx, self.y, self.radius):
                    self.x += vx
                if not game_map.is_wall_pixel_radius(self.x, self.y + vy, self.radius):
                    self.y += vy
                    
                self.angle = math.atan2(dy, dx)
        
        # ── Shooting ────────────────────────────────────────────────────────
        if has_los and dist_to_player <= self.range:
            self.angle = math.atan2(player.y - self.y, player.x - self.x)
            
            self.cooldown -= 1
            if self.cooldown <= 0:
                self.cooldown = self.max_cooldown
                self.shoot(player, bullet_manager, effect_manager, sound_manager)

    def shoot(self, player, bullet_manager, effect_manager, sound_manager):
        sound = 'sniper_shot' if self.type == 'sniper' else 'enemy_shot'
        sound_manager.play(sound)
        
        nx = math.cos(self.angle)
        ny = math.sin(self.angle)
        mx = self.x + nx * (self.radius + 5)
        my = self.y + ny * (self.radius + 5)
        
        if self.type != "boss":
            spread = random.uniform(-0.1, 0.1)
            if self.type == "sniper": spread = 0
            fa = self.angle + spread
            tx = mx + math.cos(fa) * 100
            ty = my + math.sin(fa) * 100
            bullet_manager.add_bullet(mx, my, tx, ty, is_enemy=True, damage=self.damage)
            effect_manager.add_muzzle_flash(mx, my, self.angle)
        else:
            # Boss Logic: Multi-Skill System
            self.skill_timer += 1
            if self.skill_timer > 60: # Change skill every 60 frames
                self.skill_timer = 0
                self.skill_mode = random.randint(0, 3)
            
            if self.skill_mode == 0: # Spread shot (Triple)
                for s in [-0.2, 0, 0.2]:
                    fa = self.angle + s
                    tx = mx + math.cos(fa) * 100
                    ty = my + math.sin(fa) * 100
                    bullet_manager.add_bullet(mx, my, tx, ty, is_enemy=True, damage=self.damage)
            
            elif self.skill_mode == 1: # Circular Burst
                n = 8 + (self.level // 2)
                for i in range(n):
                    fa = (math.pi * 2 / n) * i
                    tx = mx + math.cos(fa) * 100
                    ty = my + math.sin(fa) * 100
                    bullet_manager.add_bullet(mx, my, tx, ty, is_enemy=True, damage=self.damage * 0.7)
            
            elif self.skill_mode == 2: # Spiral Shot
                fa = (pygame.time.get_ticks() / 100) % (math.pi * 2)
                for i in range(2):
                    fa2 = fa + i * math.pi
                    tx = mx + math.cos(fa2) * 100
                    ty = my + math.sin(fa2) * 100
                    bullet_manager.add_bullet(mx, my, tx, ty, is_enemy=True, damage=self.damage * 0.8)
            
            elif self.skill_mode == 3: # Rapid Fire
                self.cooldown = 3 # Very short cooldown
                fa = self.angle + random.uniform(-0.1, 0.1)
                tx = mx + math.cos(fa) * 100
                ty = my + math.sin(fa) * 100
                bullet_manager.add_bullet(mx, my, tx, ty, is_enemy=True, damage=self.damage * 0.5)

            effect_manager.add_muzzle_flash(mx, my, self.angle)

    def take_damage(self, amount, effect_manager, sound_manager):
        self.hp -= amount
        effect_manager.add_blood(self.x, self.y)
        if self.hp <= 0:
            self.alive = False
            sound_manager.play('death')

    def draw(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        
        # Shadow
        pygame.draw.circle(screen, (20, 20, 20, 100), (sx, sy+4), self.radius)
        
        # Body
        pygame.draw.circle(screen, DARK_GRAY, (sx, sy), self.radius)
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius-2)
        
        # Gun
        nx = math.cos(self.angle)
        ny = math.sin(self.angle)
        gx = sx + nx * (self.radius + 6)
        gy = sy + ny * (self.radius + 6)
        pygame.draw.line(screen, (50, 50, 50), (sx, sy), (gx, gy), 3)
        
        # Boss glow and HUD
        if self.type == "boss":
            # Pulsing glow
            pulse = int(50 + 30 * math.sin(pygame.time.get_ticks() / 150))
            surf = pygame.Surface((self.radius*6, self.radius*6), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*BOSS_COLOR, pulse), (self.radius*3, self.radius*3), self.radius*2.5)
            screen.blit(surf, (sx - self.radius*3, sy - self.radius*3))
            
            # HP Bar (Modern)
            bar_w = 60
            bar_h = 6
            bx = sx - bar_w//2
            by = sy - self.radius - 12
            pct = max(0, self.hp / self.max_hp)
            pygame.draw.rect(screen, (30, 30, 30), (bx-1, by-1, bar_w+2, bar_h+2))
            pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
            pygame.draw.rect(screen, LIME, (bx, by, int(bar_w*pct), bar_h))
            
            # Skill Indicator
            skill_names = ["SPREAD", "BURST", "SPIRAL", "RAPID"]
            font = pygame.font.SysFont("arial", 12, bold=True)
            txt = font.render(skill_names[self.skill_mode], True, WHITE)
            screen.blit(txt, (sx - txt.get_width()//2, by - 14))


class EnemyManager:
    def __init__(self, map_spawns, level=1):
        self.enemies = []
        
        types = ["patrol", "sniper", "assault"]
        weights = [0.5, 0.2, 0.3]
        
        for tx, ty in map_spawns:
            etype = random.choices(types, weights=weights)[0]
            self.enemies.append(Enemy(tx, ty, etype, level))
            
        # Add BOSS on EVERY level
        if map_spawns:
            # Spawn boss at the last spawn point (usually near exit)
            bx, by = map_spawns[-1]
            self.enemies.append(Enemy(bx, by, "boss", level))

    def update(self, player, game_map, bullet_manager, effect_manager, sound_manager):
        for e in self.enemies:
            e.update(player, game_map, bullet_manager, effect_manager, sound_manager)
            
        self.enemies = [e for e in self.enemies if e.alive]

    def draw(self, screen, cam_x, cam_y):
        for e in self.enemies:
            e.draw(screen, cam_x, cam_y)
