import heapq

def heuristic(a, b):
    # a, b are (x,y)
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal, maze):
    """
    start, goal are (x,y). maze is maze[y][x].
    Return path as list of (x,y) or None.
    """
    rows, cols = len(maze), len(maze[0])
    open_set = []
    heapq.heappush(open_set, (0, start, [start]))
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    visited = set()
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    while open_set:
        current_f, current, path = heapq.heappop(open_set)
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)

        cx, cy = current
        for dx, dy in directions:
            neighbor = (cx + dx, cy + dy)
            nx, ny = neighbor
            if (0 <= nx < cols and 0 <= ny < rows and
                maze[ny][nx] not in (3, 4, 5, 6, 7, 8, 9)):

                tentative_g = g_score[current] + 1
                if neighbor in visited and tentative_g >= g_score.get(neighbor, float('inf')):
                    continue

                if tentative_g < g_score.get(neighbor, float('inf')) or neighbor not in [i[1] for i in open_set]:
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor, path + [neighbor]))
    return None
