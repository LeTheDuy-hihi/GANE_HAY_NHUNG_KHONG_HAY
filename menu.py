import pygame
from constants import WIDTH, HEIGHT, BLACK, CYAN, YELLOW, WHITE, PINK, RED, PEACH

class MenuState:
    MAIN = "MAIN"
    RULES = "RULES"
    LEVELS = "LEVELS"

class MenuManager:
    def __init__(self):
        self.state = MenuState.MAIN
        self.selected_level = 1
        
        pygame.font.init()
        self.title_font = pygame.font.SysFont('segoeui', 72, bold=True)
        self.font = pygame.font.SysFont('segoeui', 48, bold=True)
        self.small_font = pygame.font.SysFont('segoeui', 28)
        self.blink_counter = 0

        self.main_options = ["CHƠI NGAY", "CHỌN CẤP ĐỘ", "LUẬT CHƠI"]
        self.main_selected = 0
        
        self.level_options = ["CẤP ĐỘ 1", "CẤP ĐỘ 2", "CẤP ĐỘ 3", "CẤP ĐỘ 4", "CẤP ĐỘ 5"]
        self.level_selected = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == MenuState.MAIN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.main_selected = (self.main_selected - 1) % len(self.main_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.main_selected = (self.main_selected + 1) % len(self.main_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.main_selected == 0:
                        return "START"
                    elif self.main_selected == 1:
                        self.state = MenuState.LEVELS
                    elif self.main_selected == 2:
                        self.state = MenuState.RULES

            elif self.state == MenuState.LEVELS:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.level_selected = (self.level_selected - 1) % len(self.level_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.level_selected = (self.level_selected + 1) % len(self.level_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.selected_level = self.level_selected + 1
                    self.state = MenuState.MAIN
                elif event.key == pygame.K_ESCAPE:
                    self.state = MenuState.MAIN

            elif self.state == MenuState.RULES:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.state = MenuState.MAIN
                    
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            if self.state == MenuState.MAIN:
                for i in range(len(self.main_options)):
                    rect_y = HEIGHT // 2 + i * 60
                    if rect_y <= mouse_y <= rect_y + 40 and WIDTH//4 <= mouse_x <= WIDTH*3//4:
                        self.main_selected = i
                        if i == 0:
                            return "START"
                        elif i == 1:
                            self.state = MenuState.LEVELS
                        elif i == 2:
                            self.state = MenuState.RULES

            elif self.state == MenuState.LEVELS:
                for i in range(len(self.level_options)):
                    rect_y = HEIGHT // 2 - 50 + i * 50
                    if rect_y <= mouse_y <= rect_y + 40 and WIDTH//4 <= mouse_x <= WIDTH*3//4:
                        self.level_selected = i
                        self.selected_level = self.level_selected + 1
                        self.state = MenuState.MAIN
                        
            elif self.state == MenuState.RULES:
                self.state = MenuState.MAIN
                
        return None

    def update(self):
        self.blink_counter += 1

    def draw(self, screen):
        screen.fill(BLACK)
        if self.state == MenuState.MAIN:
            self._draw_main(screen)
        elif self.state == MenuState.LEVELS:
            self._draw_levels(screen)
        elif self.state == MenuState.RULES:
            self._draw_rules(screen)

    def _draw_main(self, screen):
        title = self.title_font.render("Duy oi chay di", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        for i, option in enumerate(self.main_options):
            color = CYAN if i == self.main_selected else WHITE
            if i == self.main_selected and (self.blink_counter // 20) % 2 == 0:
                color = RED # Blink effect
            text = self.font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + i * 60))

        mode_text = self.small_font.render(f"Cấp độ: {self.selected_level}", True, PEACH)
        screen.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, HEIGHT - 50))



    def _draw_levels(self, screen):
        title = self.font.render("CHỌN CẤP ĐỘ", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        for i, option in enumerate(self.level_options):
            color = CYAN if i == self.level_selected else WHITE
            text = self.font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50 + i * 50))
            
        back_text = self.small_font.render("Nhấn ENTER để chọn hoặc ESC để quay lại", True, WHITE)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

    def _draw_rules(self, screen):
        title = self.font.render("LUẬT CHƠI & CÁCH ĐIỀU KHIỂN", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        rules = [
            "MŨI TÊN/WASD: Di chuyển Pac-Man",
            "CHẤM NHỎ: 10 điểm | CHẤM LỚN: 50 điểm",
            "Ăn Chấm Lớn để làm ma ĐỔI MÀU và ăn chúng!",
            "",
            "ĐỘI QUÂN MA SỬ DỤNG AI:",
            "- Áp dụng đồng thời BFS, DFS và A* để vây bắt.",
            "- Bao vây và truy đuổi cực kỳ thông minh."
        ]

        for i, line in enumerate(rules):
            color = WHITE
            if "BLINKY" in line: color = RED
            elif "PINKY" in line: color = PINK
            elif "INKY" in line: color = CYAN
            elif "CLYDE" in line: color = (255, 184, 82)
            elif "CHẤM LỚN" in line: color = PEACH
            
            text = self.small_font.render(line, True, color)
            screen.blit(text, (50, 150 + i * 40))

        back_text = self.small_font.render("Nhấn ESC để quay lại", True, WHITE)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))
