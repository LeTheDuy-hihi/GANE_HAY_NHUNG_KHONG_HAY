import asyncio
import pygame
from constants import WIDTH, HEIGHT, FPS, BLACK
from game_controller import GameController

from menu import MenuManager

class AppState:
    MENU = "MENU"
    GAME = "GAME"

def main_sync():
    pass

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Duy oi chay di")
    clock = pygame.time.Clock()

    app_state = AppState.MENU
    menu_manager = MenuManager()
    game_controller = None

    # Resizable setup
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    current_w = WIDTH
    current_h = HEIGHT
    logical_surface = pygame.Surface((current_w, current_h))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle mouse click mapping
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Map physical screen pos to logical surface pos
                screen_w, screen_h = screen.get_size()
                scale = min(screen_w / current_w, screen_h / current_h)
                scaled_w = int(current_w * scale)
                scaled_h = int(current_h * scale)
                offset_x = (screen_w - scaled_w) // 2
                offset_y = (screen_h - scaled_h) // 2
                
                logical_x = (event.pos[0] - offset_x) / scale
                logical_y = (event.pos[1] - offset_y) / scale
                
                # Create a fake event with mapped pos for menu
                mapped_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(logical_x, logical_y))
                if app_state == AppState.MENU:
                    action = menu_manager.handle_input(mapped_event)
                    if action == "START":
                        app_state = AppState.GAME
                        game_controller = GameController(level=menu_manager.selected_level)
            else:
                if app_state == AppState.MENU:
                    action = menu_manager.handle_input(event)
                    if action == "START":
                        app_state = AppState.GAME
                        game_controller = GameController(level=menu_manager.selected_level)
                elif app_state == AppState.GAME:
                    game_controller.handle_input(event)

        logical_surface.fill(BLACK)
        if app_state == AppState.MENU:
            menu_manager.update()
            menu_manager.draw(logical_surface)
        elif app_state == AppState.GAME:
            game_controller.update()
            if game_controller.quit_to_menu:
                app_state = AppState.MENU
                game_controller = None
                current_w = WIDTH
                current_h = HEIGHT
                logical_surface = pygame.Surface((current_w, current_h))
            elif getattr(game_controller, 'level_complete', False) and game_controller.level_complete_timer <= 0:
                old_ai_mode = game_controller.auto_ai_mode
                game_controller = GameController(level=game_controller.level + 1)
                game_controller.auto_ai_mode = old_ai_mode
            else:
                cw = game_controller.get_width()
                ch = game_controller.get_height()
                if cw != current_w or ch != current_h:
                    current_w = cw
                    current_h = ch
                    logical_surface = pygame.Surface((current_w, current_h))
                game_controller.draw(logical_surface)

        # Scale logical surface to fit physical screen
        screen_w, screen_h = screen.get_size()
        scale = min(screen_w / current_w, screen_h / current_h)
        scaled_w = int(current_w * scale)
        scaled_h = int(current_h * scale)
        
        scaled_surface = pygame.transform.smoothscale(logical_surface, (scaled_w, scaled_h))
        
        screen.fill(BLACK)
        screen.blit(scaled_surface, ((screen_w - scaled_w) // 2, (screen_h - scaled_h) // 2))
        
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
