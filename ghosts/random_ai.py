from .bfs import bfs
from .dfs import dfs
from .astar import astar
import random

class RandomAI:
    def __init__(self, switch_algorithm=2):
        self.switch_algorithm = switch_algorithm

    def get_next_move(self, *args):
        if len(args) == 1 and isinstance(args[0], dict):
            gs = args[0]
            start = gs.get("ghost_pos")
            goal = gs.get("player_pos")
            maze = gs.get("map")
        elif len(args) == 3:
            start, goal, maze = args
        else:
            return None

        if start is None or goal is None or maze is None:
            return None

        mode = self.switch_algorithm
        if mode == 0:
            x, y = start
            rows, cols = len(maze), len(maze[0])
            neighbors = []
            for dx, dy in ((1,0), (0,1), (-1,0), (0,-1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < rows and 0 <= nx < cols and maze[ny][nx] not in (3,4,5,6,7,8,9):
                    neighbors.append((nx, ny))
            if not neighbors:
                return None
            choice = random.choice(neighbors)
            return [start, choice]
        elif mode == 1:
            return bfs(start, goal, maze)
        elif mode == 3:
            return dfs(start, goal, maze)
        else:
            return astar(start, goal, maze)
