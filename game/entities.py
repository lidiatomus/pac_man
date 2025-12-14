import pygame
import os
import importlib
import random
from game.map_loader import MapLoader


# -------------------------------------------------
# Base Entity Class
# -------------------------------------------------
class Entity:
    """Base class for any moving sprite (Pac-Man or Ghost)."""

    def __init__(self, x, y, sprite_path, tile_size, speed=2):
        self.x = x
        self.y = y
        self.speed = speed
        self.tile_size = tile_size
        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        self.sprite = pygame.transform.scale(
            self.sprite, (int(tile_size * 0.9), int(tile_size * 0.9))
        )
        self.rect = self.sprite.get_rect(center=(x, y))
        self.direction = pygame.Vector2(0, 0)

    def draw(self, screen):
        screen.blit(self.sprite, self.rect)

    def update_rect(self):
        self.rect.center = (self.x, self.y)


# -------------------------------------------------
# Pac-Man (Player Controlled)
# -------------------------------------------------
class Pacman(Entity):
    """Pac-Man controlled by player, can switch to AI."""

    def __init__(self, x, y, tile_size):
        base_path = os.path.join("assets", "player_img")
        raw_images = [
            pygame.image.load(os.path.join(base_path, f"{i}.png")).convert_alpha()
            for i in range(1, 5)
        ]
        scaled_size = (int(tile_size * 0.9), int(tile_size * 0.9))
        self.images = [pygame.transform.scale(img, scaled_size) for img in raw_images]
        self.image_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.15

        px = x * tile_size + tile_size // 2
        py = y * tile_size + tile_size // 2
        super().__init__(px, py, os.path.join(base_path, "1.png"), tile_size, speed=2.5)
        self.tile_size = tile_size

        if self.images:
            self.sprite = self.images[0]
            self.rect = self.sprite.get_rect(center=(self.x, self.y))

        self.use_ai = False
        self.ai_module = None

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.direction = pygame.Vector2(1, 0)
        elif keys[pygame.K_UP]:
            self.direction = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN]:
            self.direction = pygame.Vector2(0, 1)

    def move(self):
        self.x += self.direction.x * self.speed
        self.y += self.direction.y * self.speed
        self.update_rect()

    def animate(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.sprite = self.images[self.image_index]
            self.rect = self.sprite.get_rect(center=(self.x, self.y))
            self.animation_timer = 0

    def toggle_ai(self):
        self.use_ai = not self.use_ai
        if self.use_ai:
            try:
                self.ai_module = importlib.import_module("pacman.ai_pacman")
                print("[AI] Pac-Man AI mode activated.")
            except ModuleNotFoundError:
                print("[AI] pacman/ai_pacman.py not found — defaulting to manual control.")
                self.use_ai = False
        else:
            print("[AI] Player control re-enabled.")

    def ai_move(self, grid):
        if self.ai_module and hasattr(self.ai_module, "next_direction"):
            next_dir = self.ai_module.next_direction(self, grid)
            if next_dir:
                self.direction = pygame.Vector2(*next_dir)

    def update(self, grid):
        if self.use_ai:
            self.ai_move(grid)
        else:
            self.handle_input()

        new_x = self.x + self.direction.x * self.speed
        new_y = self.y + self.direction.y * self.speed
        grid_x = int(new_x // self.tile_size)
        grid_y = int(new_y // self.tile_size)

        if (
            0 <= grid_y < len(grid)
            and 0 <= grid_x < len(grid[0])
            and grid[grid_y][grid_x] not in (3, 4, 5, 6, 7, 8)
        ):
            self.x = new_x
            self.y = new_y
            self.update_rect()
            tile = grid[grid_y][grid_x]
            if tile == 1:
                grid[grid_y][grid_x] = 0
            elif tile == 2:
                grid[grid_y][grid_x] = 0
        else:
            self.direction = pygame.Vector2(0, 0)

        # Wrap around left/right edges (tunnel)
        if self.x < 0:
            self.x = len(grid[0]) * self.tile_size
        elif self.x > len(grid[0]) * self.tile_size:
            self.x = 0

        self.update_rect()
        self.animate()


# -------------------------------------------------
# Ghost Class (Normal / Frightened / Dead)
# -------------------------------------------------
class Ghost(Entity):
    """Ghost with normal, frightened, and dead states."""

    def __init__(self, x, y, color, tile_size):
        base_path = os.path.join("assets", "ghost_img")
        sprite_path = os.path.join(base_path, f"{color}.png")
        px = x * tile_size + tile_size // 2
        py = y * tile_size + tile_size // 2
        super().__init__(px, py, sprite_path, tile_size, speed=2)
        self.color = color
        self.state = "normal"
        self.house_pos = None

        # Speeds for each state
        self.speed_normal = 2
        self.speed_frightened = 1.2
        self.speed_dead = 3.5

    def set_state(self, state):
        """Change ghost appearance and adjust speed."""
        base_path = os.path.join("assets", "ghost_img")
        if self.state == "dead" and state == "frightened":
            return  # dead ghosts can't turn blue

        if state == "frightened":
            path = os.path.join(base_path, "powerup.png")
            self.speed = self.speed_frightened
        elif state == "dead":
            path = os.path.join(base_path, "dead.png")
            self.speed = self.speed_dead
        else:
            path = os.path.join(base_path, f"{self.color}.png")
            self.speed = self.speed_normal

        sprite = pygame.image.load(path).convert_alpha()
        sprite = pygame.transform.scale(sprite, (int(self.tile_size * 0.9), int(self.tile_size * 0.9)))
        self.sprite = sprite
        self.rect = self.sprite.get_rect(center=(self.x, self.y))
        self.state = state

    def move_toward(self, target_x, target_y):
        """Move smoothly toward a target pixel position."""
        direction = pygame.Vector2(target_x - self.x, target_y - self.y)
        if direction.length() > 1:
            direction = direction.normalize()
            self.x += direction.x * self.speed
            self.y += direction.y * self.speed
        self.update_rect()

    def update(self, grid=None, tile_size=None):
        """Ghost moves differently depending on its state."""
        if self.state == "frightened":
            # wander randomly
            if random.random() < 0.03:
                dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                self.direction = pygame.Vector2(dx, dy)
            self.x += self.direction.x * self.speed
            self.y += self.direction.y * self.speed

        elif self.state == "dead" and self.house_pos:
            # move back to ghost house
            tx = self.house_pos[0] * self.tile_size + self.tile_size // 2
            ty = self.house_pos[1] * self.tile_size + self.tile_size // 2
            self.move_toward(tx, ty)
            if abs(self.x - tx) < 2 and abs(self.y - ty) < 2:
                self.set_state("normal")

        # Wrap around tunnel horizontally
        if self.x < 0:
            self.x = len(grid[0]) * self.tile_size
        elif self.x > len(grid[0]) * self.tile_size:
            self.x = 0

        self.update_rect()


# -------------------------------------------------
# Entity Initialization
# -------------------------------------------------
def create_entities(map_loader, tile_size):
    """Create Pac-Man and ghosts at safe spawn locations."""
    pacman_pos, ghost_positions = map_loader.spawn_positions()
    grid = map_loader.get_grid()

    # --- find valid spawn for Pac-Man ---
    px, py = pacman_pos
    pacman = Pacman(px, py, tile_size)

    # --- safe ghost spawn (at least 4 tiles away) ---
    def is_valid_tile(x, y):
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            return grid[y][x] not in (3, 4, 5, 6, 7, 8, 9)
        return False

    ghost_colors = ["red", "pink", "blue", "orange"]
    ghosts = []
    used_positions = set()
    safe_distance = 4

    for i, color in enumerate(ghost_colors):
        gx, gy = ghost_positions[0] if ghost_positions else (px, py)
        # offset ghosts by safe distance from Pac-Man
        while abs(gx - px) < safe_distance and abs(gy - py) < safe_distance:
            gx += random.choice([-1, 1])
            gy += random.choice([-1, 1])
            gx = max(1, min(len(grid[0]) - 2, gx))
            gy = max(1, min(len(grid) - 2, gy))

        # ensure valid path
        while not is_valid_tile(gx, gy):
            gx = random.randint(1, len(grid[0]) - 2)
            gy = random.randint(1, len(grid) - 2)

        ghosts.append(Ghost(gx, gy, color, tile_size))
        used_positions.add((gx, gy))

    # assign ghost house
    try:
        gate = map_loader.find_gate_center()
        if gate:
            gx = gate[0] if len(gate) >= 1 else len(grid[0]) // 2
            gy = gate[-1] if len(gate) >= 2 else len(grid) // 2
            for g in ghosts:
                g.house_pos = (gx, gy)
    except Exception:
        pass

    return pacman, ghosts
