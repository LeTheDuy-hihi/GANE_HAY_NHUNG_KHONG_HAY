import pygame
import math
from constants import *


class HUD:
    def __init__(self, font_large, font_small):
        self.font_large = font_large
        self.font_small = font_small
        
        # Minimap surface
        self.mm_size = 150
        self.mm_surf = pygame.Surface((self.mm_size, self.mm_size), pygame.SRCALPHA)
        
    def draw(self, screen, player, level, game_map, enemies):
        # ── Bottom Left: Stats ──────────────────────────────────────────────
        margin = 20
        y_start = SCREEN_H - margin - 80
        
        # HP Bar (Rugged)
        hp_pct = max(0, player.hp / player.max_hp)
        self._draw_neon_bar(screen, margin, y_start, 200, 18, hp_pct, (180, 20, 20), "HP")
        
        # Armor Bar (Military Green)
        y_start += 28
        ar_pct = player.armor / player.max_armor if player.max_armor > 0 else 0
        self._draw_neon_bar(screen, margin, y_start, 200, 18, ar_pct, (80, 100, 60), "ARMOR")
        
        # Focus Bar (Amber)
        y_start += 28
        fc_pct = player.focus / FOCUS_MAX
        self._draw_neon_bar(screen, margin, y_start, 200, 12, fc_pct, (200, 150, 20), "FOCUS")
        
        # ── Bottom Right: Ammo & Grenades ───────────────────────────────────
        ammo_txt = self.font_large.render(f"AMMO: {player.ammo}", True, YELLOW)
        gre_txt = self.font_large.render(f"GRENADES: {player.grenades}", True, ORANGE)
        
        # Dash indicator
        dash_color = LIME if player.dash_cooldown <= 0 else GRAY
        dash_txt = self.font_small.render("DASH: READY" if player.dash_cooldown <= 0 else "DASH: COOLDOWN", True, dash_color)
        
        screen.blit(ammo_txt, (SCREEN_W - margin - ammo_txt.get_width(), SCREEN_H - margin - 70))
        screen.blit(gre_txt, (SCREEN_W - margin - gre_txt.get_width(), SCREEN_H - margin - 40))
        screen.blit(dash_txt, (SCREEN_W - margin - dash_txt.get_width(), SCREEN_H - margin - 15))
        
        # ── Top Left: Level Info ────────────────────────────────────────────
        lvl_txt = self.font_large.render(f"LEVEL {level}", True, WHITE)
        en_txt = self.font_small.render(f"ENEMIES: {len(enemies)}", True, RED)
        screen.blit(lvl_txt, (margin, margin))
        screen.blit(en_txt, (margin, margin + 35))
        
        # ── Top Right: Minimap ──────────────────────────────────────────────
        self.mm_surf.fill((10, 20, 10, 220)) # Deep tactical green
        
        scale_x = self.mm_size / game_map.pixel_w
        scale_y = self.mm_size / game_map.pixel_h
        
        # 1. Draw Terrain (Walls, Cover, Paths)
        for y in range(game_map.height):
            for x in range(game_map.width):
                t = game_map.grid[y][x]
                dx, dy = x * TILE_SIZE * scale_x, y * TILE_SIZE * scale_y
                if t == TILE_WALL:
                    pygame.draw.rect(self.mm_surf, (30, 50, 30), (dx, dy, 2, 2))
                elif t == TILE_COVER:
                    pygame.draw.rect(self.mm_surf, (70, 70, 60), (dx, dy, 2, 2))
                elif game_map.detail_grid[y][x] == 1: # Path
                    pygame.draw.rect(self.mm_surf, (50, 50, 30), (dx, dy, 1, 1))

        # 2. Radar scan line effect
        scan_y = (pygame.time.get_ticks() // 15) % self.mm_size
        scan_surf = pygame.Surface((self.mm_size, 2), pygame.SRCALPHA)
        scan_surf.fill((0, 255, 0, 40))
        self.mm_surf.blit(scan_surf, (0, scan_y))

        # 3. Draw entities
        # Draw player
        px = int(player.x * scale_x)
        py = int(player.y * scale_y)
        pygame.draw.circle(self.mm_surf, GREEN, (px, py), 3)
        pygame.draw.circle(self.mm_surf, WHITE, (px, py), 4, 1) # Ring
        
        # Draw enemies
        for e in enemies:
            ex = int(e.x * scale_x)
            ey = int(e.y * scale_y)
            pygame.draw.circle(self.mm_surf, RED, (ex, ey), 2)
            
        # Draw exit
        pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() / 200))
        for y in range(game_map.height):
            for x in range(game_map.width):
                if game_map.grid[y][x] == TILE_EXIT:
                    ex = int((x * TILE_SIZE + TILE_SIZE//2) * scale_x)
                    ey = int((y * TILE_SIZE + TILE_SIZE//2) * scale_y)
                    pygame.draw.circle(self.mm_surf, (*EXIT_COLOR, pulse), (ex, ey), 4)
                    pygame.draw.circle(self.mm_surf, WHITE, (ex, ey), 6, 1)

        # Tactical Grid and Border
        for i in range(1, 4):
            pos = i * (self.mm_size // 4)
            pygame.draw.line(self.mm_surf, (30, 50, 30), (pos, 0), (pos, self.mm_size), 1)
            pygame.draw.line(self.mm_surf, (30, 50, 30), (0, pos), (self.mm_size, pos), 1)
        pygame.draw.rect(self.mm_surf, (80, 120, 80), (0, 0, self.mm_size, self.mm_size), 2)
            
        screen.blit(self.mm_surf, (SCREEN_W - margin - self.mm_size, margin))

    def _draw_neon_bar(self, screen, x, y, w, h, pct, color, label):
        # BG
        pygame.draw.rect(screen, (10, 10, 15), (x, y, w, h), border_radius=4)
        pygame.draw.rect(screen, (40, 40, 50), (x, y, w, h), 1, border_radius=4)
        
        if pct > 0:
            fill_w = int((w-4) * pct)
            if fill_w > 0:
                # Main fill
                pygame.draw.rect(screen, color, (x+2, y+2, fill_w, h-4), border_radius=2)
                # Gloss / Shine (Using a lighter version of the color instead of alpha)
                shine_color = tuple(min(255, c + 50) for c in color)
                pygame.draw.rect(screen, shine_color, (x+2, y+2, fill_w, (h-4)//2), border_radius=2)
                
                # Glow effect
                glow_surf = pygame.Surface((fill_w+10, h+10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*color, 60), (5, 5, fill_w, h), border_radius=4)
                screen.blit(glow_surf, (x-5, y-5), special_flags=pygame.BLEND_ADD)
                
        # Label
        txt = self.font_small.render(label, True, WHITE)
        screen.blit(txt, (x + 5, y - 18))
