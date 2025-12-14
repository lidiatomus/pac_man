def dfs(start, goal, maze):
    """
    start, goal are (x,y). maze is maze[y][x].
    DFS returns path list of (x,y) or None.
    """
    rows, cols = len(maze), len(maze[0])
    stack = [(start, [start])]
    visited = {start}
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    while stack:
        current, path = stack.pop()
        if current == goal:
            return path

        cx, cy = current
        for dx, dy in directions:
            neighbor = (cx + dx, cy + dy)
            nx, ny = neighbor
            if (0 <= nx < cols and 0 <= ny < rows and
                maze[ny][nx] not in (3, 4, 5, 6, 7, 8, 9) and
                neighbor not in visited):
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))
    return None
