import random
import time

class GhostAI:
    def __init__(self, mode="bfs"):
        from .bfs import bfs
        from .dfs import dfs
        from .astar import astar
        from .random_ai import RandomAI

        self.algorithm_name = mode
        if mode == "bfs":
            self.algorithm = bfs
        elif mode == "dfs":
            self.algorithm = dfs
        elif mode == "astar":
            self.algorithm = astar
        elif mode == "random":
            self.algorithm = RandomAI().get_next_move
        else:
            raise ValueError(f"Unknown mode: {mode}")

        # --- new state variables ---
        self.state = "chase"  # can be chase / scatter / frightened
        self.last_switch = time.time()
        self.scatter_duration = 7
        self.chase_duration = 20

    def update_state(self, power_mode):
        """Handle switching between chase/scatter or frightened."""
        now = time.time()

        # scared overrides other states
        if power_mode:
            self.state = "frightened"
            return

        # alternate between chase <-> scatter
        if self.state == "chase" and now - self.last_switch > self.chase_duration:
            self.state = "scatter"
            self.last_switch = now
        elif self.state == "scatter" and now - self.last_switch > self.scatter_duration:
            self.state = "chase"
            self.last_switch = now

    def get_next_move(self, game_state):
        """Return next tile based on ghost type and current AI state."""
        ghost_pos = game_state["ghost_pos"]
        pac_pos = game_state["player_pos"]
        maze = game_state["map"]
        ghost_color = game_state.get("color", "red")
        ghosts = game_state.get("ghosts", [])
        power_mode = game_state.get("power_mode", False)
        pac_dir = game_state.get("pac_dir", (0, 0))
        blinky_pos = None

        self.update_state(power_mode)
        gx, gy = ghost_pos
        px, py = pac_pos

        # find Blinky for Inky calculations
        for g in ghosts:
            if g.color == "red":
                blinky_pos = (int(g.x // g.tile_size), int(g.y // g.tile_size))
                break

        # === frightened: random wandering ===
        if self.state == "frightened":
            dirs = [(1,0), (-1,0), (0,1), (0,-1)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = gx + dx, gy + dy
                if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]) and maze[ny][nx] not in (3,4,5,6,7,8,9):
                    return (nx, ny)
            return ghost_pos

        # === scatter corners ===
        if self.state == "scatter":
            h, w = len(maze), len(maze[0])
            corners = {
                "red":   (w - 2, 1),         # top-right
                "pink":  (1, 1),             # top-left
                "blue":  (w - 2, h - 2),     # bottom-right
                "orange":(1, h - 2)          # bottom-left
            }
            target = corners.get(ghost_color, (px, py))
        else:
            # === chase state ===
            if ghost_color == "red":
                target = (px, py)
            elif ghost_color == "pink":
                dx, dy = pac_dir
                target = (px + dx * 4, py + dy * 4)
            elif ghost_color == "blue" and blinky_pos:
                vx = px - blinky_pos[0]
                vy = py - blinky_pos[1]
                target = (px + vx, py + vy)
            elif ghost_color == "orange":
                dist = abs(gx - px) + abs(gy - py)
                if dist > 8:
                    target = (px, py)
                else:
                    h, w = len(maze), len(maze[0])
                    target = (1, h - 2)
            else:
                target = (px, py)

        # keep target within bounds
        target = (
            max(0, min(len(maze[0]) - 1, target[0])),
            max(0, min(len(maze) - 1, target[1])),
        )

        path = self.algorithm(ghost_pos, target, maze)

        # fallback: random move
        if not path or len(path) < 2:
            dirs = [(1,0), (-1,0), (0,1), (0,-1)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = gx + dx, gy + dy
                if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]) and maze[ny][nx] not in (3,4,5,6,7,8,9):
                    return (nx, ny)
            return ghost_pos

        return path[1]
