import copy

DIRECTIONS = {
    'UP':    (0, -1),
    'DOWN':  (0, 1),
    'LEFT':  (-1, 0),
    'RIGHT': (1, 0),
    'STOP':  (0, 0)
}

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def in_bounds(grid, pos):
    x, y = pos
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])

def is_walkable_tile(grid, x, y):
    if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
        return False
    # treat 3..8 as walls per your project conventions
    return grid[y][x] not in (3,4,5,6,7,8)

def add_dir(pos, direction):
    """
    direction can be:
      - a string key in DIRECTIONS ('UP','LEFT',...)
      - a (dx,dy) tuple
    Returns a new (x,y) position.
    """
    if isinstance(direction, str):
        dx, dy = DIRECTIONS.get(direction, (0,0))
    else:
        # assume tuple-like (dx,dy)
        dx, dy = direction
    return (pos[0] + dx, pos[1] + dy)

def legal_actions_from(pos, grid):
    """
    Return list of action strings ('UP','DOWN','LEFT','RIGHT') that lead to walkable tiles.
    pos is (x,y).
    """
    actions = []
    for name, (dx, dy) in DIRECTIONS.items():
        if name == 'STOP':
            continue
        nx, ny = pos[0] + dx, pos[1] + dy
        if is_walkable_tile(grid, nx, ny):
            actions.append(name)
    return actions

def find_all_pellets(grid):
    pellets = []
    for y, row in enumerate(grid):
        for x, t in enumerate(row):
            if t in (1, 2):
                pellets.append((x, y))
    return pellets

def sense_ghosts(pac_pos, ghosts, radius=4):
    positions = []
    for g in ghosts:
        if isinstance(g, (list, tuple)):
            gx, gy = int(g[0]), int(g[1])
        else:
            # fallback if ghost is an object with x,y
            try:
                gx, gy = int(g.x), int(g.y)
            except Exception:
                continue
        if manhattan_distance(pac_pos, (gx, gy)) <= radius:
            positions.append((gx, gy))
    return positions

def evaluation_function(state):
    pac = state.get('pacman_pos')
    ghosts = state.get('ghosts', [])
    pellets = find_all_pellets(state.get('grid', []))
    score = state.get('score', 0)

    if pellets:
        dp = min(manhattan_distance(pac, p) for p in pellets)
    else:
        dp = 0

    if ghosts:
        dg = min(manhattan_distance(pac, g) for g in ghosts)
    else:
        dg = 999

    val = score
    val -= dp * 2
    if dg <= 1:
        val -= 1000
    else:
        val += dg * 3
    val -= len(pellets)
    return val

def generate_successor(state, agent_index, action):
    """
    Return a shallow-copied successor state after applying action.
    agent_index == 0 -> pacman; >=1 -> ghost index = agent_index-1
    action is a string ('UP','LEFT',...) or tuple (dx,dy).
    """
    new = {
        'grid': [row[:] for row in state.get('grid', [])],
        'pacman_pos': tuple(state.get('pacman_pos')),
        'ghosts': [tuple(g) for g in state.get('ghosts', [])],
        'score': state.get('score', 0),
        'lives': state.get('lives', 3)
    }

    if isinstance(action, tuple):
        # convert tuple action to name if possible
        for name, vec in DIRECTIONS.items():
            if vec == action:
                action_name = name
                break
        else:
            action_name = 'STOP'
    else:
        action_name = action

    if agent_index == 0:
        cur = new['pacman_pos']
        dx, dy = DIRECTIONS.get(action_name, (0,0))
        nx, ny = cur[0] + dx, cur[1] + dy
        if is_walkable_tile(new['grid'], nx, ny):
            new['pacman_pos'] = (nx, ny)
            tile = new['grid'][ny][nx]
            if tile == 1:
                new['score'] += 10
                new['grid'][ny][nx] = 0
            elif tile == 2:
                new['score'] += 50
                new['grid'][ny][nx] = 0
    else:
        gi = agent_index - 1
        if gi < len(new['ghosts']):
            cur = new['ghosts'][gi]
            dx, dy = DIRECTIONS.get(action_name, (0,0))
            nx, ny = cur[0] + dx, cur[1] + dy
            if is_walkable_tile(new['grid'], nx, ny):
                new['ghosts'][gi] = (nx, ny)

    return new

def terminal_test(state):
    pellets = find_all_pellets(state.get('grid', []))
    if not pellets:
        return True
    pac = state.get('pacman_pos')
    for g in state.get('ghosts', []):
        if pac == tuple(g):
            return True
    return False