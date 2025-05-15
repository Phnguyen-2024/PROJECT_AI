# import random
# from collections import deque
# from thuattoan import bfs, reconstruct_path

# TILE_TYPES = ["G", "D", "T", "W"]
# PASSABLE_TILES = ["G", "D", "W"]
# IMPASSABLE_TILES = ["T"]
# MOVE_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# def flood_fill(tilemap, start_pos, passable_tiles):
#     """
#     Perform flood-fill to find all connected passable tiles from the start position.
#     """
#     rows, cols = len(tilemap), len(tilemap[0])
#     queue = deque([start_pos])
#     visited = {start_pos}
#     while queue:
#         r, c = queue.popleft()
#         for dr, dc in MOVE_DIRS:
#             nr, nc = r + dr, c + dc
#             if (0 <= nr < rows and 0 <= nc < cols and
#                 (nr, nc) not in visited and tilemap[nr][nc] in passable_tiles):
#                 visited.add((nr, nc))
#                 queue.append((nr, nc))
#     return visited, len(visited)

# def ensure_path(tilemap, start_pos, goal_pos):
#     """
#     Ensure a path exists from start_pos to goal_pos by modifying the map if necessary.
#     """
#     rows, cols = len(tilemap), len(tilemap[0])
#     path = bfs(start_pos, goal_pos, tilemap)
#     if not path or path[0] != start_pos:
#         parent = {}
#         queue = deque([start_pos])
#         visited = {start_pos}
#         while queue:
#             curr = queue.popleft()
#             if curr == goal_pos:
#                 break
#             for neighbor in [(curr[0] + dr, curr[1] + dc) for dr, dc in MOVE_DIRS]:
#                 if (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and
#                     neighbor not in visited and tilemap[neighbor[0]][neighbor[1]] not in IMPASSABLE_TILES):
#                     visited.add(neighbor)
#                     parent[neighbor] = curr
#                     queue.append(neighbor)
#         path = reconstruct_path(parent, start_pos, goal_pos)
#         if path:
#             for r, c in path[1:-1]:
#                 if tilemap[r][c] in IMPASSABLE_TILES:
#                     tilemap[r][c] = "G"
#     return tilemap

# def generate_random_map(rows, cols):
#     """
#     Generate a random map ensuring the starting position is not blocked and a path to the goal exists.
#     """
#     min_reachable_tiles = max(5, (rows * cols) // 10)
#     start_pos = (0, 0)
#     goal_pos = (rows - 1, cols - 1)

#     while True:
#         tilemap = [[random.choice(TILE_TYPES) for _ in range(cols)] for _ in range(rows)]
#         tilemap[start_pos[0]][start_pos[1]] = "G"
#         tilemap[goal_pos[0]][goal_pos[1]] = "X"

#         reachable_positions, reachable_count = flood_fill(tilemap, start_pos, PASSABLE_TILES + ["X"])
#         if reachable_count >= min_reachable_tiles and goal_pos in reachable_positions:
#             tilemap = ensure_path(tilemap, start_pos, goal_pos)

#             for _ in range(random.randint(3, 6)):
#                 branch_start = random.choice(list(reachable_positions))
#                 for _ in range(random.randint(2, 5)):
#                     dr, dc = random.choice(MOVE_DIRS)
#                     nr, nc = branch_start[0] + dr, branch_start[1] + dc
#                     if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] in IMPASSABLE_TILES:
#                         tilemap[nr][nc] = random.choice(PASSABLE_TILES)
#                         branch_start = (nr, nc)
#             return tilemap

# import random
# from collections import deque
# from thuattoan import bfs, reconstruct_path

# TILE_TYPES = ["G", "D", "T", "W"]
# PASSABLE_TILES = ["G", "D", "W", "X"]  # Bao gồm "X" để flood_fill đến goal
# IMPASSABLE_TILES = ["T"]
# MOVE_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# def flood_fill(tilemap, start_pos, passable_tiles):
#     """
#     Perform flood-fill to find all connected passable tiles from the start position.
#     """
#     rows, cols = len(tilemap), len(tilemap[0])
#     queue = deque([start_pos])
#     visited = {start_pos}
#     while queue:
#         r, c = queue.popleft()
#         for dr, dc in MOVE_DIRS:
#             nr, nc = r + dr, c + dc
#             if (0 <= nr < rows and 0 <= nc < cols and
#                 (nr, nc) not in visited and tilemap[nr][nc] in passable_tiles):
#                 visited.add((nr, nc))
#                 queue.append((nr, nc))
#     return visited, len(visited)

