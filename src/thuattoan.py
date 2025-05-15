import heapq
from collections import deque
from collections import defaultdict
import random
import time

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


def and_or_search_with_stats(start, goal, tilemap):
    if not tilemap or not tilemap[0] or \
       not (0 <= start[0] < len(tilemap) and 0 <= start[1] < len(tilemap[0])) or \
       not (0 <= goal[0] < len(tilemap) and 0 <= goal[1] < len(tilemap[0])) or \
       tilemap[start[0]][start[1]] == "T" or tilemap[goal[0]][goal[1]] == "T":
        return None, 0

    rows, cols = len(tilemap), len(tilemap[0])
    visited = set()
    nodes_explored = 0
    start_time = time.perf_counter()
    max_time = 5  # Giới hạn 5 giây
    max_nodes = rows * cols * 5

    def heuristic(state, goal):
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])

    def get_neighbors(state):
        r, c = state
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
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
            return [("success", next_state, 1.0)]
        else:
            return [("success", next_state, 0.7), ("failure", state, 0.3)]

    def or_search(state):
        nonlocal nodes_explored, start_time
        if time.perf_counter() - start_time > max_time or nodes_explored > max_nodes:
            return None
        nodes_explored += 1
        if state == goal:
            return []
        if state in visited:
            return None
        visited.add(state)

        neighbors = get_neighbors(state)
        neighbors.sort(key=lambda x: heuristic(x, goal))  # Ưu tiên hướng gần goal
        for next_state in neighbors:
            action = (next_state[0] - state[0], next_state[1] - state[1])
            plan = and_search(state, action)
            if plan is not None:
                visited.remove(state)
                return [(state, "action", action, next_state, plan)]
        visited.remove(state)
        return None

    def and_search(state, action):
        nonlocal nodes_explored, start_time
        if time.perf_counter() - start_time > max_time or nodes_explored > max_nodes:
            return None
        outcomes = get_possible_outcomes(state, action)
        outcomes.sort(key=lambda x: x[2], reverse=True)  # Ưu tiên xác suất cao
        sub_plans = []
        for condition, outcome, prob in outcomes:
            if outcome in visited:
                continue
            plan_i = or_search(outcome)
            if plan_i is None:
                return None
            sub_plans.append((condition, outcome, plan_i, prob))
        return sub_plans if sub_plans else None

    plan = or_search(start)
    return plan, nodes_explored

def extract_path_from_plan(plan):
    """Trích xuất một đường đi khả thi từ kế hoạch AND-OR."""
    if not plan:
        return []
    path = [plan[0][0]]  # Bắt đầu từ trạng thái đầu tiên
    curr_plan = plan
    while curr_plan:
        _, _, _, next_state, sub_plan = curr_plan[0]
        path.append(next_state)
        # Ưu tiên nhánh "success" nếu có
        next_sub_plan = None
        for condition, _, sub_plan_i, _ in sub_plan:
            if condition == "success":
                next_sub_plan = sub_plan_i
                break
        if not next_sub_plan:
            next_sub_plan = sub_plan[0][2] if sub_plan else None
        curr_plan = next_sub_plan
    return list(dict.fromkeys(path))  # Loại bỏ các phần tử trùng lặp

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

# import heapq
# from collections import deque
# from collections import defaultdict
# import random
# import time

# MOVE_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Directions: right, down, left, up

# def get_neighbors(pos, rows, cols, tilemap):
#     r, c = pos
#     for dr, dc in MOVE_DIRS:
#         nr, nc = r + dr, c + dc
#         if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] != "T":
#             yield (nr, nc)

# def heuristic(a, b):
#     return abs(a[0] - b[0]) + abs(a[1] - b[1])

# def reconstruct_path(parent, start, goal):
#     path = []
#     curr = goal
#     while curr and curr in parent:
#         path.append(curr)
#         curr = parent[curr]
#     path.reverse()
#     return path if path and path[0] == start else []

# def astar(start, goal, tilemap, tile_cost):
#     rows, cols = len(tilemap), len(tilemap[0])
#     pq = [(0 + heuristic(start, goal), 0, start)]
#     cost = {start: 0}
#     parent = {start: None}
#     nodes_explored = 0

#     while pq:
#         nodes_explored += 1
#         _, g, curr = heapq.heappop(pq)
#         if curr == goal:
#             break
#         for neighbor in get_neighbors(curr, rows, cols, tilemap):
#             ncost = tile_cost[tilemap[neighbor[0]][neighbor[1]]]
#             new_cost = g + ncost
#             if ncost != float("inf") and (neighbor not in cost or new_cost < cost[neighbor]):
#                 cost[neighbor] = new_cost
#                 heapq.heappush(pq, (new_cost + heuristic(neighbor, goal), new_cost, neighbor))
#                 parent[neighbor] = curr
    
#     path = reconstruct_path(parent, start, goal)
#     path_cost = cost.get(goal, 0) if path else 0
#     return path, path_cost, nodes_explored

