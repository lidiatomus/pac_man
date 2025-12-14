import pygame
from game.ui import draw_hud, draw_power_bar

MIN_TILE = 6
MAX_TILE = 64

def compute_tile_size(screen_w, screen_h, grid_w, grid_h, margin=40):
    if grid_w == 0 or grid_h == 0:
        return 20
    max_w = max(1, (screen_w - margin) // grid_w)
    max_h = max(1, (screen_h - margin) // grid_h)
    ts = min(max_w, max_h)
    return max(MIN_TILE, min(MAX_TILE, ts))

def draw_grid(surface, grid, tile_size):
    wall_color = (0,0,255)
    pellet_color = (255,255,255)
    energizer_color = (255,184,151)
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            cx = x * tile_size + tile_size//2
            cy = y * tile_size + tile_size//2
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            if tile in (3,4,5,6,7,8):
                pygame.draw.rect(surface, wall_color, rect, 3, border_radius=4)
            elif tile == 9:
                pygame.draw.line(surface, (255,0,0), (rect.left, cy), (rect.right, cy), 2)
            elif tile == 1:
                pygame.draw.circle(surface, pellet_color, (cx,cy), tile_size//6)
            elif tile == 2:
                pygame.draw.circle(surface, energizer_color, (cx,cy), tile_size//3)

def make_screen_for_grid(grid, tile_size):
    w = len(grid[0]) if grid else 0
    h = len(grid) if grid else 0
    return pygame.display.set_mode((w * tile_size, h * tile_size), pygame.RESIZABLE)

def build_render_surface(grid, tile_size):
    w = len(grid[0]) if grid else 0
    h = len(grid) if grid else 0
    return pygame.Surface((w * tile_size, h * tile_size))

def render_frame(screen, state):
    rs = state.render_surface
    rs.fill((0,0,0))
    draw_grid(rs, state.grid, state.tile_size)
    state.pacman.draw(rs)
    for g in state.ghosts:
        g.draw(rs)
    if state.fruit_active and state.fruit_pos:
        rect = state.fruit_img.get_rect(center=state.fruit_pos)
        rs.blit(state.fruit_img, rect)

    scaled = pygame.transform.smoothscale(rs, screen.get_size())
    screen.blit(scaled, (0,0))
    draw_hud(screen, pygame.font.SysFont("Arial", 20), state.difficulty, state.score, state.lives, getattr(state.pacman, "use_ai", False), state.mutate)
    if state.power_mode:
        draw_power_bar(screen, state.power_timer, 8*60)
    pygame.display.flip()