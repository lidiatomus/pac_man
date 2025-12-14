from game.board import boards
from game.maze_generator import mutate_predefined_maze
import random


class MapLoader:
    def __init__(self, difficulty="MEDIUM", seed=None, mutate_predefined=False):
        """
        MapLoader loads either:
          - Static predefined Pac-Man boards, or
          - Mutated predefined boards (small random variations)

        Parameters
        ----------
        difficulty : str
            Which predefined maze to load ("EASY", "MEDIUM", "HARD")
        seed : int or None
            Used to make the random mutations reproducible.
            - If seed is given (e.g. 42), every run with the same seed
              produces the same mutated maze.
            - If None, mutations are different every time.
        mutate_predefined : bool
            Whether to apply slight random modifications to the base map.
        """
        self.mutate_predefined = bool(mutate_predefined)
        self.difficulty = difficulty.upper() if isinstance(difficulty, str) else "MEDIUM"
        self.seed = seed  # stores the random seed for consistent results

        # Normalize difficulty name (case-insensitive)
        if self.difficulty not in boards:
            for k in boards:
                if k.upper() == self.difficulty:
                    self.difficulty = k
                    break
            else:
                self.difficulty = "MEDIUM"  # fallback

        self.grid = None
        self._load()

    # -----------------------------------------------------------------
    # Internal loader
    # -----------------------------------------------------------------
    def _load(self):
        """Load the map — either as-is or with small random changes."""
        # Save RNG state and apply our own seed (so mutations are repeatable)
        state = self._set_seed_safely()

        base = boards[self.difficulty]
        if self.mutate_predefined:
            # Mutate base board using our (possibly seeded) random generator
            self.grid = mutate_predefined_maze(base, changes=80, seed=self.seed)
        else:
            # No mutation → load the original static board
            self.grid = base

        # Restore RNG to previous state so it doesn’t affect other random parts of the game
        self._restore_seed_state(state)

        # Cache dimensions for quick access
        self._w = len(self.grid[0]) if self.grid else 0
        self._h = len(self.grid) if self.grid else 0

    # -----------------------------------------------------------------
    # Control methods
    # -----------------------------------------------------------------
    def regenerate(self, seed=None):
        """
        Recreate the board, possibly with a new seed.
        If a seed is given, future regenerations with the same seed
        will produce identical mazes (useful for debugging or replay).
        """
        if seed is not None:
            self.seed = seed
        self._load()
        return self.grid

    def set_mutation_mode(self, enabled=True, seed=None):
        """
        Turn mutation mode (false-random maze) on or off.
        Optional 'seed' parameter allows you to lock in a reproducible variant.
        """
        self.mutate_predefined = bool(enabled)
        if seed is not None:
            self.seed = seed
        self._load()
        return self.grid

    # -----------------------------------------------------------------
    # Accessors and utilities
    # -----------------------------------------------------------------
    def get_grid(self):
        """Return the current board as a 2D list."""
        return self.grid

    def get_tile(self, x, y):
        """Return the tile value at (x, y), or raise IndexError if out of bounds."""
        if self.grid is None:
            raise ValueError("Grid not loaded")
        if not (0 <= y < self._h and 0 <= x < self._w):
            raise IndexError("Tile coordinates out of range")
        return self.grid[y][x]

    def size(self):
        """Return (width, height) of the grid."""
        return (self._w, self._h) if self.grid else (0, 0)

    def count_tiles(self):
        """Return a dictionary with counts of each tile type (0–9)."""
        counts = {k: 0 for k in range(10)}
        for row in self.grid:
            for t in row:
                if t in counts:
                    counts[t] += 1
        return counts

    def find_gate_center(self):
        """Find the ghost gate (two adjacent 9 tiles)."""
        for y, row in enumerate(self.grid):
            for x in range(len(row) - 1):
                if row[x] == 9 and row[x + 1] == 9:
                    return (x, x + 1, y)
        return None

    def spawn_positions(self):
        """Find safe spawn tiles for Pac-Man and ghosts."""
        gate = self.find_gate_center()
        if not gate:
            # fallback: center of map
            center_x = self._w // 2
            center_y = self._h // 2
            return (center_x, center_y), [(center_x, center_y)]

        xL, xR, y = gate
        pacman_pos = ((xL + xR) // 2, min(y + 1, self._h - 1))
        ghosts = [((xL + xR) // 2, max(y - 1, 0))]

        # --- ensure pacman spawn is not inside a wall ---
        def is_walkable(tile):
            return tile in (0, 1, 2, 9)

        gx, gy = pacman_pos
        if not is_walkable(self.grid[gy][gx]):
            # search nearby open tiles in spiral pattern
            for radius in range(1, 6):
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        nx, ny = gx + dx, gy + dy
                        if (
                            0 <= nx < self._w
                            and 0 <= ny < self._h
                            and is_walkable(self.grid[ny][nx])
                        ):
                            pacman_pos = (nx, ny)
                            return pacman_pos, ghosts

        return pacman_pos, ghosts

    # -----------------------------------------------------------------
    # Random seed handling
    # -----------------------------------------------------------------
    def _set_seed_safely(self):
        """
        Temporarily apply our own random seed.

        Why:
            - We want maze mutations to be reproducible when using the same seed.
            - We also don’t want to interfere with the global random generator
              that other parts of the game might be using.

        What it does:
            1. Saves the current global random state.
            2. Applies our seed (if provided).
            3. Returns the saved state so we can restore it later.
        """
        if self.seed is None:
            return None
        state = random.getstate()   # snapshot current global RNG
        random.seed(self.seed)      # apply deterministic seed
        return state

    def _restore_seed_state(self, state):
        """
        Restore the random generator to its previous global state.

        Why:
            - Ensures that other parts of the game using random (e.g. ghost AI,
              fruit spawns, animations) are unaffected by our seeding.
        """
        if state is not None:
            random.setstate(state)