# def bfs(start, goal, tilemap, tile_cost):
#     rows, cols = len(tilemap), len(tilemap[0])
#     queue = deque([(start, None)])
#     visited = {start}
#     parent = {start: None}
#     cost = {start: 0}
#     nodes_explored = 0

#     while queue:
#         nodes_explored += 1
#         curr, _ = queue.popleft()
#         if curr == goal:
#             break
#         for neighbor in get_neighbors(curr, rows, cols, tilemap):
#             if neighbor not in visited:
#                 visited.add(neighbor)
#                 parent[neighbor] = curr
#                 cost[neighbor] = cost[curr] + tile_cost[tilemap[neighbor[0]][neighbor[1]]]
#                 queue.append((neighbor, curr))
    
#     path = reconstruct_path(parent, start, goal)
#     path_cost = cost.get(goal, 0) if path else 0
#     return path, path_cost, nodes_explored

# def beam_search(start, goal, tilemap, tile_cost, beam_width=3):
#     rows, cols = len(tilemap), len(tilemap[0])
#     beam = [(heuristic(start, goal), start)]
#     parent = {start: None}
#     cost = {start: 0}
#     visited = set([start])
#     nodes_explored = 0

#     while beam:
#         candidates = []
#         for _, pos in beam:
#             for neighbor in get_neighbors(pos, rows, cols, tilemap):
#                 nodes_explored += 1
#                 if neighbor not in visited:
#                     score = heuristic(neighbor, goal)
#                     candidates.append((score, neighbor))
#                     visited.add(neighbor)
#                     parent[neighbor] = pos
#                     cost[neighbor] = cost[pos] + tile_cost[tilemap[neighbor[0]][neighbor[1]]]

#         if not candidates:
#             break

#         candidates.sort(key=lambda x: x[0])
#         beam = candidates[:beam_width]

#         for score, pos in beam:
#             if pos == goal:
#                 path = reconstruct_path(parent, start, goal)
#                 path_cost = cost.get(goal, 0) if path else 0
#                 return path, path_cost, nodes_explored

#     return [], 0, nodes_explored

# def and_or_search_with_stats(start, goal, tilemap, tile_cost):
#     if not tilemap or not tilemap[0] or \
#        not (0 <= start[0] < len(tilemap) and 0 <= start[1] < len(tilemap[0])) or \
#        not (0 <= goal[0] < len(tilemap) and 0 <= goal[1] < len(tilemap[0])) or \
#        tilemap[start[0]][start[1]] == "T" or tilemap[goal[0]][goal[1]] == "T":
#         return None, 0, 0

#     rows, cols = len(tilemap), len(tilemap[0])
#     visited = set()
#     nodes_explored = 0
#     start_time = time.perf_counter()
#     max_time = 5  # Giới hạn 5 giây
#     max_nodes = rows * cols * 5

#     def heuristic(state, goal):
#         return abs(state[0] - goal[0]) + abs(state[1] - goal[1])

#     def get_neighbors(state):
#         r, c = state
#         directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
#         neighbors = []
#         for dr, dc in directions:
#             nr, nc = r + dr, c + dc
#             if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] != "T":
#                 neighbors.append((nr, nc))
#         return neighbors

#     def is_deterministic(state):
#         return tilemap[state[0]][state[1]] != "W"

#     def get_possible_outcomes(state, action):
#         r, c = state
#         dr, dc = action
#         next_state = (r + dr, c + dc)
#         if is_deterministic(next_state):
#             return [("success", next_state, 1.0)]
#         else:
#             return [("success", next_state, 0.7), ("failure", state, 0.3)]

#     def or_search(state):
#         nonlocal nodes_explored, start_time
#         if time.perf_counter() - start_time > max_time or nodes_explored > max_nodes:
#             return None
#         nodes_explored += 1
#         if state == goal:
#             return []
#         if state in visited:
#             return None
#         visited.add(state)

#         neighbors = get_neighbors(state)
#         neighbors.sort(key=lambda x: heuristic(x, goal))  # Ưu tiên hướng gần goal
#         for next_state in neighbors:
#             action = (next_state[0] - state[0], next_state[1] - state[1])
#             plan = and_search(state, action)
#             if plan is not None:
#                 visited.remove(state)
#                 return [(state, "action", action, next_state, plan)]
#         visited.remove(state)
#         return None

#     def and_search(state, action):
#         nonlocal nodes_explored, start_time
#         if time.perf_counter() - start_time > max_time or nodes_explored > max_nodes:
#             return None
#         outcomes = get_possible_outcomes(state, action)
#         outcomes.sort(key=lambda x: x[2], reverse=True)  # Ưu tiên xác suất cao
#         sub_plans = []
#         for condition, outcome, prob in outcomes:
#             if outcome in visited:
#                 continue
#             plan_i = or_search(outcome)
#             if plan_i is None:
#                 return None
#             sub_plans.append((condition, outcome, plan_i, prob))
#         return sub_plans if sub_plans else None

