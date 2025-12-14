import pygame
import sys
import random
import os
import traceback
from game.map_loader import MapLoader
from game.entities import create_entities
from game.ui import draw_hud, draw_power_bar, draw_center_text
from ghosts.ghost_ai import GhostAI
from game.renderer import compute_tile_size, make_screen_for_grid, build_render_surface, draw_grid
from game.state import reset_positions, check_ghost_collision, initialize_round
from game.ai_controller import update_ghosts
from game.update import handle_pellets, handle_fruit
from game.assets import load_and_scale_fruit
from pacman_logic.pacman_agent import get_pacman_action
from pacman_logic.util import DIRECTIONS

# ---------------- Configuration ----------------
FPS = 60
POWER_TIME = 8 * FPS  # seconds of power mode
FRUIT_SCORE = 100
FRUIT_TIME = 8 * FPS  # fruit visible for 8 seconds
FRUIT_TRIGGER_COUNTS = {30, 70, 120}  # spawn fruit after these many pellets
FRUIT_PATH = "assets/fructul_pasiunii.png"


# ---------------- Main ----------------
def main():
    pygame.init()
    pygame.display.set_caption("Pac-Man AI Edition")
    font = pygame.font.SysFont("Arial", 20)
    clock = pygame.time.Clock()

    # --- Initial Setup ---
    difficulty = "MEDIUM"
    mutate = False
    loader = MapLoader(difficulty=difficulty, mutate_predefined=mutate)
    grid = loader.get_grid()
    grid_w, grid_h = loader.size()

    # --- Window and Surfaces ---
    info = pygame.display.Info()
    tile_size = compute_tile_size(info.current_w, info.current_h, grid_w, grid_h)
    screen = make_screen_for_grid(grid, tile_size)
    render_surface = build_render_surface(grid, tile_size)

    # --- Entities ---
    pacman, ghosts = create_entities(loader, tile_size)

    # assign ghost house position for respawn
    try:
        gate = loader.find_gate_center()
        if gate and len(gate) >= 3:
            gx, _, gy = gate
        else:
            gx, gy = grid_w // 2, grid_h // 2
        for g in ghosts:
            g.house_pos = (gx, gy)
    except Exception:
        pass

    # --- Fruit setup ---
    fruit_raw, fruit_img = load_and_scale_fruit(FRUIT_PATH, tile_size)
    # --- Fruit music (preload) ---
    fruit_sound = None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(base_dir, "assets", "tornero.mp3")
    try:
        # Initialize mixer (pre_init can help on some systems)
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
        except Exception:
            pass
        pygame.mixer.init()
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)
                print(f"[AUDIO] loaded music: {music_path}")
            except Exception as e:
                print("[AUDIO] pygame.mixer.music load failed:", e)
            # try Sound fallback (may fail for mp3 on some SDL builds)
            try:
                fruit_sound = pygame.mixer.Sound(music_path)
                fruit_sound.set_volume(0.5)
                print("[AUDIO] loaded Sound fallback")
            except Exception as e:
                print("[AUDIO] Sound() load failed (fallback):", e)
        else:
            print(f"[AUDIO] music file not found: {music_path}")
    except Exception as e:
        print("[AUDIO] mixer init/load error:", e)
    fruit_active, fruit_timer, fruit_pos = False, 0, None
    pellets_eaten, triggered_fruits = 0, set()

    # --- Ghost AI setup ---
    ai_mode = "bfs"
    ghost_ai = GhostAI(ai_mode)
    show_paths = False

    # --- Pac-Man AI setup ---
    pacman_ai_mode = "reflex"   # 'reflex' | 'minmax' | 'alphabeta'
    pacman_ai_depth = 2

    # --- Game state ---
    score, lives = 0, 3
    power_mode, power_timer = False, 0
    fullscreen = False

    # --- Reset helper (delegated to game.state.initialize_round) ---
    # initial round values (use the centralized initializer so event handlers can reuse it)
    fruit_img, fruit_active, fruit_timer, fruit_pos, \
    pellets_eaten, triggered_fruits, score, lives, \
    power_mode, power_timer, render_surface, pacman, ghosts = initialize_round(
        loader, grid, tile_size, fruit_raw, gx, gy
    )

    # enable pacman AI by default for testing (press 'a' to toggle)
    try:
        pacman.use_ai = True
        print(f"[PACMAN AI] enabled (mode={pacman_ai_mode}, depth={pacman_ai_depth})")
    except Exception:
        pass

    # keep previous state to detect fruit spawn/disappear transitions
    prev_fruit_active = False

    # draw a small on-screen legend of key controls
    def draw_legend(surface, font):
        lines = [
            "Esc: Quit",
            "A: Toggle Pac-Man AI",
            "K: Cycle Pac-Man AI (reflex/minmax/alphabeta)",
            "P: Toggle Ghost Paths",
            "1-4: Ghost AI mode (bfs/dfs/astar/random)",
            "5-7: Difficulty (Easy/Medium/Hard)",
            "R: Random Maze Mutation",
            "F: Toggle Fullscreen"
        ]
        padding = 6
        line_h = font.get_linesize()
        box_w = max(font.size(l)[0] for l in lines) + padding * 2
        box_h = line_h * len(lines) + padding * 2
        x = 10
        y = 10
        # semi-transparent background
        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg, (x, y))
        # render lines
        tx = x + padding
        ty = y + padding
        for l in lines:
            txt = font.render(l, True, (230, 230, 230))
            surface.blit(txt, (tx, ty))
            ty += line_h

    # small BFS pathfinder (tile coords) used to draw ghost paths when toggled
    def find_path_bfs(grid, start, goal):
        from collections import deque
        if start == goal:
            return [start]
        h, w = len(grid), len(grid[0])
        def walkable(x, y):
            if not (0 <= y < h and 0 <= x < w):
                return False
            return grid[y][x] not in (3,4,5,6,7,8)
        q = deque([start])
        parent = {start: None}
        while q:
            cur = q.popleft()
            for dx, dy in DIRECTIONS.values():
                if (dx, dy) == (0, 0):
                    continue
                nxt = (cur[0] + dx, cur[1] + dy)
                if nxt in parent:
                    continue
                if not walkable(nxt[0], nxt[1]):
                    continue
                parent[nxt] = cur
                if nxt == goal:
                    # reconstruct
                    path = []
                    it = nxt
                    while it is not None:
                        path.append(it)
                        it = parent[it]
                    return list(reversed(path))
                q.append(nxt)
        return None

    # --- Game Loop ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_a:
                    new_state = not getattr(pacman, "use_ai", False)
                    pacman.use_ai = new_state
                    try:
                        pacman.direction = pygame.Vector2(0, 0)
                    except Exception:
                        pass
                    print(f"[PACMAN AI] {'enabled' if new_state else 'disabled'}")
                elif event.key == pygame.K_p:
                    show_paths = not show_paths
                elif event.key == pygame.K_k:
                    # cycle pac-man AI modes
                    modes = ["reflex", "minmax", "alphabeta"]
                    i = modes.index(pacman_ai_mode) if pacman_ai_mode in modes else 0
                    pacman_ai_mode = modes[(i + 1) % len(modes)]
                    print(f"[PACMAN AI] mode -> {pacman_ai_mode} (depth={pacman_ai_depth})")
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = make_screen_for_grid(grid, tile_size)
                    render_surface = build_render_surface(grid, tile_size)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    modes = {pygame.K_1: "bfs", pygame.K_2: "dfs", pygame.K_3: "astar", pygame.K_4: "random"}
                    ai_mode = modes[event.key]
                    ghost_ai = GhostAI(ai_mode)
                    print(f"[AI] Mode set to {ai_mode.upper()}")
                elif event.key == pygame.K_r:
                    mutate = not mutate
                    loader.set_mutation_mode(mutate)
                    grid = loader.get_grid()
                    # full reset via state helper (keeps same logic)
                    fruit_img, fruit_active, fruit_timer, fruit_pos, \
                    pellets_eaten, triggered_fruits, score, lives, \
                    power_mode, power_timer, render_surface, pacman, ghosts = initialize_round(
                        loader, grid, tile_size, fruit_raw, gx, gy
                    )
                    # stop any fruit music when round is reset
                    try:
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
                elif event.key in (pygame.K_5, pygame.K_6, pygame.K_7):
                    difficulties = {pygame.K_5: "EASY", pygame.K_6: "MEDIUM", pygame.K_7: "HARD"}
                    difficulty = difficulties[event.key]
                    loader = MapLoader(difficulty=difficulty, mutate_predefined=mutate)
                    grid = loader.get_grid()
                    fruit_img, fruit_active, fruit_timer, fruit_pos, \
                    pellets_eaten, triggered_fruits, score, lives, \
                    power_mode, power_timer, render_surface, pacman, ghosts = initialize_round(
                        loader, grid, tile_size, fruit_raw, gx, gy
                    )
                    # stop any fruit music when difficulty changes
                    try:
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
            elif event.type == pygame.KEYUP:
                pacman.direction = pygame.Vector2(0, 0)

        # --- Update Pac-Man ---
        # If pacman AI is enabled, ask the selected agent for an action and set pacman.direction.
        if getattr(pacman, "use_ai", False):
            ai_state = {
                "grid": grid,
                "pacman_pos": (int(pacman.x // tile_size), int(pacman.y // tile_size)),
                "ghosts": [(int(g.x // tile_size), int(g.y // tile_size)) for g in ghosts],
                "scared_timer": power_timer // FPS,
                "score": score,
                "lives": lives
            }
            try:
                action = get_pacman_action(ai_state, agent_type=pacman_ai_mode, depth=pacman_ai_depth)
            except Exception as e:
                action = None
                print("[PACMAN AI] exception when calling agent (printing traceback):")
                traceback.print_exc()              # full stack trace to find offending file/line

                # if someone (incorrectly) raised a direction tuple, try to recover
                if isinstance(e, tuple) and len(e) == 2 and all(isinstance(v, int) for v in e):
                    dx, dy = e
                    for name, vec in DIRECTIONS.items():
                        if vec == (dx, dy):
                            action = name
                            print(f"[PACMAN AI] recovered action from raised tuple -> {action}")
                            break

                # final safe fallback: pick first legal action or STOP
                if action not in DIRECTIONS:
                    try:
                        from pacman_logic.util import legal_actions_from
                        legal = legal_actions_from(ai_state['pacman_pos'], ai_state['grid'])
                    except Exception:
                        legal = []
                    action = legal[0] if legal else 'STOP'
                    print(f"[PACMAN AI] fallback action -> {action}")

            if action in DIRECTIONS:
                dx, dy = DIRECTIONS[action]
                pacman.direction = pygame.Vector2(dx, dy)

        pacman.update(grid)

        # --- Ghost AI Movement ---
        pac_tile = (int(pacman.x // tile_size), int(pacman.y // tile_size))

        # ghost movement: delegate to ai_controller
        ghost_move_delay = 10   # adjust ghost speed (same as before)
        frame_counter = getattr(main, "frame_counter", 0)
        ghosts, frame_counter = update_ghosts(ghosts, pacman, grid, tile_size, ghost_ai, frame_counter, ghost_move_delay, power_mode)
        main.frame_counter = frame_counter


        # --- Collision Handling ---
        collision = check_ghost_collision(pacman, ghosts, tile_size, power_mode)
        if collision == "dead":
            score -= 500
            lives -= 1
            if lives <= 0:
                text = font.render("GAME OVER", True, (255, 0, 0))
                screen.blit(text, (screen.get_width() // 2 - 60, screen.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(2000)
                break
            else:
                pacman, ghosts = reset_positions(loader, tile_size)
                for g in ghosts:
                    g.house_pos = (gx, gy)
                power_mode = False
                fruit_active, fruit_pos = False, None
                text = font.render("READY!", True, (255, 255, 0))
                screen.blit(text, (screen.get_width() // 2 - 40, screen.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(1500)
                continue
        elif collision == "eat":
            score += 200

        # --- Power Timer ---
        if power_mode:
            power_timer -= 1
            if power_timer <= 0:
                power_mode = False
                for g in ghosts:
                    if g.state != "dead":
                        g.set_state("normal")

        # --- Pellet & Boost Eating ---
        grid, score, pellets_eaten, power_mode, power_timer, ghosts = handle_pellets(
            grid, pacman, tile_size, score, pellets_eaten, ghosts, power_mode, power_timer, POWER_TIME
        )

        # --- Fruit Handling ---
        # detect transition so we can start/stop fruit music
        prev_fruit_active = fruit_active
        fruit_active, fruit_timer, fruit_pos, triggered_fruits, fruit_score = handle_fruit(
            grid, pacman, tile_size, pellets_eaten, triggered_fruits, fruit_active, fruit_timer, fruit_pos,
            fruit_raw, FRUIT_TRIGGER_COUNTS, FRUIT_TIME, FRUIT_SCORE
        )
        # start music when fruit appears
        if not prev_fruit_active and fruit_active:
            try:
                if fruit_sound:
                    fruit_sound.play(loops=-1)
                else:
                    pygame.mixer.music.play(-1)
            except Exception as e:
                print("[AUDIO] play failed:", e)
        # stop music when fruit disappears (collected or timed out)
        if prev_fruit_active and not fruit_active:
            try:
                if fruit_sound:
                    fruit_sound.stop()
                else:
                    pygame.mixer.music.stop()
            except Exception as e:
                print("[AUDIO] stop failed:", e)
        score += fruit_score

        # --- Win condition ---
        if all(tile not in (1, 2) for row in grid for tile in row):
            # show centered win overlay via UI helper
            scaled_surface = pygame.transform.smoothscale(render_surface, screen.get_size())
            screen.blit(scaled_surface, (0, 0))
            draw_center_text(screen, font, "YOU WIN!", (255, 255, 0))
            pygame.display.flip()
            pygame.time.wait(2000)
            break

        # --- Drawing ---
        render_surface.fill((0, 0, 0))
        draw_grid(render_surface, grid, tile_size)
        pacman.draw(render_surface)
        for ghost in ghosts:
            ghost.draw(render_surface)
        # draw ghost paths when toggled
        if show_paths:
            colors = [(255, 0, 0), (0, 255, 0), (0, 160, 255), (255, 165, 0)]
            for i, g in enumerate(ghosts):
                try:
                    g_tile = (int(g.x // tile_size), int(g.y // tile_size))
                    path = find_path_bfs(grid, g_tile, pac_tile)
                except Exception:
                    path = None
                if path:
                    pts = []
                    for tx, ty in path:
                        cx = int(tx * tile_size + tile_size / 2)
                        cy = int(ty * tile_size + tile_size / 2)
                        pts.append((cx, cy))
                    col = colors[i % len(colors)]
                    if len(pts) >= 2:
                        pygame.draw.lines(render_surface, col, False, pts, 3)
                    for p in pts:
                        pygame.draw.circle(render_surface, col, p, 4)
        if fruit_active and fruit_pos:
            rect = fruit_img.get_rect(center=fruit_pos)
            render_surface.blit(fruit_img, rect)

        # scale & blit maze -> then draw overlays via UI
        scaled_surface = pygame.transform.smoothscale(render_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        draw_hud(screen, font, difficulty, score, lives, pacman.use_ai, mutate)
        if power_mode:
            draw_power_bar(screen, power_timer, POWER_TIME)

        # draw controls legend (small, top-left)
        draw_legend(screen, pygame.font.SysFont("Arial", 16))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
