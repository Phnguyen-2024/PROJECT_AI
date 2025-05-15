import heapq
from collections import deque
from collections import defaultdict
import random

MOVE_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Directions: right, down, left, up

def get_neighbors(pos, rows, cols, tilemap):
    r, c = pos
    for dr, dc in MOVE_DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] != "T":
            yield (nr, nc)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(parent, start, goal):
    path = []
    curr = goal
    while curr and curr in parent:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path if path and path[0] == start else []

def astar(start, goal, tilemap, tile_cost):
    rows, cols = len(tilemap), len(tilemap[0])
    pq = [(0 + heuristic(start, goal), 0, start)]
    cost = {start: 0}
    parent = {start: None}

    while pq:
        _, g, curr = heapq.heappop(pq)
        if curr == goal:
            break
        for neighbor in get_neighbors(curr, rows, cols, tilemap):
            ncost = tile_cost[tilemap[neighbor[0]][neighbor[1]]]
            new_cost = g + ncost
            if ncost != float("inf") and (neighbor not in cost or new_cost < cost[neighbor]):
                cost[neighbor] = new_cost
                heapq.heappush(pq, (new_cost + heuristic(neighbor, goal), new_cost, neighbor))
                parent[neighbor] = curr
    return reconstruct_path(parent, start, goal)

def bfs(start, goal, tilemap):
    rows, cols = len(tilemap), len(tilemap[0])
    queue = deque([(start, None)])
    visited = {start}
    parent = {start: None}

    while queue:
        curr, _ = queue.popleft()
        if curr == goal:
            break
        for neighbor in get_neighbors(curr, rows, cols, tilemap):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                queue.append((neighbor, curr))
    return reconstruct_path(parent, start, goal)

def beam_search(start, goal, tilemap, beam_width=3):
    rows, cols = len(tilemap), len(tilemap[0])
    beam = [(heuristic(start, goal), start)]
    parent = {start: None}
    visited = set([start])

    while beam:
        candidates = []
        for _, pos in beam:
            for neighbor in get_neighbors(pos, rows, cols, tilemap):
                if neighbor not in visited:
                    score = heuristic(neighbor, goal)
                    candidates.append((score, neighbor))
                    visited.add(neighbor)
                    parent[neighbor] = pos

        if not candidates:
            break

        candidates.sort(key=lambda x: x[0])
        beam = candidates[:beam_width]

        for score, pos in beam:
            if pos == goal:
                return reconstruct_path(parent, start, goal)

    return []

def and_or_search(start, goal, tilemap):
    # Kiểm tra đầu vào
    if not tilemap or not tilemap[0] or \
       not (0 <= start[0] < len(tilemap) and 0 <= start[1] < len(tilemap[0])) or \
       not (0 <= goal[0] < len(tilemap) and 0 <= goal[1] < len(tilemap[0])):
        return []

    rows, cols = len(tilemap), len(tilemap[0])
    visited = set()
    solution_tree = defaultdict(list)
    max_nodes = rows * cols * 10  # Giới hạn số nút khám phá
    nodes_explored = [0]

    def get_neighbors(state):
        r, c = state
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] != "T":
                neighbors.append((nr, nc))
        return neighbors

    def is_deterministic(state):
        return tilemap[state[0]][state[1]] != "W"

    def get_possible_outcomes(state, action):
        r, c = state
        dr, dc = action
        next_state = (r + dr, c + dc)
        if is_deterministic(next_state):
            return [next_state]
        else:
            return [next_state, state]  # Ô "W" có thể giữ nguyên hoặc di chuyển

    def or_search(state):
        if nodes_explored[0] > max_nodes:
            return False, None  # Trả về None nếu vượt giới hạn
        nodes_explored[0] += 1
        if state == goal:
            return True, state
        if state in visited:
            return False, None
        visited.add(state)

        neighbors = get_neighbors(state)
        random.shuffle(neighbors)  # Ngẫu nhiên hóa để tránh thiên vị
        for next_state in neighbors:
            action = (next_state[0] - state[0], next_state[1] - state[1])
            success, result = and_search(state, action)
            if success:
                solution_tree[state].append((action, next_state))
                visited.remove(state)
                return True, next_state
        visited.remove(state)
        return False, None

    def and_search(state, action):
        outcomes = get_possible_outcomes(state, action)
        for outcome in outcomes:
            if outcome in visited:
                continue
            success, result = or_search(outcome)
            if not success:
                return False, None
        return True, state

    # Thực thi tìm kiếm
    success, _ = or_search(start)
    if not success:
        return []  # Không tìm được chiến lược đảm bảo

    # Xây dựng đường đi từ solution_tree
    path = []
    curr = start
    path.append(curr)
    seen = set([curr])
    while curr != goal and solution_tree[curr]:
        found = False
        for action, next_state in solution_tree[curr]:
            if next_state not in seen:
                path.append(next_state)
                seen.add(next_state)
                curr = next_state
                found = True
                break
        if not found:
            return []  # Không thể xây dựng đường đi hoàn chỉnh
    if curr != goal:
        return []  # Đường đi không dẫn đến mục tiêu
    return path

def backtracking(start, goal, tilemap, tile_cost):
    rows, cols = len(tilemap), len(tilemap[0])
    visited = set()
    path = []
    exploration_order = []  # Lưu thứ tự các ô được thăm

    def backtrack(curr):
        if curr == goal:
            path.append(curr)
            exploration_order.append(curr)
            return True
        if curr in visited:
            return False
        visited.add(curr)
        exploration_order.append(curr)  # Ghi lại ô hiện tại
        path.append(curr)
        for neighbor in get_neighbors(curr, rows, cols, tilemap):
            if backtrack(neighbor):
                return True
        path.pop()
        visited.remove(curr)
        return False

    if backtrack(start):
        return path, exploration_order
    return [], exploration_order

def q_learning(start, goal, tilemap, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
    rows, cols = len(tilemap), len(tilemap[0])
    actions = [(0,1), (1,0), (0,-1), (-1,0)]
    
    q_table = {}
    for r in range(rows):
        for c in range(cols):
            for a in range(len(actions)):
                q_table[((r,c), a)] = 0.0
                
    def get_valid_actions(state):
        valid = []
        r, c = state
        for i, (dr, dc) in enumerate(actions):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] != "T":
                valid.append(i)
        return valid
        
    def get_next_state(state, action):
        r, c = state
        dr, dc = actions[action]
        return (r + dr, c + dc)
        
    def get_reward(state):
        if state == goal:
            return 100
        if tilemap[state[0]][state[1]] == "T":
            return -100
        return -1
        
    for _ in range(episodes):
        state = start
        while state != goal:
            valid_actions = get_valid_actions(state)
            if not valid_actions:
                break
            if random.random() < epsilon:
                action = random.choice(valid_actions)
            else:
                action = max(valid_actions, key=lambda a: q_table[(state, a)])
            next_state = get_next_state(state, action)
            reward = get_reward(next_state)
            next_valid_actions = get_valid_actions(next_state)
            if next_valid_actions:
                max_next_q = max(q_table[(next_state, a)] for a in next_valid_actions)
            else:
                max_next_q = 0
            q_table[(state, action)] += alpha * (
                reward + gamma * max_next_q - q_table[(state, action)]
            )
            state = next_state
            
    path = []
    state = start
    while state != goal:
        path.append(state)
        valid_actions = get_valid_actions(state)
        if not valid_actions:
            return []
        action = max(valid_actions, key=lambda a: q_table[(state, a)])
        state = get_next_state(state, action)
        
    path.append(goal)
    return path