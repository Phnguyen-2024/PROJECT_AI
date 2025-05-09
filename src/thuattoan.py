import heapq
import random

# Các hướng di chuyển (lên, xuống, trái, phải)
MOVE_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

def get_neighbors(pos, rows, cols):
    """
    Lấy các ô lân cận hợp lệ trong bản đồ.
    :param pos: Vị trí hiện tại (hàng, cột).
    :param rows: Số hàng của bản đồ.
    :param cols: Số cột của bản đồ.
    :return: Các ô lân cận hợp lệ.
    """
    r, c = pos
    for dr, dc in MOVE_DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield (nr, nc)

def heuristic(a, b):
    """
    Hàm heuristic sử dụng khoảng cách Manhattan.
    :param a: Vị trí đầu (hàng, cột).
    :param b: Vị trí đích (hàng, cột).
    :return: Giá trị heuristic.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(parent, start, goal):
    """
    Xây dựng lại đường đi từ cây cha.
    :param parent: Từ điển lưu cha của mỗi ô.
    :param start: Điểm bắt đầu.
    :param goal: Điểm đích.
    :return: Đường đi từ start đến goal.
    """
    path = []
    curr = goal
    while curr and curr in parent:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path if path and path[0] == start else []

# Uniform Cost Search (UCS)
def ucs(start, goal, tilemap, tile_cost):
    """
    Thuật toán Uniform Cost Search (UCS).
    :param start: Điểm bắt đầu (hàng, cột).
    :param goal: Điểm đích (hàng, cột).
    :param tilemap: Bản đồ các ô.
    :param tile_cost: Chi phí di chuyển qua từng loại ô.
    :return: Đường đi từ start đến goal.
    """
    rows, cols = len(tilemap), len(tilemap[0])
    pq = [(0, start)]
    cost = {start: 0}
    parent = {start: None}

    while pq:
        curr_cost, curr = heapq.heappop(pq)
        if curr == goal:
            break
        for neighbor in get_neighbors(curr, rows, cols):
            ncost = tile_cost[tilemap[neighbor[0]][neighbor[1]]]
            total = curr_cost + ncost
            if neighbor not in cost or total < cost[neighbor]:
                cost[neighbor] = total
                heapq.heappush(pq, (total, neighbor))
                parent[neighbor] = curr
    return reconstruct_path(parent, start, goal)

# Greedy Best-First Search
def greedy(start, goal, tilemap, tile_cost):
    """
    Thuật toán Greedy Best-First Search.
    :param start: Điểm bắt đầu (hàng, cột).
    :param goal: Điểm đích (hàng, cột).
    :param tilemap: Bản đồ các ô.
    :param tile_cost: Chi phí di chuyển qua từng loại ô.
    :return: Đường đi từ start đến goal.
    """
    rows, cols = len(tilemap), len(tilemap[0])
    pq = [(heuristic(start, goal), start)]
    visited = set()
    parent = {start: None}

    while pq:
        _, curr = heapq.heappop(pq)
        if curr == goal:
            break
        visited.add(curr)
        for neighbor in get_neighbors(curr, rows, cols):
            if neighbor not in visited:
                heapq.heappush(pq, (heuristic(neighbor, goal), neighbor))
                parent[neighbor] = curr
                visited.add(neighbor)
    return reconstruct_path(parent, start, goal)

# A* Search
def astar(start, goal, tilemap, tile_cost):
    """
    Thuật toán A* Search.
    :param start: Điểm bắt đầu (hàng, cột).
    :param goal: Điểm đích (hàng, cột).
    :param tilemap: Bản đồ các ô.
    :param tile_cost: Chi phí di chuyển qua từng loại ô.
    :return: Đường đi từ start đến goal.
    """
    rows, cols = len(tilemap), len(tilemap[0])
    pq = [(0 + heuristic(start, goal), 0, start)]
    cost = {start: 0}
    parent = {start: None}

    while pq:
        _, g, curr = heapq.heappop(pq)
        if curr == goal:
            break
        for neighbor in get_neighbors(curr, rows, cols):
            ncost = tile_cost[tilemap[neighbor[0]][neighbor[1]]]
            new_cost = g + ncost
            if neighbor not in cost or new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                heapq.heappush(pq, (new_cost + heuristic(neighbor, goal), new_cost, neighbor))
                parent[neighbor] = curr
    return reconstruct_path(parent, start, goal)

# Min-Conflicts Search
def min_conflicts(csp, max_steps=1000):
    """
    Thuật toán Min-Conflicts để giải bài toán ràng buộc.
    :param csp: Bài toán ràng buộc (Constraint Satisfaction Problem).
    :param max_steps: Số bước tối đa.
    :return: Lời giải hoặc thất bại.
    """
    current = csp.initial_assignment()
    for _ in range(max_steps):
        if csp.is_solution(current):
            return current
        var = random.choice(csp.get_conflicted_variables(current))
        value = min(csp.get_domain(var), key=lambda v: csp.conflicts(var, v, current))
        current[var] = value
    return None  # Trả về thất bại nếu không tìm được lời giải