# def ensure_path(tilemap, start_pos, goal_pos):
#     """
#     Ensure a path exists from start_pos to goal_pos by modifying the map if necessary.
#     """
#     rows, cols = len(tilemap), len(tilemap[0])
#     path = bfs(start_pos, goal_pos, tilemap)
#     if not path or path[0] != start_pos or path[-1] != goal_pos:
#         # Sử dụng BFS để tạo đường đi đơn giản
#         parent = {}
#         queue = deque([start_pos])
#         visited = {start_pos}
#         while queue:
#             curr = queue.popleft()
#             if curr == goal_pos:
#                 break
#             for neighbor in [(curr[0] + dr, curr[1] + dc) for dr, dc in MOVE_DIRS]:
#                 if (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and
#                     neighbor not in visited and tilemap[neighbor[0]][neighbor[1]] not in IMPASSABLE_TILES):
#                     visited.add(neighbor)
#                     parent[neighbor] = curr
#                     queue.append(neighbor)
#         path = reconstruct_path(parent, start_pos, goal_pos)
#         if not path:
#             # Nếu không có đường đi, tạo một đường đi cơ bản bằng cách thay "T" thành "G"
#             path = [start_pos]
#             current = start_pos
#             while current != goal_pos:
#                 next_pos = None
#                 min_dist = float('inf')
#                 for dr, dc in MOVE_DIRS:
#                     nr, nc = current[0] + dr, current[1] + dc
#                     if (0 <= nr < rows and 0 <= nc < cols and
#                         (nr, nc) not in path and tilemap[nr][nc] != "T"):
#                         dist = abs(nr - goal_pos[0]) + abs(nc - goal_pos[1])
#                         if dist < min_dist:
#                             min_dist = dist
#                             next_pos = (nr, nc)
#                 if next_pos:
#                     path.append(next_pos)
#                     current = next_pos
#                 else:
#                     # Thay một ô "T" gần nhất thành "G" để tạo đường đi
#                     for r in range(rows):
#                         for c in range(cols):
#                             if tilemap[r][c] == "T" and abs(r - current[0]) + abs(c - current[1]) <= 1:
#                                 tilemap[r][c] = "G"
#                                 break
#                         else:
#                             continue
#                         break
#                     path.append(current)
#         else:
#             # Đảm bảo các ô trên đường đi là passable
#             for r, c in path[1:-1]:
#                 if tilemap[r][c] in IMPASSABLE_TILES:
#                     tilemap[r][c] = random.choice(PASSABLE_TILES[:-1])  # Tránh thay bằng "X"
#     return tilemap

# def generate_random_map(rows, cols):
#     """
#     Generate a random map ensuring the starting position is not blocked and a path to the goal exists.
#     """
#     min_reachable_tiles = max(10, (rows * cols) // 8)  # Tăng ngưỡng reachable tiles
#     start_pos = (0, 0)
#     goal_pos = (rows - 1, cols - 1)

#     while True:
#         tilemap = [[random.choice(TILE_TYPES) for _ in range(cols)] for _ in range(rows)]
#         tilemap[start_pos[0]][start_pos[1]] = "G"
#         tilemap[goal_pos[0]][goal_pos[1]] = "X"

#         # Giảm tỷ lệ chướng ngại vật "T"
#         for r in range(rows):
#             for c in range(cols):
#                 if (r, c) != start_pos and (r, c) != goal_pos:
#                     if random.random() < 0.1:  # Giảm từ 0.1 xuống 0.05
#                         tilemap[r][c] = "T"
#                     elif random.random() < 0.3:
#                         tilemap[r][c] = "D"
#                     elif random.random() < 0.5:
#                         tilemap[r][c] = "W"

#         reachable_positions, reachable_count = flood_fill(tilemap, start_pos, PASSABLE_TILES + ["X"])
#         if reachable_count >= min_reachable_tiles and goal_pos in reachable_positions:
#             tilemap = ensure_path(tilemap, start_pos, goal_pos)

#             # Thêm các nhánh ngẫu nhiên để tăng tính kết nối
#             for _ in range(random.randint(3, 6)):
#                 branch_start = random.choice(list(reachable_positions))
#                 for _ in range(random.randint(2, 5)):
#                     dr, dc = random.choice(MOVE_DIRS)
#                     nr, nc = branch_start[0] + dr, branch_start[1] + dc
#                     if (0 <= nr < rows and 0 <= nc < cols and
#                         tilemap[nr][nc] in IMPASSABLE_TILES and
#                         (nr, nc) not in [(0, 0), (rows-1, cols-1)]):
#                         tilemap[nr][nc] = random.choice(PASSABLE_TILES[:-1])
#                         branch_start = (nr, nc)

#             # Kiểm tra lại sau khi thêm nhánh
#             reachable_positions, reachable_count = flood_fill(tilemap, start_pos, PASSABLE_TILES + ["X"])
#             if reachable_count >= min_reachable_tiles and goal_pos in reachable_positions:
#                 return tilemap

