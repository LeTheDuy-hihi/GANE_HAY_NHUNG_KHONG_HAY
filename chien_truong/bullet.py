import pygame
import math
from constants import *


class Bullet:
    def __init__(self, x, y, target_x, target_y, is_enemy=False):
        self.x, self.y = x, y
        self.is_enemy = is_enemy
        
        # Calculate angle and velocity
        angle = math.atan2(target_y - y, target_x - x)
        speed = ENEMY_BULLET_SPD if is_enemy else BULLET_SPEED
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.alive = True
        self.damage = 0  # Set by shooter
        
        # Trail history
        self.history = []

    def update(self):
        self.history.append((self.x, self.y))
        if len(self.history) > 3:
            self.history.pop(0)
            
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        
        color = ORANGE if not self.is_enemy else RED
        
        # Draw trail
        if len(self.history) > 1:
            pts = [(int(hx - cam_x), int(hy - cam_y)) for hx, hy in self.history]
            pygame.draw.lines(screen, color, False, pts, 2)
            
        # Draw bullet head
        pygame.draw.circle(screen, WHITE, (sx, sy), 3)
        # Glow
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, 120), (6, 6), 6)
        screen.blit(surf, (sx - 6, sy - 6))


class Grenade:
    def __init__(self, x, y, target_x, target_y):
        self.x, self.y = x, y
        
        # Calculate throw trajectory
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        
        # Cap throw distance
        max_dist = 250
        if dist > max_dist:
            dx = dx / dist * max_dist
            dy = dy / dist * max_dist
            dist = max_dist
            
        # Time to target
        self.duration = int(dist / 5)
        self.timer = 0
        
        self.start_x, self.start_y = x, y
        self.target_x = x + dx
        self.target_y = y + dy
        
        self.fuse_timer = GRENADE_FUSE
        self.exploded = False
        
        # Arc variables
        self.height = 0

    def update(self):
        self.fuse_timer -= 1
        if self.fuse_timer <= 0:
            self.exploded = True
            
        if self.timer < self.duration:
            self.timer += 1
            t = self.timer / self.duration
            # Linear interp
            self.x = self.start_x + (self.target_x - self.start_x) * t
            self.y = self.start_y + (self.target_y - self.start_y) * t
            # Parabolic arc
            self.height = math.sin(t * math.pi) * 40
        else:
            self.height = 0

    def draw(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y - self.height)
        
        # Shadow
        shadow_y = int(self.y - cam_y)
        pygame.draw.ellipse(screen, (20, 20, 20, 100), (sx-6, shadow_y-3, 12, 6))
        
        # Blinking red light
        blink = (self.fuse_timer % 10) < 5
        color = RED if blink else DARK_GREEN if 'DARK_GREEN' in globals() else (20, 80, 20)
        
        pygame.draw.circle(screen, color, (sx, sy), 5)
        pygame.draw.circle(screen, BLACK, (sx, sy), 5, 1)

class BulletManager:
    def __init__(self):
        self.bullets = []
        self.grenades = []

    def add_bullet(self, x, y, target_x, target_y, is_enemy=False, damage=10):
        b = Bullet(x, y, target_x, target_y, is_enemy)
        b.damage = damage
        self.bullets.append(b)

    def add_grenade(self, x, y, target_x, target_y):
        self.grenades.append(Grenade(x, y, target_x, target_y))

    def update(self, game_map, effect_manager, sound_manager):
        explosions = []
        
        # Update bullets
        for b in self.bullets:
            b.update()
            # Map collision
            if game_map.is_wall_pixel(b.x, b.y):
                # Check for barrel
                tx, ty = int(b.x // TILE_SIZE), int(b.y // TILE_SIZE)
                if game_map.get_tile(tx, ty) == TILE_BARREL:
                    game_map.grid[ty][tx] = TILE_EMPTY
                    # Re-bake the surface would be slow, so we just clear it from grid 
                    # and rely on the explosion effect to hide the "disappearance"
                    # Actually, a better way is to handle barrel as an entity, but for now:
                    explosions.append((b.x, b.y))
                    effect_manager.add_explosion(b.x, b.y, GRENADE_RADIUS * 1.2)
                    sound_manager.play('explosion')
                
                b.alive = False
                effect_manager.add_bullet_impact(b.x, b.y)
                
        self.bullets = [b for b in self.bullets if b.alive]
        
        # Update grenades
        for g in self.grenades:
            g.update()
            if g.exploded:
                explosions.append((g.x, g.y))
                effect_manager.add_explosion(g.x, g.y, GRENADE_RADIUS)
                sound_manager.play('explosion')
                
        self.grenades = [g for g in self.grenades if not g.exploded]
        
        return explosions

    def draw(self, screen, cam_x, cam_y):
        for g in self.grenades:
            g.draw(screen, cam_x, cam_y)
        for b in self.bullets:
            b.draw(screen, cam_x, cam_y)
