import pygame

def update_ghosts(ghosts, pacman, grid, tile_size, ghost_ai, frame_counter, ghost_move_delay, power_mode):
    
    pac_tile = (int(pacman.x // tile_size), int(pacman.y // tile_size))

    frame_counter += 1

    for ghost in ghosts:
        if not hasattr(ghost, "target") or ghost.target is None:
            ghost.target = None

        if ghost.state == "dead":
            ghost.update(grid)
            continue

        start = (int(ghost.x // tile_size), int(ghost.y // tile_size))

        if ghost.target:
            tx, ty = ghost.target
            ghost.target_px = tx * tile_size + tile_size // 2
            ghost.target_py = ty * tile_size + tile_size // 2
            reached = (abs(ghost.x - ghost.target_px) < 1.0 and abs(ghost.y - ghost.target_py) < 1.0)
        else:
            reached = True

        if reached and (frame_counter % ghost_move_delay == 0):
            game_state = {
                "ghost_pos": start,
                "player_pos": pac_tile,
                "map": grid,
                "color": ghost.color,
                "ghosts": ghosts,
                "pac_dir": (int(pacman.direction.x), int(pacman.direction.y)),
                "power_mode": power_mode
            }
            next_tile = ghost_ai.get_next_move(game_state)
            if next_tile and next_tile != start:
                ghost.target = next_tile
                tx, ty = next_tile
                ghost.target_px = tx * tile_size + tile_size // 2
                ghost.target_py = ty * tile_size + tile_size // 2

        if ghost.target:
            vec = pygame.Vector2(ghost.target_px - ghost.x, ghost.target_py - ghost.y)
            dist = vec.length()
            if dist > 0:
                step = min(ghost.speed, dist)
                vec = vec.normalize()
                ghost.x += vec.x * step
                ghost.y += vec.y * step
            if dist <= 1.0:
                ghost.x = ghost.target_px
                ghost.y = ghost.target_py
                ghost.target = None

        ghost.update_rect()

        if ghost.x < -tile_size:
            ghost.x = len(grid[0]) * tile_size
        elif ghost.x > len(grid[0]) * tile_size + tile_size:
            ghost.x = -tile_size

    return ghosts, frame_counter