import random
from collections import deque
from thuattoan import bfs, reconstruct_path

TILE_TYPES = ["G", "D", "T", "W"]
PASSABLE_TILES = ["G", "D", "W", "X"]
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
    if not path or path[0] != start_pos or path[-1] != goal_pos:
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
        if not path:
            path = [start_pos]
            current = start_pos
            while current != goal_pos:
                next_pos = None
                min_dist = float('inf')
                for dr, dc in MOVE_DIRS:
                    nr, nc = current[0] + dr, current[1] + dc
                    if (0 <= nr < rows and 0 <= nc < cols and
                        (nr, nc) not in path and tilemap[nr][nc] != "T"):
                        dist = abs(nr - goal_pos[0]) + abs(nc - goal_pos[1])
                        if dist < min_dist:
                            min_dist = dist
                            next_pos = (nr, nc)
                if next_pos:
                    path.append(next_pos)
                    current = next_pos
                else:
                    for r in range(rows):
                        for c in range(cols):
                            if tilemap[r][c] == "T" and abs(r - current[0]) + abs(c - current[1]) <= 1:
                                tilemap[r][c] = "G"
                                break
                        else:
                            continue
                        break
                    path.append(current)
        else:
            for r, c in path[1:-1]:
                if tilemap[r][c] in IMPASSABLE_TILES:
                    tilemap[r][c] = random.choice(PASSABLE_TILES[:-1])
    return tilemap

def generate_random_map(rows, cols):
    """
    Generate a random map with fewer dead ends to improve pathfinding for Beam Search.
    """
    min_reachable_tiles = max(10, (rows * cols) // 8)
    start_pos = (0, 0)
    goal_pos = (rows - 1, cols - 1)

    while True:
        tilemap = [[random.choice(TILE_TYPES) for _ in range(cols)] for _ in range(rows)]
        tilemap[start_pos[0]][start_pos[1]] = "G"
        tilemap[goal_pos[0]][goal_pos[1]] = "X"

        # Giảm tỷ lệ chướng ngại vật "T" để tạo bản đồ thoáng hơn
        for r in range(rows):
            for c in range(cols):
                if (r, c) != start_pos and (r, c) != goal_pos:
                    if random.random() < 0.2:  # Giảm từ 0.35 xuống 0.2
                        tilemap[r][c] = "T"
                    elif random.random() < 0.3:
                        tilemap[r][c] = "D"
                    elif random.random() < 0.5:
                        tilemap[r][c] = "W"

        reachable_positions, reachable_count = flood_fill(tilemap, start_pos, PASSABLE_TILES + ["X"])
        if reachable_count >= min_reachable_tiles and goal_pos in reachable_positions:
            tilemap = ensure_path(tilemap, start_pos, goal_pos)

            # Giảm số lượng nhánh và ngõ cụt
            for _ in range(random.randint(5, 10)):  # Giảm từ 10-15 xuống 5-10
                branch_start = random.choice(list(reachable_positions))
                branch_length = random.randint(4, 8)
                is_dead_end = random.random() < 0.5  # Giảm từ 0.9 xuống 0.5
                for i in range(branch_length):
                    dr, dc = random.choice(MOVE_DIRS)
                    nr, nc = branch_start[0] + dr, branch_start[1] + dc
                    if (0 <= nr < rows and 0 <= nc < cols and
                        (nr, nc) not in [(0, 0), (rows-1, cols-1)]):
                        distance_to_goal = abs(nr - goal_pos[0]) + abs(nc - goal_pos[1])
                        if distance_to_goal < 3 and is_dead_end:
                            tilemap[nr][nc] = "T"
                            break
                        if tilemap[nr][nc] in IMPASSABLE_TILES:
                            if not is_dead_end or (nr, nc) in reachable_positions:
                                tilemap[nr][nc] = random.choice(PASSABLE_TILES[:-1])
                                branch_start = (nr, nc)
                            else:
                                break
                        elif i == branch_length - 1 and is_dead_end:
                            for dr2, dc2 in MOVE_DIRS:
                                nnr, nnc = nr + dr2, nc + dc2
                                if (0 <= nnr < rows and 0 <= nnc < cols and
                                    (nnr, nnc) not in [(0, 0), (rows-1, cols-1)] and
                                    tilemap[nnr][nnc] not in IMPASSABLE_TILES):
                                    tilemap[nnr][nnc] = "T"
                                    break

            # Kiểm tra lại sau khi thêm nhánh
            reachable_positions, reachable_count = flood_fill(tilemap, start_pos, PASSABLE_TILES + ["X"])
            if reachable_count >= min_reachable_tiles and goal_pos in reachable_positions:
                return tilemap