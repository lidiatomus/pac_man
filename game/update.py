import random

def handle_pellets(grid, pacman, tile_size, score, pellets_eaten, ghosts, power_mode, power_timer, POWER_TIME):
    
    px = int((pacman.x + pacman.tile_size / 2) // tile_size)
    py = int((pacman.y + pacman.tile_size / 2) // tile_size)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            tx, ty = px + dx, py + dy
            if 0 <= ty < len(grid) and 0 <= tx < len(grid[0]):
                tile = grid[ty][tx]
                if tile == 1:
                    grid[ty][tx] = 0
                    score += 10
                    pellets_eaten += 1
                elif tile == 2:
                    grid[ty][tx] = 0
                    score += 50
                    pellets_eaten += 1
                    power_mode, power_timer = True, POWER_TIME
                    for g in ghosts:
                        g.set_state("frightened")
    return grid, score, pellets_eaten, power_mode, power_timer, ghosts

def handle_fruit(grid, pacman, tile_size, pellets_eaten, triggered_fruits, fruit_active, fruit_timer, fruit_pos, fruit_raw, FRUIT_TRIGGER_COUNTS, FRUIT_TIME, FRUIT_SCORE):
    
    score = 0
    if not fruit_active:
        for trigger in FRUIT_TRIGGER_COUNTS:
            if pellets_eaten >= trigger and trigger not in triggered_fruits:
                # spawn only on walkable path
                valid_positions = [
                    (x, y)
                    for y, row in enumerate(grid)
                    for x, t in enumerate(row)
                    if t == 0
                ]
                if valid_positions:
                    spawn_x, spawn_y = random.choice(valid_positions)
                    fruit_pos = (
                        spawn_x * tile_size + tile_size // 2,
                        spawn_y * tile_size + tile_size // 2,
                    )
                    fruit_active, fruit_timer = True, FRUIT_TIME
                    triggered_fruits.add(trigger)
                break

    if fruit_active and fruit_pos:
        fx, fy = fruit_pos
        if abs(pacman.x - fx) < tile_size * 0.6 and abs(pacman.y - fy) < tile_size * 0.6:
            fruit_active, fruit_pos = False, None
            score += FRUIT_SCORE

    if fruit_active:
        fruit_timer -= 1
        if fruit_timer <= 0:
            fruit_active, fruit_pos = False, None

    return fruit_active, fruit_timer, fruit_pos, triggered_fruits, score