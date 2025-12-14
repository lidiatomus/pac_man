from collections import deque

def bfs(start, goal, maze):
    """
    start, goal are (x,y). maze is maze[row][col] => maze[y][x].
    Return path as list of (x,y) or None.
    """
    rows, cols = len(maze), len(maze[0])
    queue = deque([(start, [start])])
    visited = {start}
    # directions as (dx,dy) for (x,y)
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path

        cx, cy = current
        for dx, dy in directions:
            neighbor = (cx + dx, cy + dy)
            nx, ny = neighbor
            # bounds: nx in [0, cols), ny in [0, rows)
            if (0 <= nx < cols and 0 <= ny < rows and
                maze[ny][nx] not in (3, 4, 5, 6, 7, 8, 9) and
                neighbor not in visited):
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None
