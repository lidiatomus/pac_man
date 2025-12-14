import pygame

def draw_hud(screen, font, difficulty, score, lives, pacman_ai, mutate):
    """Draw top HUD bar with info text."""
    ai_text = "AI: ON" if pacman_ai else "AI: OFF"
    ai_color = (0, 255, 0) if pacman_ai else (255, 80, 80)
    text = f"{difficulty} | {'Mutated' if mutate else 'Predefined'} | Score: {score} | Lives: {lives} | {ai_text}"
    hud = font.render(text, True, ai_color)
    screen.blit(hud, (10, 10))

# new helpers
def draw_power_bar(screen, power_timer, power_time, color=(0, 150, 255), height=8):
    """Draw power-up remaining bar at bottom of the screen."""
    if power_time <= 0:
        return
    w = screen.get_width()
    bar_width = int((max(0, power_timer) / power_time) * w)
    pygame.draw.rect(screen, color, (0, screen.get_height() - height - 2, bar_width, height))

def draw_center_text(screen, font, text, color=(255, 255, 0), y_offset=0):
    """Draw a centered message on the screen (useful for READY!, GAME OVER, YOU WIN)."""
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + y_offset))
    screen.blit(surf, rect)
