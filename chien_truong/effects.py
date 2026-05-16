import pygame
import math
import random
from constants import *


class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration

    def update(self):
        if self.duration > 0:
            self.offset_x = random.randint(-self.intensity, self.intensity)
            self.offset_y = random.randint(-self.intensity, self.intensity)
            self.duration -= 1
        else:
            self.offset_x = 0
            self.offset_y = 0

    def apply(self, x, y):
        return x + self.offset_x, y + self.offset_y


class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        return self.lifetime > 0

    @property
    def alpha(self):
        return int(255 * self.lifetime / self.max_lifetime)

    def draw(self, screen, cam_x, cam_y):
        if self.size < 1:
            return
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, self.alpha), (self.size, self.size), self.size)
        screen.blit(surf, (sx - self.size, sy - self.size))


class FireParticle(Particle):
    def __init__(self, x, y):
        vx = random.uniform(-1.2, 1.2)
        vy = random.uniform(-2.5, -0.5)
        color = random.choice([ORANGE, (255,100,0), YELLOW, RED])
        size = random.randint(4, 9)
        super().__init__(x, y, vx, vy, color, size, random.randint(20, 40))

    def update(self):
        self.size = max(0, self.size - 0.15)
        return super().update()


class SmokeParticle(Particle):
    def __init__(self, x, y):
        vx = random.uniform(-0.6, 0.6)
        vy = random.uniform(-1.5, -0.3)
        c = random.randint(80, 140)
        super().__init__(x, y, vx, vy, (c,c,c), random.randint(5, 12), random.randint(30, 60))

    def update(self):
        self.size = min(self.size + 0.08, 14)
        return super().update()


class BloodParticle(Particle):
    def __init__(self, x, y, angle=None):
        if angle is None:
            angle = random.uniform(0, math.pi*2)
        spd = random.uniform(1.5, 5.0)
        super().__init__(x, y,
                         math.cos(angle)*spd, math.sin(angle)*spd,
                         random.choice([RED, DARK_RED, (180,10,10)]),
                         random.randint(2, 5), random.randint(20, 45))

    def update(self):
        self.vy += 0.15  # gravity
        return super().update()


class TrailParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, 0, 0, color, random.randint(2, 4), 10)

    def update(self):
        self.size *= 0.8
        return super().update()


class ShellCasing(Particle):
    def __init__(self, x, y, angle):
        spd = random.uniform(2, 4)
        side_angle = angle + math.pi/2 + random.uniform(-0.5, 0.5)
        vx = math.cos(side_angle) * spd
        vy = math.sin(side_angle) * spd
        super().__init__(x, y, vx, vy, GOLD, 2, 40)

    def update(self):
        self.vx *= 0.95
        self.vy *= 0.95
        self.vy += 0.2 # gravity
        return super().update()


