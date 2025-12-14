import pygame

def handle_event(event, screen, state):
    if event.type == pygame.QUIT:
        return False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return False
        if event.key == pygame.K_a:
            state.pacman.toggle_ai()
        if event.key == pygame.K_r:
            state.toggle_mutation()
        if event.key == pygame.K_f:
            if screen.get_flags() & pygame.FULLSCREEN:
                pygame.display.set_mode((state.screen_w//2, state.screen_h//2), pygame.RESIZABLE)
            else:
                info = pygame.display.Info()
                pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            win_w, win_h = pygame.display.get_window_size()
            state.set_tile_size(state.tile_size if state.tile_size else 20)
    if event.type == pygame.VIDEORESIZE:
        screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
    return True