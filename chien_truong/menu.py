# menu.py — Tactical Main Menu (Cyber Military Style)
import pygame
import math
import random
from constants import *
from ui_framework import Button, Panel, ScanLine, ParticleField


class MainMenu:
    def __init__(self, font_title, font_normal, font_small):
        self.font_title = font_title
        self.font_normal = font_normal
        self.font_small = font_small

        self.state = "MAIN"  # MAIN, CONTROLS, STORY
        self.selected = 0
        self._pulse = 0.0

        # Menu items with icons
        self.menu_items = [
            {"text": "PLAY",       "icon": "▶", "action": "START",    "color": UI_SUCCESS},
            {"text": "LOADOUT",    "icon": "⚔", "action": "LOADOUT",  "color": UI_BORDER},
            {"text": "INVENTORY",  "icon": "▦", "action": "INVENTORY","color": UI_BORDER},
            {"text": "MISSIONS",   "icon": "◎", "action": "MISSIONS", "color": UI_BORDER},
            {"text": "SETTINGS",   "icon": "⚙", "action": "SETTINGS", "color": UI_BORDER},
            {"text": "EXIT",       "icon": "✕", "action": "QUIT",     "color": UI_DANGER},
        ]

        # Background effects
        self.particles = ParticleField(80)
        self.scan = ScanLine(0, 0, SCREEN_W, SCREEN_H, speed=1, color=UI_BORDER)

        # Rain effect
        self.rain = []
        for _ in range(120):
            self.rain.append([
                random.randint(0, SCREEN_W),
                random.randint(0, SCREEN_H),
                random.randint(8, 18),
                random.randint(150, 220)
            ])

        # Distant flashes
        self.flash_timer = 0
        self.flash_x = 0
        self.flash_y = 0

        # Controls text
        self.controls_text = [
            "W, A, S, D — Di chuyển",
            "Chuột trái — Bắn súng",
            "Chuột phải — Ngắm bắn (ADS)",
            "G — Ném lựu đạn",
            "SHIFT — Chạy nhanh (Sprint)",
            "Q — Tập trung (Slow-Mo)",
            "TAB — Mở Inventory",
            "R — Nạp đạn",
            "",
            "Tiêu diệt kẻ địch, tìm đường đến trực thăng (H).",
        ]

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "MAIN":
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.menu_items)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.menu_items)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return self._activate()
            else:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    if self.state == "STORY":
                        return "START"
                    self.state = "MAIN"

        if event.type == pygame.MOUSEMOTION and self.state == "MAIN":
            for i in range(len(self.menu_items)):
                rect = self._get_item_rect(i)
                if rect.collidepoint(event.pos):
                    self.selected = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "MAIN":
                for i in range(len(self.menu_items)):
                    rect = self._get_item_rect(i)
                    if rect.collidepoint(event.pos):
                        self.selected = i
                        return self._activate()
            elif self.state == "STORY":
                return "START"
            else:
                self.state = "MAIN"
        return None

    def _activate(self):
        action = self.menu_items[self.selected]["action"]
        if action == "START":
            return "START"
        elif action == "QUIT":
            return "QUIT"
        elif action == "SETTINGS":
            self.state = "CONTROLS"
        # LOADOUT, INVENTORY, MISSIONS — future phases
        return None

    def _get_item_rect(self, index):
        x = 80
        y = 320 + index * 58
        return pygame.Rect(x, y, 320, 48)

    def draw(self, screen):
        self._pulse += 0.02

        # ── Background ──────────────────────────────────────────────────
        screen.fill(UI_BG)

        # Grid overlay
        for gx in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, (15, 20, 28), (gx, 0), (gx, SCREEN_H), 1)
        for gy in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, (15, 20, 28), (0, gy), (SCREEN_W, gy), 1)

        # Rain
        for drop in self.rain:
            alpha = drop[3]
            pygame.draw.line(screen, (40, 60, 90),
                             (drop[0], drop[1]),
                             (drop[0] - 1, drop[1] + drop[2]), 1)
            drop[1] += drop[2] * 0.8
            drop[0] -= 1
            if drop[1] > SCREEN_H:
                drop[1] = random.randint(-30, 0)
                drop[0] = random.randint(0, SCREEN_W)

        # Distant explosion flashes
        if self.flash_timer > 0:
            flash_alpha = int(self.flash_timer * 8)
            flash_r = 200 + (20 - self.flash_timer) * 15
            flash_surf = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 200, 100, min(flash_alpha, 60)),
                               (flash_r, flash_r), flash_r)
            screen.blit(flash_surf, (self.flash_x - flash_r, self.flash_y - flash_r))
            self.flash_timer -= 1
        elif random.random() > 0.995:
            self.flash_timer = random.randint(8, 18)
            self.flash_x = random.randint(SCREEN_W // 2, SCREEN_W)
            self.flash_y = random.randint(0, SCREEN_H // 3)

        # Particles
        self.particles.update()
        self.particles.draw(screen)

        # Scan line
        self.scan.update()
        self.scan.draw(screen)

        if self.state == "MAIN":
            self._draw_main(screen)
        elif self.state == "CONTROLS":
            self._draw_controls(screen)

    def _draw_main(self, screen):
        # ── Left Panel: Title + Menu ────────────────────────────────────
        # Title
        title_text = "CHIẾN TRƯỜNG"
        title_surf = self.font_title.render(title_text, True, UI_HIGHLIGHT)
        screen.blit(title_surf, (80, 100))

        # Subtitle
        sub_text = "1968 — TACTICAL OPERATIONS"
        sub_surf = self.font_small.render(sub_text, True, UI_TEXT_DIM)
        screen.blit(sub_surf, (84, 170))

        # Separator line
        sep_pulse = int(180 + 40 * math.sin(self._pulse * 2))
        pygame.draw.line(screen, (*UI_BORDER, sep_pulse), (80, 200), (400, 200), 2)

        # Version/status
        ver_surf = self.font_small.render("v2.0 TACTICAL // STATUS: OPERATIONAL", True, UI_TEXT_DIM)
        screen.blit(ver_surf, (80, 215))

        # ── Menu Items ──────────────────────────────────────────────────
        for i, item in enumerate(self.menu_items):
            rect = self._get_item_rect(i)
            is_sel = (i == self.selected)

            # Background
            if is_sel:
                # Selected highlight
                sel_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                sel_surf.fill((*UI_PANEL_LIGHT, 200))
                screen.blit(sel_surf, rect.topleft)

                # Left accent bar
                pygame.draw.rect(screen, item["color"], (rect.x, rect.y, 4, rect.h))

                # Glow
                glow_pulse = int(15 + 10 * math.sin(self._pulse * 4))
                glow_surf = pygame.Surface((rect.w + 20, rect.h + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*item["color"], glow_pulse),
                                 (0, 0, rect.w + 20, rect.h + 10), border_radius=6)
                screen.blit(glow_surf, (rect.x - 10, rect.y - 5))
            else:
                # Subtle background
                bg_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                bg_surf.fill((15, 20, 30, 100))
                screen.blit(bg_surf, rect.topleft)

            # Border bottom
            border_col = item["color"] if is_sel else (30, 40, 55)
            pygame.draw.line(screen, border_col,
                             (rect.x, rect.bottom - 1),
                             (rect.right, rect.bottom - 1), 1)

            # Text
            txt_color = item["color"] if is_sel else UI_TEXT_DIM
            txt = self.font_normal.render(item["text"], True, txt_color)
            screen.blit(txt, (rect.x + 20, rect.y + rect.h // 2 - txt.get_height() // 2))

            # Arrow indicator
            if is_sel:
                arrow_x = rect.x + rect.w - 30
                arr_pulse = int(8 * math.sin(self._pulse * 5))
                arrow = self.font_normal.render("›", True, item["color"])
                screen.blit(arrow, (arrow_x + arr_pulse,
                                    rect.y + rect.h // 2 - arrow.get_height() // 2))

        # ── Right Panel: Info/Stats ─────────────────────────────────────
        # Decorative right panel
        right_x = SCREEN_W - 420
        panel_rect = pygame.Rect(right_x, 80, 380, 500)
        pygame.draw.rect(screen, (*UI_PANEL, 150), panel_rect, border_radius=6)
        pygame.draw.rect(screen, UI_BORDER, panel_rect, 1, border_radius=6)

        # Corner decorations
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            cx = panel_rect.left if dx == 1 else panel_rect.right
            cy = panel_rect.top if dy == 1 else panel_rect.bottom
            pygame.draw.line(screen, UI_HIGHLIGHT, (cx, cy), (cx + 15 * dx, cy), 2)
            pygame.draw.line(screen, UI_HIGHLIGHT, (cx, cy), (cx, cy + 15 * dy), 2)

        # Right panel content
        info_title = self.font_normal.render("BRIEFING", True, UI_HIGHLIGHT)
        screen.blit(info_title, (right_x + 20, 100))
        pygame.draw.line(screen, UI_BORDER, (right_x + 20, 130), (right_x + 360, 130), 1)

        briefing = [
            "Năm 1968 — Chiến dịch Mậu Thân",
            "",
            "Bạn là trinh sát đặc biệt được",
            "giao nhiệm vụ xâm nhập vào",
            "hậu cứ của địch.",
            "",
            "▸ Tiêu diệt kẻ địch",
            "▸ Thu thập vật tư",
            "▸ Tìm đường đến trực thăng",
            "",
            f"Level hiện tại: 1/{MAX_LEVEL}",
        ]
        for i, line in enumerate(briefing):
            col = UI_TEXT if line.startswith("▸") else UI_TEXT_DIM
            txt = self.font_small.render(line, True, col)
            screen.blit(txt, (right_x + 25, 145 + i * 28))

        # Status indicators at bottom of right panel
        status_y = panel_rect.bottom - 80
        indicators = [
            ("WEAPONS", UI_SUCCESS, "ONLINE"),
            ("COMMS", UI_WARNING, "STATIC"),
            ("RADAR", UI_BORDER, "ACTIVE"),
        ]
        for i, (label, color, val) in enumerate(indicators):
            iy = status_y + i * 22
            lbl = self.font_small.render(label, True, UI_TEXT_DIM)
            screen.blit(lbl, (right_x + 25, iy))
            # Blinking dot
            dot_alpha = int(200 + 55 * math.sin(self._pulse * 3 + i))
            dot_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, (*color, dot_alpha), (4, 4), 4)
            screen.blit(dot_surf, (right_x + 140, iy + 4))
            val_txt = self.font_small.render(val, True, color)
            screen.blit(val_txt, (right_x + 155, iy))

        # ── Bottom Bar ──────────────────────────────────────────────────
        bar_y = SCREEN_H - 40
        pygame.draw.line(screen, UI_BORDER, (0, bar_y), (SCREEN_W, bar_y), 1)
        hint = self.font_small.render("↑↓ Di chuyển  |  ENTER Chọn  |  ESC Thoát", True, UI_TEXT_DIM)
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, bar_y + 10))

        # Time display
        import time
        time_str = time.strftime("%H:%M:%S")
        time_txt = self.font_small.render(time_str, True, UI_BORDER)
        screen.blit(time_txt, (SCREEN_W - time_txt.get_width() - 20, bar_y + 10))

    def _draw_controls(self, screen):
        # Panel
        panel = Panel(SCREEN_W // 2 - 350, 60, 700, 600, "HƯỚNG DẪN ĐIỀU KHIỂN")
        panel.draw(screen, self.font_normal)

        px = SCREEN_W // 2 - 350 + 30
        py = 120
        for i, line in enumerate(self.controls_text):
            if "—" in line:
                parts = line.split("—")
                key_txt = self.font_normal.render(parts[0].strip(), True, UI_HIGHLIGHT)
                desc_txt = self.font_normal.render(parts[1].strip(), True, UI_TEXT)
                screen.blit(key_txt, (px, py + i * 40))
                screen.blit(desc_txt, (px + 200, py + i * 40))
            else:
                txt = self.font_normal.render(line, True, UI_TEXT_DIM)
                screen.blit(txt, (px, py + i * 40))

        # Back prompt
        back_txt = self.font_small.render("Nhấn ENTER hoặc ESC để quay lại", True, UI_WARNING)
        pulse = int(128 + 127 * math.sin(self._pulse * 4))
        back_txt.set_alpha(pulse)
        screen.blit(back_txt, (SCREEN_W // 2 - back_txt.get_width() // 2, 680))