class MuzzleFlash:
    def __init__(self, x, y, angle):
        self.x, self.y = x, y
        self.angle = angle
        self.lifetime = 5
        self.size = random.randint(10, 18)

    def update(self):
        self.lifetime -= 1
        self.size = max(0, self.size - 2)
        return self.lifetime > 0

    def draw(self, screen, cam_x, cam_y):
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        for r in [self.size, self.size//2]:
            surf = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            alpha = int(200 * self.lifetime / 5)
            pygame.draw.circle(surf, (255, 240, 180, alpha), (r+1, r+1), r)
            screen.blit(surf, (sx - r - 1, sy - r - 1))


class ExplosionEffect:
    def __init__(self, x, y, radius):
        self.x, self.y = x, y
        self.radius = radius
        self.lifetime = 45
        self.max_lt = 45
        self.particles = []
        # Fire core
        for _ in range(30):
            self.particles.append(FireParticle(x + random.uniform(-10,10),
                                               y + random.uniform(-10,10)))
        # Smoke ring
        for _ in range(20):
            angle = random.uniform(0, math.pi*2)
            dist = random.uniform(radius*0.3, radius*0.8)
            self.particles.append(SmokeParticle(
                x + math.cos(angle)*dist, y + math.sin(angle)*dist))
        # Debris
        for _ in range(15):
            angle = random.uniform(0, math.pi*2)
            spd = random.uniform(3, 8)
            c = random.choice([BROWN, DARK_GRAY, (60,40,20)])
            p = Particle(x, y, math.cos(angle)*spd, math.sin(angle)*spd,
                         c, random.randint(2,5), 40)
            self.particles.append(p)

    def update(self):
        self.lifetime -= 1
        self.particles = [p for p in self.particles if p.update()]
        return self.lifetime > 0

    def draw(self, screen, cam_x, cam_y):
        for p in self.particles:
            p.draw(screen, cam_x, cam_y)
        # Shockwave ring
        prog = 1 - self.lifetime / self.max_lt
        if prog < 0.4:
            r = int(self.radius * prog / 0.4)
            alpha = int(200 * (1 - prog/0.4))
            sx, sy = int(self.x - cam_x), int(self.y - cam_y)
            if 0 < r < 300:
                surf = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255,200,100,alpha), (r+2,r+2), r, 3)
                screen.blit(surf, (sx-r-2, sy-r-2))


class EffectManager:
    def __init__(self):
        self.particles  = []
        self.flashes    = []
        self.explosions = []
        self.shake      = ScreenShake()

    def add_trail(self, x, y, color):
        self.particles.append(TrailParticle(x, y, color))

    def add_shell(self, x, y, angle):
        self.particles.append(ShellCasing(x, y, angle))

    def add_blood(self, x, y, count=8, angle=None):
        for _ in range(count):
            a = angle + random.uniform(-0.8, 0.8) if angle else None
            self.particles.append(BloodParticle(x, y, a))

    def add_muzzle_flash(self, x, y, angle):
        self.flashes.append(MuzzleFlash(x, y, angle))

    def add_smoke(self, x, y, count=3):
        for _ in range(count):
            self.particles.append(SmokeParticle(
                x+random.uniform(-5,5), y+random.uniform(-5,5)))

    def add_fire(self, x, y, count=5):
        for _ in range(count):
            self.particles.append(FireParticle(x+random.uniform(-8,8), y))

    def add_explosion(self, x, y, radius=90):
        self.explosions.append(ExplosionEffect(x, y, radius))

    def add_bullet_impact(self, x, y):
        for _ in range(5):
            angle = random.uniform(0, math.pi*2)
            spd = random.uniform(1, 3)
            c = random.choice([GRAY, (120,100,80), DARK_GRAY])
            self.particles.append(Particle(
                x, y, math.cos(angle)*spd, math.sin(angle)*spd,
                c, random.randint(2,4), 20))

    def update_ambient(self, cam_x, cam_y):
        """Add random smoke and embers to simulate a battlefield."""
        if random.random() > 0.92: # Random smoke drifts
            ax = cam_x + random.randint(-100, SCREEN_W + 100)
            ay = cam_y + random.randint(-100, SCREEN_H + 100)
            self.particles.append(SmokeParticle(ax, ay))
        
        if random.random() > 0.98: # Random embers/sparks
            ax = cam_x + random.randint(0, SCREEN_W)
            ay = cam_y + random.randint(0, SCREEN_H)
            self.particles.append(FireParticle(ax, ay))

    def update(self):
        self.particles  = [p for p in self.particles  if p.update()]
        self.flashes    = [f for f in self.flashes    if f.update()]
        self.explosions = [e for e in self.explosions if e.update()]
        self.shake.update()

    def draw(self, screen, cam_x, cam_y):
        for p in self.particles:
            p.draw(screen, cam_x, cam_y)
        for f in self.flashes:
            f.draw(screen, cam_x, cam_y)
        for e in self.explosions:
            e.draw(screen, cam_x, cam_y)
