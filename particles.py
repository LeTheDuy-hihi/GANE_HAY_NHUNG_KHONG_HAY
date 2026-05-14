import pygame
import random
from constants import WHITE, PINK

class SparkParticle:
    def __init__(self, x, y, color=WHITE):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.lifetime = random.randint(10, 20)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 1)

class FloatingText:
    def __init__(self, text, x, y, font, color=PINK):
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.lifetime = 60 # frames
        self.vy = -0.5

    def update(self):
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            # Simple fade by rendering with alpha if possible, or just disappear
            text_surf = self.font.render(self.text, True, self.color)
            screen.blit(text_surf, (int(self.x - text_surf.get_width()//2), int(self.y)))