#     plan = or_search(start)
#     if plan:
#         path = extract_path_from_plan(plan)
#         path_cost = 0
#         for r, c in path:
#             path_cost += tile_cost[tilemap[r][c]]
#         return plan, path_cost, nodes_explored
#     return None, 0, nodes_explored

# def extract_path_from_plan(plan):
#     """Trích xuất một đường đi khả thi từ kế hoạch AND-OR."""
#     if not plan:
#         return []
#     path = [plan[0][0]]  # Bắt đầu từ trạng thái đầu tiên
#     curr_plan = plan
#     while curr_plan:
#         _, _, _, next_state, sub_plan = curr_plan[0]
#         path.append(next_state)
#         # Ưu tiên nhánh "success" nếu có
#         next_sub_plan = None
#         for condition, _, sub_plan_i, _ in sub_plan:
#             if condition == "success":
#                 next_sub_plan = sub_plan_i
#                 break
#         if not next_sub_plan:
#             next_sub_plan = sub_plan[0][2] if sub_plan else None
#         curr_plan = next_sub_plan
#     return list(dict.fromkeys(path))  # Loại bỏ các phần tử trùng lặp

# def backtracking(start, goal, tilemap, tile_cost):
#     rows, cols = len(tilemap), len(tilemap[0])
#     visited = set()
#     path = []
#     exploration_order = []
#     nodes_explored = 0
#     path_cost = [0]  # Dùng list để có thể thay đổi trong hàm đệ quy

#     def backtrack(curr):
#         nonlocal nodes_explored
#         nodes_explored += 1
#         if curr == goal:
#             path.append(curr)
#             exploration_order.append(curr)
#             path_cost[0] += tile_cost[tilemap[curr[0]][curr[1]]]
#             return True
#         if curr in visited:
#             return False
#         visited.add(curr)
#         exploration_order.append(curr)
#         path.append(curr)
#         path_cost[0] += tile_cost[tilemap[curr[0]][curr[1]]]
#         for neighbor in get_neighbors(curr, rows, cols, tilemap):
#             if backtrack(neighbor):
#                 return True
#         path.pop()
#         path_cost[0] -= tile_cost[tilemap[curr[0]][curr[1]]]
#         visited.remove(curr)
#         return False

#     if backtrack(start):
#         return path, path_cost[0], exploration_order, nodes_explored
#     return [], 0, exploration_order, nodes_explored

# def q_learning(start, goal, tilemap, tile_cost, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
#     rows, cols = len(tilemap), len(tilemap[0])
#     actions = [(0,1), (1,0), (0,-1), (-1,0)]
#     q_table = {}
#     for r in range(rows):
#         for c in range(cols):
#             for a in range(len(actions)):
#                 q_table[((r,c), a)] = 0.0
#     nodes_explored = 0

#     def get_valid_actions(state):
#         valid = []
#         r, c = state
#         for i, (dr, dc) in enumerate(actions):
#             nr, nc = r + dr, c + dc
#             if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] != "T":
#                 valid.append(i)
#         return valid

#     def get_next_state(state, action):
#         r, c = state
#         dr, dc = actions[action]
#         return (r + dr, c + dc)

#     def get_reward(state):
#         if state == goal:
#             return 100
#         if tilemap[state[0]][state[1]] == "T":
#             return -100
#         return -1

#     for _ in range(episodes):
#         state = start
#         while state != goal:
#             nodes_explored += 1
#             valid_actions = get_valid_actions(state)
#             if not valid_actions:
#                 break
#             if random.random() < epsilon:
#                 action = random.choice(valid_actions)
#             else:
#                 action = max(valid_actions, key=lambda a: q_table[(state, a)])
#             next_state = get_next_state(state, action)
#             reward = get_reward(next_state)
#             next_valid_actions = get_valid_actions(next_state)
#             if next_valid_actions:
#                 max_next_q = max(q_table[(next_state, a)] for a in next_valid_actions)
#             else:
#                 max_next_q = 0
#             q_table[(state, action)] += alpha * (
#                 reward + gamma * max_next_q - q_table[(state, action)]
#             )
#             state = next_state

#     path = []
#     path_cost = 0
#     state = start
#     visited = set()  # Ngăn lặp vô hạn
#     while state != goal and state not in visited:
#         path.append(state)
#         path_cost += tile_cost[tilemap[state[0]][state[1]]]
#         visited.add(state)
#         valid_actions = get_valid_actions(state)
#         if not valid_actions:
#             return [], 0, nodes_explored
#         action = max(valid_actions, key=lambda a: q_table[(state, a)])
#         state = get_next_state(state, action)
#         nodes_explored += 1

#     if state == goal:
#         path.append(goal)
#         path_cost += tile_cost[tilemap[state[0]][state[1]]]
#         return path, path_cost, nodes_explored
#     return [], 0, nodes_explored