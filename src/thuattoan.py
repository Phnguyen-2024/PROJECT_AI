import heapq
from collections import deque
import random

MOVE_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Directions: right, down, left, up

def get_neighbors(pos, rows, cols, tilemap):
    """
    Get valid neighboring tiles, only blocking trees ("T"), allowing water ("W").
    """
    r, c = pos
    for dr, dc in MOVE_DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and tilemap[nr][nc] != "T":
            yield (nr, nc)

def heuristic(a, b):
    """
    Manhattan distance heuristic.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(parent, start, goal):
    """
    Reconstruct the path from start to goal using the parent dictionary.
    """
    path = []
    curr = goal
    while curr and curr in parent:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path if path and path[0] == start else []

def astar(start, goal, tilemap, tile_cost):
    """
    A* Search algorithm.
    """
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
    """
    Breadth-First Search algorithm.
    """
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
    """
    Beam Search algorithm to find a path.
    """
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
    """
    AND-OR Search algorithm to find a path.
    """
    rows, cols = len(tilemap), len(tilemap[0])
    visited = set()
    parent = {start: None}
    
    def or_search(state):
        if state == goal:
            return True
        if state in visited:
            return False
        visited.add(state)
        successors = list(get_neighbors(state, rows, cols, tilemap))
        for next_state in successors:
            if and_search(next_state):
                parent[next_state] = state
                return True
        visited.remove(state)
        return False
        
    def and_search(state):
        if state == goal:
            return True
        if state in visited:
            return False
        visited.add(state)
        successors = list(get_neighbors(state, rows, cols, tilemap))
        for next_state in successors:
            if or_search(next_state):
                parent[next_state] = state
                return True
        visited.remove(state)
        return False

    if and_search(start):
        return reconstruct_path(parent, start, goal)
    return []

def backtracking(start, goal, tilemap, tile_cost):
    """
    Backtracking algorithm to find a path.
    """
    rows, cols = len(tilemap), len(tilemap[0])
    visited = set()
    path = []

    def backtrack(curr):
        if curr == goal:
            path.append(curr)
            return True
        if curr in visited:
            return False
        visited.add(curr)
        path.append(curr)
        for neighbor in get_neighbors(curr, rows, cols, tilemap):
            if backtrack(neighbor):
                return True
        path.pop()
        visited.remove(curr)
        return False

    if backtrack(start):
        return path
    return []

def q_learning(start, goal, tilemap, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
    """
    Q-Learning algorithm to find optimal path.
    """
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