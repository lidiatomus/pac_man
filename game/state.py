from game.map_loader import MapLoader
from game.entities import create_entities
import pygame
import random
from game.renderer import build_render_surface

class GameState:
    def __init__(self, difficulty="MEDIUM", mutate=False, screen_size=(800,600)):
        self.difficulty = difficulty
        self.mutate = bool(mutate)
        self.loader = MapLoader(difficulty=difficulty, mutate_predefined=self.mutate)
        self.grid = self.loader.get_grid()
        self.grid_w, self.grid_h = self.loader.size()

        self.screen_w, self.screen_h = screen_size
        # tile_size will be set by caller (usually computed from screen)
        self.tile_size = 20

        # entity & visual placeholders
        self.pacman = None
        self.ghosts = []
        self.render_surface = None

        # fruit / round state
        self.fruit_raw = pygame.image.load("assets/fructul_pasiunii.png").convert_alpha()
        self.fruit_img = None
        self.fruit_active = False
        self.fruit_timer = 0
        self.fruit_pos = None
        self.pellets_eaten = 0
        self.triggered_fruits = set()

        # gameplay
        self.score = 0
        self.lives = 3
        self.power_mode = False
        self.power_timer = 0

    def set_tile_size(self, tile_size):
        self.tile_size = tile_size
        self._rescale_assets()
        self.rebuild_render_surface()
        self.reset_positions()

    def _rescale_assets(self):
        if self.fruit_raw:
            self.fruit_img = pygame.transform.scale(self.fruit_raw, (int(self.tile_size * 0.8), int(self.tile_size * 0.8)))

    def rebuild_render_surface(self):
        w = max(1, self.grid_w * self.tile_size)
        h = max(1, self.grid_h * self.tile_size)
        self.render_surface = pygame.Surface((w, h))

    def reset_positions(self):
        self.pacman, self.ghosts = create_entities(self.loader, self.tile_size)
        # ghost house assignment if loader offers it
        try:
            gate = self.loader.find_gate_center()
            if gate and len(gate) >= 3:
                gx, _, gy = gate
            else:
                gx, gy = self.grid_w // 2, self.grid_h // 2
            for g in self.ghosts:
                g.house_pos = (gx, gy)
        except Exception:
            pass

    def initialize_round(self):
        # reset round state and rescale assets
        self._rescale_assets()
        self.fruit_active = False
        self.fruit_timer = 0
        self.fruit_pos = None
        self.pellets_eaten = 0
        self.triggered_fruits = set()
        self.score = 0
        self.lives = 3
        self.power_mode = False
        self.power_timer = 0
        self.rebuild_render_surface()
        self.reset_positions()

    def change_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.loader = MapLoader(difficulty=difficulty, mutate_predefined=self.mutate)
        self.grid = self.loader.get_grid()
        self.grid_w, self.grid_h = self.loader.size()
        self.initialize_round()

    def toggle_mutation(self):
        self.mutate = not self.mutate
        self.loader.set_mutation_mode(self.mutate)
        self.grid = self.loader.get_grid()
        self.grid_w, self.grid_h = self.loader.size()
        self.initialize_round()

# Module-level helpers (exported for main.py)
def reset_positions(loader, tile_size):
    """Return (pacman, ghosts) — same behavior main expected."""
    return create_entities(loader, tile_size)


def check_ghost_collision(pacman, ghosts, tile_size, power_mode):
    """Return 'eat' | 'dead' | None as in original main collision logic."""
    for ghost in ghosts:
        if pacman.rect.colliderect(ghost.rect):
            if power_mode and getattr(ghost, "state", None) == "frightened":
                ghost.set_state("dead")
                return "eat"
            elif getattr(ghost, "state", None) != "dead":
                return "dead"
    return None


def initialize_round(loader, grid, tile_size, fruit_raw, gx, gy):
    """
    Initialize/reset round state and return the tuple main expects:
    (fruit_img, fruit_active, fruit_timer, fruit_pos,
     pellets_eaten, triggered_fruits, score, lives,
     power_mode, power_timer, render_surface, pacman, ghosts)
    """
    fruit_img = pygame.transform.scale(fruit_raw, (int(tile_size * 0.8), int(tile_size * 0.8)))
    fruit_active, fruit_timer, fruit_pos = False, 0, None
    pellets_eaten, triggered_fruits = 0, set()
    score, lives = 0, 3
    power_mode, power_timer = False, 0
    pacman, ghosts = create_entities(loader, tile_size)
    render_surface = build_render_surface(grid, tile_size)
    for g in ghosts:
        try:
            g.house_pos = (gx, gy)
        except Exception:
            pass
    return (
        fruit_img, fruit_active, fruit_timer, fruit_pos,
        pellets_eaten, triggered_fruits, score, lives,
        power_mode, power_timer, render_surface, pacman, ghosts
    )