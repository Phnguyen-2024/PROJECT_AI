import random
from collections import deque
from thuattoan import bfs, reconstruct_path

TILE_TYPES = ["G", "D", "T", "W"]
PASSABLE_TILES = ["G", "D", "W"]
IMPASSABLE_TILES = ["T"]
MOVE_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

def flood_fill(tilemap, start_pos, passable_tiles):
    """
    Perform flood-fill to find all connected passable tiles from the start position.
    """
    rows, cols = len(tilemap), len(tilemap[0])
    queue = deque([start_pos])
    visited = {start_pos}
    while queue:
        r, c = queue.popleft()
        for dr, dc in MOVE_DIRS:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and
                (nr, nc) not in visited and tilemap[nr][nc] in passable_tiles):
                visited.add((nr, nc))
                queue.append((nr, nc))
    return visited, len(visited)

def ensure_path(tilemap, start_pos, goal_pos):
    """
    Ensure a path exists from start_pos to goal_pos by modifying the map if necessary.
    """
    rows, cols = len(tilemap), len(tilemap[0])
    path = bfs(start_pos, goal_pos, tilemap)
    if not path or path[0] != start_pos:
        parent = {}
        queue = deque([start_pos])
        visited = {start_pos}
        while queue:
            curr = queue.popleft()
            if curr == goal_pos:
                break
            for neighbor in [(curr[0] + dr, curr[1] + dc) for dr, dc in MOVE_DIRS]:
                if (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and
                    neighbor not in visited and tilemap[neighbor[0]][neighbor[1]] not in IMPASSABLE_TILES):
                    visited.add(neighbor)
                    parent[neighbor] = curr
                    queue.append(neighbor)
        path = reconstruct_path(parent, start_pos, goal_pos)
        if path:
            for r, c in path[1:-1]:
                if tilemap[r][c] in IMPASSABLE_TILES:
                    tilemap[r][c] = "G"
    return tilemap

def generate_random_map(rows, cols):
    """
    Generate a random map ensuring the starting position is not blocked and a path to the goal exists.
    """
    min_reachable_tiles = max(5, (rows * cols) // 10)
    start_pos = (0, 0)
    goal_pos = (rows - 1, cols - 1)

    while True:
        tilemap = [[random.choice(TILE_TYPES) for _ in range(cols)] for _ in range(rows)]
        tilemap[start_pos[0]][start_pos[1]] = "G"
        tilemap[goal_pos[0]][goal_pos[1]] = "X"

        reachable_positions, reachable_count = flood_fill(tilemap, start_pos, PASSABLE_TILES + ["X"])
        if reachable_count >= min_reachable_tiles and goal_pos in reachable_positions:
            tilemap = ensure_path(tilemap, start_pos, goal_pos)

            for _ in range(random.randint(3, 6)):
                branch_start = random.choice(list(reachable_positions))
                for _ in range(random.randint(2, 5)):
                    dr, dc = random.choice(MOVE_DIRS)
                    nr, nc = branch_start[0] + dr, branch_start[1] + dc
                    if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] in IMPASSABLE_TILES:
                        tilemap[nr][nc] = random.choice(PASSABLE_TILES)
                        branch_start = (nr, nc)
            return tilemap