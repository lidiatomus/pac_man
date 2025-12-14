import random
import copy
from collections import deque

# -------------------------------------
# Pac-Man board tile rules
# -------------------------------------
WALKABLE_TILES = {0, 1, 2, 9}         # 0 = empty, 1 = pellet, 2 = energizer, 9 = gate
PROTECTED_TILES = {4, 5, 6, 7, 8, 9}  # corners, gate, and borders (never modified)


# -------------------------------------
# Connectivity helpers
# -------------------------------------
def is_walkable(tile: int) -> bool:
    """Return True if Pac-Man can move on this tile."""
    return tile in WALKABLE_TILES


def find_connected_components(grid):
    """Return a list of connected walkable areas (each is a list of (x, y) cells)."""
    height = len(grid)
    width = len(grid[0]) if height else 0
    visited = [[False] * width for _ in range(height)]
    components = []

    for y in range(height):
        for x in range(width):
            if visited[y][x] or not is_walkable(grid[y][x]):
                continue

            queue = deque([(x, y)])
            visited[y][x] = True
            component = [(x, y)]

            while queue:
                cx, cy = queue.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if not visited[ny][nx] and is_walkable(grid[ny][nx]):
                            visited[ny][nx] = True
                            queue.append((nx, ny))
                            component.append((nx, ny))

            components.append(component)

    return components


def carve_corridor(grid, start, end):
    """Open a simple straight corridor between two coordinates."""
    x1, y1 = start
    x2, y2 = end
    cx, cy = x1, y1

    # Step horizontally
    step_x = 1 if x2 > cx else -1
    while cx != x2:
        if grid[cy][cx] not in PROTECTED_TILES:
            grid[cy][cx] = 0
        cx += step_x

    # Step vertically
    step_y = 1 if y2 > cy else -1
    while cy != y2:
        if grid[cy][cx] not in PROTECTED_TILES:
            grid[cy][cx] = 0
        cy += step_y

    # Final cell
    if grid[cy][cx] not in PROTECTED_TILES:
        grid[cy][cx] = 0


def ensure_fully_connected(grid):
    """Guarantee that all walkable areas are reachable by connecting components."""
    components = find_connected_components(grid)
    if len(components) <= 1:
        return

    # Merge smaller areas into the largest one
    components.sort(key=len, reverse=True)
    main = components[0]

    for comp in components[1:]:
        closest_pair = None
        closest_distance = float("inf")

        for (x1, y1) in main:
            for (x2, y2) in comp:
                d = abs(x1 - x2) + abs(y1 - y2)
                if d < closest_distance:
                    closest_distance = d
                    closest_pair = ((x1, y1), (x2, y2))

        if closest_pair:
            carve_corridor(grid, *closest_pair)

        # Recompute main component
        components = find_connected_components(grid)
        components.sort(key=len, reverse=True)
        main = components[0]


# -------------------------------------
# Maze mutation logic
# -------------------------------------
def mutate_predefined_maze(board, changes=120, wall_to_path_prob=0.8, path_to_wall_prob=0.1, seed=None):
    """
    Randomly modify a predefined Pac-Man maze by flipping small clusters of tiles.

    The mutation:
      - Primarily opens new corridors (wall → path)
      - Occasionally adds new walls (path → wall)
      - Keeps symmetry (left mirrored to right)
      - Ensures maze stays fully connected and playable
    """
    if seed is not None:
        random.seed(seed)

    grid = copy.deepcopy(board)
    height = len(grid)
    width = len(grid[0]) if height else 0
    if not width or not height:
        return grid

    def flip_cluster(cx, cy, radius=1):
        """Flip a small 2D area of tiles around a center point."""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                if not (0 <= x < width and 0 <= y < height):
                    continue
                if grid[y][x] in PROTECTED_TILES:
                    continue

                tile = grid[y][x]
                if is_walkable(tile) and random.random() < path_to_wall_prob:
                    grid[y][x] = 3  # small wall
                elif not is_walkable(tile) and random.random() < wall_to_path_prob:
                    grid[y][x] = 0  # open path

    # Apply random cluster mutations on the left half
    for _ in range(changes):
        x = random.randint(2, width // 2 - 2)
        y = random.randint(1, height - 2)
        flip_cluster(x, y, radius=random.choice([1, 2]))

    # Mirror horizontally for symmetry
    for y in range(height):
        for x in range(width // 2):
            grid[y][width - 1 - x] = grid[y][x]

    # Repair connectivity
    ensure_fully_connected(grid)
    return grid
