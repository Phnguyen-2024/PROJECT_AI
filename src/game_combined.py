import pygame
import math
import random
import time
from thuattoan import *
from player import Player
from map_generator import generate_random_map
from utils import load_image, load_icon
from ui import load_gif_frames, show_start_screen
from collections import defaultdict

PANEL_TOP_HEIGHT = 100

class Game:
    def __init__(self, screen, tile_size, rows, cols):
        self.screen = screen
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols
    
        # Load GIF frames
        self.gif_path = r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\src\hinhnen.gif"
        self.gif_frames = load_gif_frames(self.gif_path, screen)
        self.frame_count = len(self.gif_frames)
        self.current_frame = 0
        self.frame_timer = 0

        # Load images
        self.grass_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\grass.png", tile_size)
        self.dirt_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\dirt.png", tile_size)
        self.trees_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\tree.png", tile_size)
        self.water_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\water_16px.png", tile_size)
        self.treasure_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\treasure.png", tile_size)

        # Load icons for buttons
        self.replay_icon = load_icon(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\replay_icon.png", 24)
        self.pause_icon = load_icon(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\pause_icon.png", 24)

        # Load win and lose sounds
        try:
            self.win_sound = pygame.mixer.Sound(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\win.mp3")
            self.lose_sound = pygame.mixer.Sound(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\losing.mp3")
        except pygame.error as e:
            print(f"Cannot load sound: {e}")
            self.win_sound = None
            self.lose_sound = None

        # Initialize map and positions
        self.tilemap = generate_random_map(self.rows, self.cols)
        self.start_pos = (0, 0)
        self.goal_pos = (self.rows - 1, self.cols - 1)
        self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"

        # Initialize player
        blocky_sprite = pygame.image.load(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\blocky.png")
        self.player = Player(screen, blocky_sprite, start_pos=self.start_pos, tile_size=tile_size)

        # Game state
        self.steps = 0
        self.font = pygame.font.SysFont("Times New Roman", 28)
        self.win_font = pygame.font.SysFont("Times New Roman", 60)
        self.paused = False
        self.level = 1
        self.new_level_ready = False

        # Timer state
        self.time_limit = 60
        self.time_left = self.time_limit
        self.last_time_update = pygame.time.get_ticks()

        # Path finding state
        self.path = []
        self.path_index = 0
        self.last_move_time = 0
        self.move_delay = 200
        self.current_algorithm = "astar"
        self.show_path = False
        self.auto_move_enabled = False
        self.plan = None  # Lưu kế hoạch AND-OR

        # Tile costs for A*, Backtracking, and Q-Learning
        self.tile_cost = {
            "G": 1, "D": 2, "T": float("inf"), "W": 3, "X": 1
        }

        # Path and exploration overlays
        # self.path_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        # self.path_overlay.fill((255, 255, 0, 200))
        # self.exploration_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        # self.exploration_overlay.fill((0, 255, 0, 64))
        # self.explored_tiles = set()
        # self.exploration_index = 0
        # self.exploration_list = []
        # self.last_explore_time = 0
        # self.explore_delay = 50
        # self.is_exploring = False

        self.path_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.path_overlay.fill((255, 255, 0, 200))
        self.exploration_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.exploration_overlay.fill((0, 255, 0, 100))  # Đậm hơn: từ 64 -> 100
        self.active_exploration_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.active_exploration_overlay.fill((0, 255, 0, 200))  # Đậm hơn: từ 128 -> 200
        self.explored_tiles = set()
        self.exploration_index = 0
        self.exploration_list = []
        self.last_explore_time = 0
        self.explore_delay = 300
        self.is_exploring = False
        self.current_explored_tile = None

        # Statistics for algorithms
        self.stats = {
            "astar": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "bfs": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "beam_search": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "and_or_search": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "backtracking": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "q_learning": {"time": 0, "cost": 0, "nodes": 0, "steps": 0}
        }
        self.show_stats = False

        # Compute initial statistics for the starting map
        self.compute_all_stats()

    def draw_tilemap(self):
        for row in range(len(self.tilemap)):
            for col in range(len(self.tilemap[row])):
                tile = self.tilemap[row][col]
                x = col * self.tile_size
                y = row * self.tile_size + PANEL_TOP_HEIGHT

                if tile == "G":
                    self.screen.blit(self.grass_img, (x, y))
                elif tile == "D":
                    self.screen.blit(self.dirt_img, (x, y))
                elif tile == "T":
                    self.screen.blit(self.trees_img, (x, y))
                elif tile == "W":
                    self.screen.blit(self.water_img, (x, y))
                elif tile == "X":
                    self.screen.blit(self.treasure_img, (x, y))

                # # if self.current_algorithm in ["backtracking", "and_or_search"] and (row, col) in self.explored_tiles:
                # #     self.screen.blit(self.exploration_overlay, (x, y))

                # if self.current_algorithm == "backtracking":
                #     if (row, col) == self.current_explored_tile:
                #         self.screen.blit(self.active_exploration_overlay, (x, y))
                #     elif (row, col) in self.explored_tiles:
                #         self.screen.blit(self.exploration_overlay, (x, y))

                if self.current_algorithm in ["backtracking", "and_or_search"]:
                    if (row, col) == self.current_explored_tile:
                        self.screen.blit(self.active_exploration_overlay, (x, y))
                    elif (row, col) in self.explored_tiles:
                        self.screen.blit(self.exploration_overlay, (x, y))

                if self.show_path and self.path and (row, col) in self.path and (row, col) != self.goal_pos:
                    self.screen.blit(self.path_overlay, (x, y))

                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, self.tile_size, self.tile_size), 1)

    def draw_ui(self):
        algo_text = self.font.render(f"Algorithm: {self.current_algorithm.replace('_', ' ').upper()}", True, (255, 255, 255))
        self.screen.blit(algo_text, (self.screen.get_width() - algo_text.get_width() - 10, 10))
        time_text = self.font.render(f"Time: {int(self.time_left)}", True, (255, 255, 255))
        self.screen.blit(time_text, (self.screen.get_width() - time_text.get_width() - 10, 45))

        # # Thông báo cho AND-OR Search
        # if self.current_algorithm == "and_or_search":
        #     water_count = sum(row.count("W") for row in self.tilemap)
        #     if water_count < 5:
        #         warning_text = self.font.render("Few 'W' tiles: AND-OR may act like Backtracking", True, (255, 255, 0))
        #         self.screen.blit(warning_text, (10, 80))
        #     else:
        #         info_text = self.font.render("AND-OR Search: Handles uncertain 'W' tiles", True, (255, 255, 255))
        #         self.screen.blit(info_text, (10, 80))
            # Không hiển thị kế hoạch trên UI nữa, đã in ra terminal
            # if self.plan is not None:
            #     y_offset = 120
            #     y_offset = self.draw_plan(self.plan, 10, y_offset)

        if self.new_level_ready:
            start_text = self.font.render("Press Enter to start!", True, (255, 255, 0))
            self.screen.blit(start_text, (self.screen.get_width() // 2 - start_text.get_width() // 2, self.screen.get_height() // 2))

    def draw_plan(self, plan, x, y, indent=0):
        # Giữ nguyên hàm này để tương thích với các phần khác nếu cần
        if not plan:
            return y
        state, _, action, next_state, sub_plan = plan[0]
        action_text = f"From {state}: Move {action} to {next_state}"
        text = self.font.render("  " * indent + action_text, True, (255, 255, 255))
        self.screen.blit(text, (x, y))
        y += 20
        for condition, outcome, sub_plan_i, prob in sub_plan:
            condition_text = f"If {condition} → {outcome} (prob: {prob:.1%})"
            text = self.font.render("  " * (indent + 1) + condition_text, True, (255, 255, 0))
            self.screen.blit(text, (x, y))
            y += 20
            y = self.draw_plan(sub_plan_i, x, y, indent + 2)
        return y

    def print_plan_to_terminal(self, plan, tilemap):
        if plan is None:
            print("No strategy ensures reaching goal.")
            return

        def print_plan_recursive(plan, indent=0):
            for state, action_type, action, next_state, sub_plan in [plan] if isinstance(plan, tuple) else plan:
                if action_type == "action":
                    tile = tilemap[state[0]][state[1]] if 0 <= state[0] < len(tilemap) and 0 <= state[1] < len(tilemap[0]) else "?"
                    next_tile = tilemap[next_state[0]][next_state[1]] if 0 <= next_state[0] < len(tilemap) and 0 <= next_state[1] < len(tilemap[0]) else "?"
                    print("  " * indent + f"From {state} ({tile}): Move {action} to {next_state} ({next_tile})")
                    if sub_plan:
                        for condition, outcome, sub_plan_i, prob in sub_plan:
                            print("  " * (indent + 1) + f"If {condition} ({prob*100:.0f}%) -> {outcome}")
                            print_plan_recursive(sub_plan_i, indent + 2)
                else:
                    print("  " * indent + f"Unexpected action type: {action_type}")

        print("\nAND-OR Search Plan:")
        print_plan_recursive(plan)
        print(f"Total nodes explored: {self.stats['and_or_search']['nodes_explored']}")
        print(f"Time taken: {self.stats['and_or_search']['time_taken']:.2f} seconds\n")

    def draw_stats_table(self):
        table_width = 700
        table_height = 400
        table_x = (self.screen.get_width() - table_width) // 2
        table_y = (self.screen.get_height() - table_height) // 2
        table_surface = pygame.Surface((table_width, table_height))
        table_surface.fill((255, 255, 255))

        pygame.draw.rect(table_surface, (0, 0, 0), (0, 0, table_width, table_height), 2)

        algo_col_width = 180
        other_col_width = 110
        row_height = 40
        header_font = pygame.font.SysFont("Times New Roman", 24, bold=True)
        cell_font = pygame.font.SysFont("Times New Roman", 20)
        title_font = pygame.font.SysFont("Times New Roman", 30, bold=True)

        title_text = title_font.render("So sánh thuật toán", True, (0, 0, 255))
        title_rect = title_text.get_rect(center=(table_width // 2, 30))
        table_surface.blit(title_text, title_rect)

        headers = ["Algorithm", "Time (s)", "Cost", "Nodes", "Steps"]
        algorithms = ["astar", "bfs", "beam_search", "and_or_search", "backtracking", "q_learning"]

        col_positions = [20]
        col_positions.append(col_positions[-1] + algo_col_width)
        col_positions.append(col_positions[-1] + other_col_width)
        col_positions.append(col_positions[-1] + other_col_width)
        col_positions.append(col_positions[-1] + other_col_width)

        header_y = 70
        for i, header in enumerate(headers):
            pygame.draw.rect(table_surface, (200, 200, 200), (col_positions[i], header_y, 
                            algo_col_width if i == 0 else other_col_width, row_height))
            pygame.draw.rect(table_surface, (0, 0, 0), (col_positions[i], header_y, 
                            algo_col_width if i == 0 else other_col_width, row_height), 1)
            text = header_font.render(header, True, (0, 0, 0))
            text_rect = text.get_rect(center=(col_positions[i] + (algo_col_width if i == 0 else other_col_width) // 2, header_y + row_height // 2))
            table_surface.blit(text, text_rect)

        for row, algo in enumerate(algorithms):
            row_y = header_y + (row + 1) * row_height
            row_color = (240, 240, 240) if row % 2 else (255, 255, 255)
            for i in range(len(headers)):
                pygame.draw.rect(table_surface, row_color, (col_positions[i], row_y, 
                                algo_col_width if i == 0 else other_col_width, row_height))
                pygame.draw.rect(table_surface, (0, 0, 0), (col_positions[i], row_y, 
                                algo_col_width if i == 0 else other_col_width, row_height), 1)

            text = cell_font.render(algo.replace('_', ' ').upper(), True, (0, 0, 0))
            text_rect = text.get_rect(center=(col_positions[0] + algo_col_width // 2, row_y + row_height // 2))
            table_surface.blit(text, text_rect)

            time_val = f"{self.stats[algo]['time']:.6f}"
            text = cell_font.render(time_val, True, (0, 0, 0))
            text_rect = text.get_rect(center=(col_positions[1] + other_col_width // 2, row_y + row_height // 2))
            table_surface.blit(text, text_rect)

            cost_val = f"{self.stats[algo]['cost']}"
            text = cell_font.render(cost_val, True, (0, 0, 0))
            text_rect = text.get_rect(center=(col_positions[2] + other_col_width // 2, row_y + row_height // 2))
            table_surface.blit(text, text_rect)

            nodes_val = f"{self.stats[algo]['nodes']}"
            text = cell_font.render(nodes_val, True, (0, 0, 0))
            text_rect = text.get_rect(center=(col_positions[3] + other_col_width // 2, row_y + row_height // 2))
            table_surface.blit(text, text_rect)

            steps_val = f"{self.stats[algo]['steps']}"
            text = cell_font.render(steps_val, True, (0, 0, 0))
            text_rect = text.get_rect(center=(col_positions[4] + other_col_width // 2, row_y + row_height // 2))
            table_surface.blit(text, text_rect)

        close_button_rect = pygame.Rect(table_width - 120, table_height - 50, 100, 40)
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_in_table = (mouse_pos[0] - table_x, mouse_pos[1] - table_y)
        close_color = (255, 215, 0) if close_button_rect.collidepoint(mouse_pos_in_table) else (160, 82, 45)
        pygame.draw.rect(table_surface, close_color, close_button_rect, border_radius=8)
        close_text = cell_font.render("Close", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_button_rect.center)
        table_surface.blit(close_text, close_text_rect)

        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(table_surface, (table_x, table_y))
        return close_button_rect.move(table_x, table_y)

    def compute_path(self):
        self.path = []
        self.path_index = 0
        self.explored_tiles.clear()
        self.exploration_list = []
        self.exploration_index = 0
        self.is_exploring = False
        self.show_path = True
        self.plan = None  # Reset kế hoạch

        start_time = time.perf_counter()
        nodes_explored = 0
        path = []
        max_time = 5  # Giới hạn 5 giây

        if self.current_algorithm == "astar":
            path, nodes_explored = self.astar_with_stats(self.start_pos, self.goal_pos, self.tilemap, self.tile_cost)
        elif self.current_algorithm == "bfs":
            path, nodes_explored = self.bfs_with_stats(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "beam_search":
            path, nodes_explored = self.beam_search_with_stats(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "and_or_search":
            self.is_exploring = True
            self.plan, nodes_explored = and_or_search_with_stats(self.start_pos, self.goal_pos, self.tilemap)
            self.stats["and_or_search"]["nodes_explored"] = nodes_explored  # Lưu số node
            self.stats["and_or_search"]["time_taken"] = time.perf_counter() - start_time  # Lưu thời gian
            if self.plan:
                path = extract_path_from_plan(self.plan)
                self.exploration_list = path
                self.explored_tiles = set(self.exploration_list)
                # In kế hoạch ra terminal
                self.print_plan_to_terminal(self.plan, self.tilemap)
            else:
                print("AND-OR Search: No strategy ensures reaching goal due to uncertain 'W' tiles")
        elif self.current_algorithm == "backtracking":
            self.is_exploring = True
            path, nodes_explored, exploration_order = self.backtracking_with_stats(self.start_pos, self.goal_pos, self.tilemap, self.tile_cost)
            self.exploration_list = exploration_order
            self.explored_tiles = set()
        elif self.current_algorithm == "q_learning":
            path, nodes_explored = self.q_learning_with_stats(self.start_pos, self.goal_pos, self.tilemap)

        end_time = time.perf_counter()
        time_taken = end_time - start_time
        if time_taken > max_time:
            print(f"{self.current_algorithm} timed out")
            path = []
            time_taken = 0
            nodes_explored = 0

        path_cost = self.calculate_path_cost(path) if path else 0
        steps = len(path) - 1 if path else 0

        self.path = path
        if path:
            print(f"{self.current_algorithm} path: {path}")
            print(f"Tilemap at path: {[self.tilemap[r][c] for r, c in path]}")
            self.stats[self.current_algorithm] = {
                "time": time_taken,
                "cost": path_cost,
                "nodes": nodes_explored,
                "steps": steps
            }
        else:
            print(f"{self.current_algorithm} found no path")
            if self.current_algorithm == "and_or_search":
                print("AND-OR Search: No strategy ensures reaching goal due to uncertain 'W' tiles")
            self.stats[self.current_algorithm] = {"time": 0, "cost": 0, "nodes": nodes_explored, "steps": 0}

    def extract_one_path(self, plan):
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

    def compute_all_stats(self):
        algorithms = ["astar", "bfs", "beam_search", "and_or_search", "backtracking", "q_learning"]
        original_algorithm = self.current_algorithm
        original_path = self.path
        original_explored_tiles = self.explored_tiles.copy()
        original_exploration_list = self.exploration_list.copy()
        original_is_exploring = self.is_exploring
        original_show_path = self.show_path
        original_plan = self.plan

        for algo in algorithms:
            self.current_algorithm = algo
            self.compute_path()

        self.current_algorithm = original_algorithm
        self.path = original_path
        self.explored_tiles = original_explored_tiles
        self.exploration_list = original_exploration_list
        self.is_exploring = original_is_exploring
        self.show_path = original_show_path
        self.plan = original_plan

    def calculate_path_cost(self, path):
        if not path:
            return 0
        cost = 0
        for r, c in path:
            tile = self.tilemap[r][c]
            cost += self.tile_cost.get(tile, 0)
        return cost

    def astar_with_stats(self, start, goal, tilemap, tile_cost):
        rows, cols = len(tilemap), len(tilemap[0])
        pq = [(0 + heuristic(start, goal), 0, start)]
        cost = {start: 0}
        parent = {start: None}
        nodes_explored = 0

        while pq:
            nodes_explored += 1
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
        path = reconstruct_path(parent, start, goal)
        return path, nodes_explored

    def bfs_with_stats(self, start, goal, tilemap):
        rows, cols = len(tilemap), len(tilemap[0])
        queue = deque([(start, None)])
        visited = {start}
        parent = {start: None}
        nodes_explored = 0

        while queue:
            nodes_explored += 1
            curr, _ = queue.popleft()
            if curr == goal:
                break
            for neighbor in get_neighbors(curr, rows, cols, tilemap):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = curr
                    queue.append((neighbor, curr))
        path = reconstruct_path(parent, start, goal)
        return path, nodes_explored

    def beam_search_with_stats(self, start, goal, tilemap, beam_width=3):
        rows, cols = len(tilemap), len(tilemap[0])
        beam = [(heuristic(start, goal), start)]
        parent = {start: None}
        visited = set([start])
        nodes_explored = 0

        while beam:
            candidates = []
            for _, pos in beam:
                for neighbor in get_neighbors(pos, rows, cols, tilemap):
                    nodes_explored += 1
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
                    path = reconstruct_path(parent, start, goal)
                    return path, nodes_explored

        return [], nodes_explored

    def backtracking_with_stats(self, start, goal, tilemap, tile_cost):
        rows, cols = len(tilemap), len(tilemap[0])
        visited = set()
        path = []
        exploration_order = []
        nodes_explored = 0

        def backtrack(curr):
            nonlocal nodes_explored
            nodes_explored += 1
            if curr == goal:
                path.append(curr)
                exploration_order.append(curr)
                return True
            if curr in visited:
                return False
            visited.add(curr)
            exploration_order.append(curr)
            path.append(curr)
            for neighbor in get_neighbors(curr, rows, cols, tilemap):
                if backtrack(neighbor):
                    return True
            path.pop()
            visited.remove(curr)
            return False

        if backtrack(start):
            return path, nodes_explored, exploration_order
        return [], nodes_explored, exploration_order

    def q_learning_with_stats(self, start, goal, tilemap, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
        rows, cols = len(tilemap), len(tilemap[0])
        actions = [(0,1), (1,0), (0,-1), (-1,0)]
        q_table = {}
        for r in range(rows):
            for c in range(cols):
                for a in range(len(actions)):
                    q_table[((r,c), a)] = 0.0
        nodes_explored = 0

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
                return -10
            return -1

        for _ in range(episodes):
            state = start
            while state != goal:
                nodes_explored += 1
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
        visited = set()  # Ngăn lặp vô hạn
        while state != goal and state not in visited:
            path.append(state)
            visited.add(state)
            valid_actions = get_valid_actions(state)
            if not valid_actions:
                return [], nodes_explored
            action = max(valid_actions, key=lambda a: q_table[(state, a)])
            state = get_next_state(state, action)
            nodes_explored += 1

        if state == goal:
            path.append(goal)
            return path, nodes_explored
        return [], nodes_explored

    def update_exploration(self):
        if not self.is_exploring or self.current_algorithm not in ["backtracking", "and_or_search"]:
            return
        current_time = pygame.time.get_ticks()
        # if self.exploration_index < len(self.exploration_list) and current_time - self.last_explore_time > self.explore_delay:
        #     tile = self.exploration_list[self.exploration_index]
        #     self.explored_tiles.add(tile)
        #     self.exploration_index += 1
        #     self.last_explore_time = current_time
        # elif self.exploration_index >= len(self.exploration_list):
        #     self.is_exploring = False

        if self.exploration_index < len(self.exploration_list) and current_time - self.last_explore_time > self.explore_delay:
            if self.current_explored_tile:
                self.explored_tiles.add(self.current_explored_tile)
            self.current_explored_tile = self.exploration_list[self.exploration_index]
            self.exploration_index += 1
            self.last_explore_time = current_time
        elif self.exploration_index >= len(self.exploration_list):
            if self.current_explored_tile:
                self.explored_tiles.add(self.current_explored_tile)
            self.current_explored_tile = None
            self.is_exploring = False

    def follow_path(self):
        if self.is_exploring or self.paused or self.new_level_ready or not self.auto_move_enabled:
            return
        current_time = pygame.time.get_ticks()
        if self.path and self.path_index < len(self.path) and current_time - self.last_move_time > self.move_delay:
            next_pos = self.path[self.path_index]
            direction = None
            curr_row, curr_col = self.player.row, self.player.col
            next_row, next_col = next_pos
            if next_row == curr_row - 1:
                direction = "UP"
            elif next_row == curr_row + 1:
                direction = "DOWN"
            elif next_col == curr_col - 1:
                direction = "LEFT"
            elif next_col == curr_col + 1:
                direction = "RIGHT"
            if direction:
                if self.player.move(direction, self.rows, self.cols, self.tilemap):
                    self.steps += 1
                    self.start_pos = (self.player.row, self.player.col)
                    self.path_index += 1
                    self.last_move_time = current_time
                else:
                    print(f"Failed to move {direction} to {next_pos}")

    def check_goal(self):
        return (self.player.row, self.player.col) == self.goal_pos

    def set_time_limit(self):
        if self.level == 1:
            self.time_limit = 60
        elif self.level == 2:
            self.time_limit = 40
        elif self.level == 3:
            self.time_limit = 20
        self.time_left = self.time_limit
        self.last_time_update = pygame.time.get_ticks()

    def reset_stats(self):
        self.stats = {
            "astar": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "bfs": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "beam_search": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "and_or_search": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "backtracking": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
            "q_learning": {"time": 0, "cost": 0, "nodes": 0, "steps": 0}
        }

    def reset_for_new_level(self):
        self.start_pos = (0, 0)
        self.tilemap = generate_random_map(self.rows, self.cols)
        self.goal_pos = (self.rows - 1, self.cols - 1)
        self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"
        self.player.row, self.player.col = self.start_pos
        self.steps = 0
        self.path = []
        self.path_index = 0
        self.explored_tiles.clear()
        self.exploration_list = []
        self.exploration_index = 0
        self.is_exploring = False
        self.auto_move_enabled = False
        self.show_path = False
        self.plan = None  # Reset kế hoạch
        self.set_time_limit()
        self.new_level_ready = True
        self.reset_stats()
        self.compute_all_stats()

    def reset_game(self):
        self.level = 1
        self.steps = 0
        self.start_pos = (0, 0)
        self.tilemap = generate_random_map(self.rows, self.cols)
        self.goal_pos = (self.rows - 1, self.cols - 1)
        self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"
        self.player.row, self.player.col = self.start_pos
        self.path = []
        self.path_index = 0
        self.explored_tiles.clear()
        self.exploration_list = []
        self.exploration_index = 0
        self.is_exploring = False
        self.auto_move_enabled = False
        self.show_path = False
        self.plan = None  # Reset kế hoạch
        self.set_time_limit()
        self.new_level_ready = False
        self.paused = False
        self.reset_stats()
        self.compute_all_stats()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        close_button_rect = None

        while running:
            try:
                if self.gif_frames and not self.paused:
                    self.frame_timer += 1
                    if self.frame_timer >= 10:
                        self.current_frame = (self.current_frame + 1) % self.frame_count
                        self.frame_timer = 0
                    self.screen.blit(self.gif_frames[self.current_frame], (0, 0))
                else:
                    self.screen.fill((0, 105, 148), (0, 0, self.screen.get_width(), PANEL_TOP_HEIGHT))
            except pygame.error as e:
                print(f"Error rendering top panel background: {e}")

            self.screen.fill((30, 30, 30), (0, PANEL_TOP_HEIGHT, self.screen.get_width(), self.screen.get_height() - PANEL_TOP_HEIGHT))
            self.draw_tilemap()
            self.player.render()
            self.draw_ui()

            if not self.paused and not self.new_level_ready:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_time_update >= 1000:
                    self.time_left -= 1
                    self.last_time_update = current_time

            try:
                button_font = pygame.font.SysFont("timesnewroman", 18, bold=True)
                button_width, button_height = 90, 35
                icon_button_size = 40
                button_spacing = 10

                top_row_y = 10
                replay_button_rect = pygame.Rect((self.screen.get_width() - 2 * icon_button_size - button_spacing) // 2, top_row_y, icon_button_size, icon_button_size)
                pause_button_rect = pygame.Rect((self.screen.get_width() - 2 * icon_button_size - button_spacing) // 2 + icon_button_size + button_spacing, top_row_y, icon_button_size, icon_button_size)

                bottom_row_y = 55
                random_map_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2, bottom_row_y, button_width, button_height)
                help_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + button_width + button_spacing, bottom_row_y, button_width, button_height)
                stats_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + 2 * (button_width + button_spacing), bottom_row_y, button_width, button_height)
                exit_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + 3 * (button_width + button_spacing), bottom_row_y, button_width, button_height)

                mouse_pos = pygame.mouse.get_pos()
                replay_color = (255, 215, 0) if replay_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                pause_color = (255, 215, 0) if pause_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                random_map_color = (255, 215, 0) if random_map_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                help_color = (255, 215, 0) if help_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                stats_color = (255, 215, 0) if stats_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                exit_color = (255, 215, 0) if exit_button_rect.collidepoint(mouse_pos) else (160, 82, 45)

                pygame.draw.rect(self.screen, replay_color, replay_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, pause_color, pause_button_rect, border_radius=8)
                self.screen.blit(self.replay_icon, (replay_button_rect.x + (icon_button_size - self.replay_icon.get_width()) // 2, replay_button_rect.y + (icon_button_size - self.replay_icon.get_height()) // 2))
                self.screen.blit(self.pause_icon, (pause_button_rect.x + (icon_button_size - self.pause_icon.get_width()) // 2, pause_button_rect.y + (icon_button_size - self.pause_icon.get_height()) // 2))

                pygame.draw.rect(self.screen, random_map_color, random_map_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, help_color, help_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, stats_color, stats_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, exit_color, exit_button_rect, border_radius=8)

                random_map_text = button_font.render("Random", True, (255, 255, 255))
                help_text = button_font.render("Help", True, (255, 255, 255))
                stats_text = button_font.render("Statistics", True, (255, 255, 255))
                exit_text = button_font.render("Exit", True, (255, 255, 255))

                self.screen.blit(random_map_text, random_map_text.get_rect(center=random_map_button_rect.center))
                self.screen.blit(help_text, help_text.get_rect(center=help_button_rect.center))
                self.screen.blit(stats_text, stats_text.get_rect(center=stats_button_rect.center))
                self.screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))

                steps_text = self.font.render(f"Steps: {self.steps}", True, (0, 255, 128), (0, 0, 0))
                level_text = self.font.render(f"Level: {self.level}", True, (255, 165, 0), (0, 0, 0))
                self.screen.blit(steps_text, (10, 10))
                self.screen.blit(level_text, (10, 45))

            except pygame.error as e:
                print(f"Error rendering buttons: {e}")

            if self.show_stats:
                close_button_rect = self.draw_stats_table()

            self.update_exploration()
            self.follow_path()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if replay_button_rect.collidepoint(event.pos):
                        self.reset_game()
                    elif random_map_button_rect.collidepoint(event.pos):
                        self.tilemap = generate_random_map(self.rows, self.cols)
                        self.goal_pos = (self.rows - 1, self.cols - 1)
                        self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"
                        self.player.row, self.player.col = self.start_pos
                        self.steps = 0
                        self.path = []
                        self.auto_move_enabled = False
                        self.show_path = False
                        self.set_time_limit()
                        self.new_level_ready = False
                        self.reset_stats()
                        self.compute_all_stats()
                    elif help_button_rect.collidepoint(event.pos):
                        self.compute_path()
                    elif pause_button_rect.collidepoint(event.pos):
                        self.paused = not self.paused
                    elif stats_button_rect.collidepoint(event.pos):
                        self.show_stats = not self.show_stats
                    elif exit_button_rect.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        show_start_screen(self.screen)
                        return "MAIN_MENU"
                    elif self.show_stats and close_button_rect and close_button_rect.collidepoint(event.pos):
                        self.show_stats = False
                elif event.type == pygame.KEYDOWN and not self.paused:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.player.move("UP", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.player.move("DOWN", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.player.move("LEFT", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.player.move("RIGHT", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_SPACE:
                        self.compute_path()
                        self.auto_move_enabled = True
                    elif event.key == pygame.K_1:
                        self.current_algorithm = "astar"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                        print("Selected A*")
                    elif event.key == pygame.K_2:
                        self.current_algorithm = "bfs"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                        print("Selected BFS")
                    elif event.key == pygame.K_3:
                        self.current_algorithm = "beam_search"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                        print("Selected Beam Search")
                    elif event.key == pygame.K_4:
                        self.current_algorithm = "and_or_search"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                        #print("Selected AND-OR Search: Handles uncertain 'W' tiles")
                    elif event.key == pygame.K_5:
                        self.current_algorithm = "backtracking"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                        print("Selected Backtracking")
                    elif event.key == pygame.K_6:
                        self.current_algorithm = "q_learning"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                        print("Selected Q-Learning")
                    elif event.key == pygame.K_RETURN and self.new_level_ready:
                        self.new_level_ready = False
                        self.last_time_update = pygame.time.get_ticks()

            if self.time_left <= 0 and not self.paused and not self.new_level_ready:
                game_over_text = self.win_font.render("TIME OUT!", True, (255, 0, 0))
                shadow_text = self.win_font.render("TIME OUT!", True, (0, 0, 0))
                self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 + 3, self.screen.get_height() // 2 + 3))
                self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 - 3, self.screen.get_height() // 2 - 3))
                self.screen.blit(game_over_text, (self.screen.get_width() // 2 - game_over_text.get_width() // 2, self.screen.get_height() // 2))
                if self.lose_sound:
                    self.lose_sound.play()
                pygame.display.flip()
                pygame.time.wait(3000)
                self.reset_game()

            if self.check_goal() and not self.paused and not self.new_level_ready:
                if self.win_sound:
                    self.win_sound.play()

                if self.level >= 3:
                    final_win_text = self.win_font.render("CONGRATULATIONS!", True, (255, 215, 0))
                    shadow_text = self.win_font.render("CONGRATULATIONS!", True, (245, 245, 220))
                    self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 + 3, self.screen.get_height() // 2 + 3))
                    self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 - 3, self.screen.get_height() // 2 - 3))
                    self.screen.blit(final_win_text, (self.screen.get_width() // 2 - final_win_text.get_width() // 2, self.screen.get_height() // 2))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    pygame.mixer.music.stop()  # Dừng nhạc game nếu có
                    self.reset_game()  # Reset game về level 1 và trạng thái ban đầu
                    show_start_screen(self.screen)  # Hiển thị giao diện chính
                    return "MAIN_MENU"  # Trả về trạng thái để main.py xử lý
                else:
                    you_win_text = self.win_font.render("YOU WIN!", True, (255, 255, 0))
                    shadow_text = self.win_font.render("YOU WIN!", True, (0, 0, 0))
                    self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 + 3, self.screen.get_height() // 2 + 3))
                    self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 - 3, self.screen.get_height() // 2 - 3))
                    self.screen.blit(you_win_text, (self.screen.get_width() // 2 - you_win_text.get_width() // 2, self.screen.get_height() // 2))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    self.level += 1
                    self.reset_for_new_level()

            pygame.display.flip()
            clock.tick(60)

        return "Level Complete"


# import pygame
# import math
# import random
# import time
# from thuattoan import *
# from player import Player
# from map_generator import generate_random_map
# from utils import load_image, load_icon
# from ui import load_gif_frames, show_start_screen
# from collections import defaultdict

# PANEL_TOP_HEIGHT = 100

# class Game:
#     def __init__(self, screen, tile_size, rows, cols):
#         self.screen = screen
#         self.tile_size = tile_size
#         self.rows = rows
#         self.cols = cols
    
#         # Load GIF frames
#         self.gif_path = r"D:\PROJECT_AI\src\hinhnen.gif"
#         self.gif_frames = load_gif_frames(self.gif_path, screen)
#         self.frame_count = len(self.gif_frames)
#         self.current_frame = 0
#         self.frame_timer = 0

#         # Load images
#         self.grass_img = load_image(r"D:\PROJECT_AI\assets\map\grass.png", tile_size)
#         self.dirt_img = load_image(r"D:\PROJECT_AI\assets\map\dirt.png", tile_size)
#         self.trees_img = load_image(r"D:\PROJECT_AI\assets\map\tree.png", tile_size)
#         self.water_img = load_image(r"D:\PROJECT_AI\assets\map\water_16px.png", tile_size)
#         self.treasure_img = load_image(r"D:\PROJECT_AI\assets\map\treasure.png", tile_size)

#         # Load icons for buttons
#         self.replay_icon = load_icon(r"D:\PROJECT_AI\assets\replay_icon.png", 24)
#         self.pause_icon = load_icon(r"D:\PROJECT_AI\assets\pause_icon.png", 24)

#         # Load win and lose sounds
#         try:
#             self.win_sound = pygame.mixer.Sound(r"D:\PROJECT_AI\assets\win.mp3")
#             self.lose_sound = pygame.mixer.Sound(r"D:\PROJECT_AI\assets\losing.mp3")
#         except pygame.error as e:
#             print(f"Cannot load sound: {e}")
#             self.win_sound = None
#             self.lose_sound = None

#         # Initialize map and positions
#         self.tilemap = generate_random_map(self.rows, self.cols)
#         self.start_pos = (0, 0)
#         self.goal_pos = (self.rows - 1, self.cols - 1)
#         self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"

#         # Initialize player
#         blocky_sprite = pygame.image.load(r"D:\PROJECT_AI\assets\map\blocky.png")
#         self.player = Player(screen, blocky_sprite, start_pos=self.start_pos, tile_size=tile_size)

#         # Game state
#         self.steps = 0
#         self.font = pygame.font.SysFont("Times New Roman", 28)
#         self.win_font = pygame.font.SysFont("Times New Roman", 60)
#         self.paused = False
#         self.level = 1
#         self.new_level_ready = False

#         # Timer state
#         self.time_limit = 60
#         self.time_left = self.time_limit
#         self.last_time_update = pygame.time.get_ticks()

#         # Path finding state
#         self.path = []
#         self.path_index = 0
#         self.last_move_time = 0
#         self.move_delay = 200
#         self.current_algorithm = "astar"
#         self.show_path = False
#         self.auto_move_enabled = False
#         self.plan = None  # Lưu kế hoạch AND-OR

#         # Tile costs for A*, Backtracking, and Q-Learning
#         self.tile_cost = {
#             "G": 1, "D": 2, "T": float("inf"), "W": 3, "X": 1
#         }

#         # Path and exploration overlays
#         self.path_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
#         self.path_overlay.fill((255, 255, 0, 200))
#         self.exploration_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
#         self.exploration_overlay.fill((0, 255, 0, 100))  # Đậm hơn: từ 64 -> 100
#         self.active_exploration_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
#         self.active_exploration_overlay.fill((0, 255, 0, 200))  # Đậm hơn: từ 128 -> 200
#         self.explored_tiles = set()
#         self.exploration_index = 0
#         self.exploration_list = []
#         self.last_explore_time = 0
#         self.explore_delay = 300
#         self.is_exploring = False
#         self.current_explored_tile = None

#         # Statistics for algorithms
#         self.stats = {
#             "astar": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "bfs": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "beam_search": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "and_or_search": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "backtracking": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "q_learning": {"time": 0, "cost": 0, "nodes": 0, "steps": 0}
#         }
#         self.show_stats = False

#         # Compute initial statistics for the starting map
#         self.compute_all_stats()

#     def draw_tilemap(self):
#         for row in range(len(self.tilemap)):
#             for col in range(len(self.tilemap[row])):
#                 tile = self.tilemap[row][col]
#                 x = col * self.tile_size
#                 y = row * self.tile_size + PANEL_TOP_HEIGHT

#                 if tile == "G":
#                     self.screen.blit(self.grass_img, (x, y))
#                 elif tile == "D":
#                     self.screen.blit(self.dirt_img, (x, y))
#                 elif tile == "T":
#                     self.screen.blit(self.trees_img, (x, y))
#                 elif tile == "W":
#                     self.screen.blit(self.water_img, (x, y))
#                 elif tile == "X":
#                     self.screen.blit(self.treasure_img, (x, y))

#                 if self.current_algorithm in ["backtracking", "and_or_search"]:
#                     if (row, col) == self.current_explored_tile:
#                         self.screen.blit(self.active_exploration_overlay, (x, y))
#                     elif (row, col) in self.explored_tiles:
#                         self.screen.blit(self.exploration_overlay, (x, y))

#                 if self.show_path and self.path and (row, col) in self.path and (row, col) != self.goal_pos:
#                     self.screen.blit(self.path_overlay, (x, y))

#                 pygame.draw.rect(self.screen, (0, 0, 0), (x, y, self.tile_size, self.tile_size), 1)

#     def draw_ui(self):
#         algo_text = self.font.render(f"Algorithm: {self.current_algorithm.replace('_', ' ').upper()}", True, (255, 255, 255))
#         self.screen.blit(algo_text, (self.screen.get_width() - algo_text.get_width() - 10, 10))
#         time_text = self.font.render(f"Time: {int(self.time_left)}", True, (255, 255, 255))
#         self.screen.blit(time_text, (self.screen.get_width() - time_text.get_width() - 10, 45))

#         # Thông báo cho AND-OR Search
#         if self.current_algorithm == "and_or_search":
#             water_count = sum(row.count("W") for row in self.tilemap)
#             if water_count < 5:
#                 warning_text = self.font.render("Few 'W' tiles: AND-OR may act like Backtracking", True, (255, 255, 0))
#                 self.screen.blit(warning_text, (10, 80))
#             else:
#                 info_text = self.font.render("AND-OR Search: Handles uncertain 'W' tiles", True, (255, 255, 255))
#                 self.screen.blit(info_text, (10, 80))

#         if self.new_level_ready:
#             start_text = self.font.render("Press Enter to start!", True, (255, 255, 0))
#             self.screen.blit(start_text, (self.screen.get_width() // 2 - start_text.get_width() // 2, self.screen.get_height() // 2))

#     def draw_plan(self, plan, x, y, indent=0):
#         if not plan:
#             return y
#         state, _, action, next_state, sub_plan = plan[0]
#         action_text = f"From {state}: Move {action} to {next_state}"
#         text = self.font.render("  " * indent + action_text, True, (255, 255, 255))
#         self.screen.blit(text, (x, y))
#         y += 20
#         for condition, outcome, sub_plan_i, prob in sub_plan:
#             condition_text = f"If {condition} → {outcome} (prob: {prob:.1%})"
#             text = self.font.render("  " * (indent + 1) + condition_text, True, (255, 255, 0))
#             self.screen.blit(text, (x, y))
#             y += 20
#             y = self.draw_plan(sub_plan_i, x, y, indent + 2)
#         return y

#     def print_plan_to_terminal(self, plan, tilemap):
#         if plan is None:
#             print("No strategy ensures reaching goal.")
#             return

#         def print_plan_recursive(plan, indent=0):
#             for state, action_type, action, next_state, sub_plan in [plan] if isinstance(plan, tuple) else plan:
#                 if action_type == "action":
#                     tile = tilemap[state[0]][state[1]] if 0 <= state[0] < len(tilemap) and 0 <= state[1] < len(tilemap[0]) else "?"
#                     next_tile = tilemap[next_state[0]][next_state[1]] if 0 <= next_state[0] < len(tilemap) and 0 <= next_state[1] < len(tilemap[0]) else "?"
#                     print("  " * indent + f"From {state} ({tile}): Move {action} to {next_state} ({next_tile})")
#                     if sub_plan:
#                         for condition, outcome, sub_plan_i, prob in sub_plan:
#                             print("  " * (indent + 1) + f"If {condition} ({prob*100:.0f}%) -> {outcome}")
#                             print_plan_recursive(sub_plan_i, indent + 2)
#                 else:
#                     print("  " * indent + f"Unexpected action type: {action_type}")

#         print("\nAND-OR Search Plan:")
#         print_plan_recursive(plan)
#         print(f"Total nodes explored: {self.stats['and_or_search']['nodes']}")
#         print(f"Time taken: {self.stats['and_or_search']['time']:.2f} seconds\n")

#     def draw_stats_table(self):
#         table_width = 700
#         table_height = 400
#         table_x = (self.screen.get_width() - table_width) // 2
#         table_y = (self.screen.get_height() - table_height) // 2
#         table_surface = pygame.Surface((table_width, table_height))
#         table_surface.fill((255, 255, 255))

#         pygame.draw.rect(table_surface, (0, 0, 0), (0, 0, table_width, table_height), 2)

#         algo_col_width = 180
#         other_col_width = 110
#         row_height = 40
#         header_font = pygame.font.SysFont("Times New Roman", 24, bold=True)
#         cell_font = pygame.font.SysFont("Times New Roman", 20)
#         title_font = pygame.font.SysFont("Times New Roman", 30, bold=True)

#         title_text = title_font.render("So sánh thuật toán", True, (0, 0, 255))
#         title_rect = title_text.get_rect(center=(table_width // 2, 30))
#         table_surface.blit(title_text, title_rect)

#         headers = ["Algorithm", "Time (s)", "Cost", "Nodes", "Steps"]
#         algorithms = ["astar", "bfs", "beam_search", "and_or_search", "backtracking", "q_learning"]

#         col_positions = [20]
#         col_positions.append(col_positions[-1] + algo_col_width)
#         col_positions.append(col_positions[-1] + other_col_width)
#         col_positions.append(col_positions[-1] + other_col_width)
#         col_positions.append(col_positions[-1] + other_col_width)

#         header_y = 70
#         for i, header in enumerate(headers):
#             pygame.draw.rect(table_surface, (200, 200, 200), (col_positions[i], header_y, 
#                             algo_col_width if i == 0 else other_col_width, row_height))
#             pygame.draw.rect(table_surface, (0, 0, 0), (col_positions[i], header_y, 
#                             algo_col_width if i == 0 else other_col_width, row_height), 1)
#             text = header_font.render(header, True, (0, 0, 0))
#             text_rect = text.get_rect(center=(col_positions[i] + (algo_col_width if i == 0 else other_col_width) // 2, header_y + row_height // 2))
#             table_surface.blit(text, text_rect)

#         for row, algo in enumerate(algorithms):
#             row_y = header_y + (row + 1) * row_height
#             row_color = (240, 240, 240) if row % 2 else (255, 255, 255)
#             for i in range(len(headers)):
#                 pygame.draw.rect(table_surface, row_color, (col_positions[i], row_y, 
#                                 algo_col_width if i == 0 else other_col_width, row_height))
#                 pygame.draw.rect(table_surface, (0, 0, 0), (col_positions[i], row_y, 
#                                 algo_col_width if i == 0 else other_col_width, row_height), 1)

#             text = cell_font.render(algo.replace('_', ' ').upper(), True, (0, 0, 0))
#             text_rect = text.get_rect(center=(col_positions[0] + algo_col_width // 2, row_y + row_height // 2))
#             table_surface.blit(text, text_rect)

#             time_val = f"{self.stats[algo]['time']:.6f}"
#             text = cell_font.render(time_val, True, (0, 0, 0))
#             text_rect = text.get_rect(center=(col_positions[1] + other_col_width // 2, row_y + row_height // 2))
#             table_surface.blit(text, text_rect)

#             cost_val = f"{self.stats[algo]['cost']}"
#             text = cell_font.render(cost_val, True, (0, 0, 0))
#             text_rect = text.get_rect(center=(col_positions[2] + other_col_width // 2, row_y + row_height // 2))
#             table_surface.blit(text, text_rect)

#             nodes_val = f"{self.stats[algo]['nodes']}"
#             text = cell_font.render(nodes_val, True, (0, 0, 0))
#             text_rect = text.get_rect(center=(col_positions[3] + other_col_width // 2, row_y + row_height // 2))
#             table_surface.blit(text, text_rect)

#             steps_val = f"{self.stats[algo]['steps']}"
#             text = cell_font.render(steps_val, True, (0, 0, 0))
#             text_rect = text.get_rect(center=(col_positions[4] + other_col_width // 2, row_y + row_height // 2))
#             table_surface.blit(text, text_rect)

#         close_button_rect = pygame.Rect(table_width - 120, table_height - 50, 100, 40)
#         mouse_pos = pygame.mouse.get_pos()
#         mouse_pos_in_table = (mouse_pos[0] - table_x, mouse_pos[1] - table_y)
#         close_color = (255, 215, 0) if close_button_rect.collidepoint(mouse_pos_in_table) else (160, 82, 45)
#         pygame.draw.rect(table_surface, close_color, close_button_rect, border_radius=8)
#         close_text = cell_font.render("Close", True, (255, 255, 255))
#         close_text_rect = close_text.get_rect(center=close_button_rect.center)
#         table_surface.blit(close_text, close_text_rect)

#         overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
#         overlay.fill((0, 0, 0, 150))
#         self.screen.blit(overlay, (0, 0))
#         self.screen.blit(table_surface, (table_x, table_y))
#         return close_button_rect.move(table_x, table_y)

#     def compute_path(self):
#         self.path = []
#         self.path_index = 0
#         self.explored_tiles.clear()
#         self.exploration_list = []
#         self.exploration_index = 0
#         self.is_exploring = False
#         self.show_path = True
#         self.plan = None  # Reset kế hoạch

#         start_time = time.perf_counter()
#         nodes_explored = 0
#         path = []
#         path_cost = 0
#         max_time = 5  # Giới hạn 5 giây

#         if self.current_algorithm == "astar":
#             path, path_cost, nodes_explored = astar(self.start_pos, self.goal_pos, self.tilemap, self.tile_cost)
#         elif self.current_algorithm == "bfs":
#             path, nodes_explored = bfs(self.start_pos, self.goal_pos, self.tilemap)
#             path_cost = self.calculate_path_cost(path) if path else 0
#         elif self.current_algorithm == "beam_search":
#             path, nodes_explored = beam_search(self.start_pos, self.goal_pos, self.tilemap)
#             path_cost = self.calculate_path_cost(path) if path else 0
#         elif self.current_algorithm == "and_or_search":
#             self.is_exploring = True
#             self.plan, nodes_explored = and_or_search_with_stats(self.start_pos, self.goal_pos, self.tilemap)
#             if self.plan:
#                 path = extract_path_from_plan(self.plan)
#                 self.exploration_list = path
#                 self.explored_tiles = set(self.exploration_list)
#                 self.print_plan_to_terminal(self.plan, self.tilemap)
#                 path_cost = self.calculate_path_cost(path) if path else 0
#             else:
#                 print("AND-OR Search: No strategy ensures reaching goal due to uncertain 'W' tiles")
#         elif self.current_algorithm == "backtracking":
#             self.is_exploring = True
#             path, exploration_order, nodes_explored = backtracking(self.start_pos, self.goal_pos, self.tilemap, self.tile_cost)
#             self.exploration_list = exploration_order
#             self.explored_tiles = set()
#             path_cost = self.calculate_path_cost(path) if path else 0
#         elif self.current_algorithm == "q_learning":
#             path, nodes_explored = q_learning(self.start_pos, self.goal_pos, self.tilemap)
#             path_cost = self.calculate_path_cost(path) if path else 0

#         end_time = time.perf_counter()
#         time_taken = end_time - start_time
#         if time_taken > max_time:
#             print(f"{self.current_algorithm} timed out")
#             path = []
#             path_cost = 0
#             time_taken = 0
#             nodes_explored = 0

#         steps = len(path) - 1 if path else 0

#         self.path = path
#         if path:
#             print(f"{self.current_algorithm} path: {path}")
#             print(f"Tilemap at path: {[self.tilemap[r][c] for r, c in path]}")
#             self.stats[self.current_algorithm] = {
#                 "time": time_taken,
#                 "cost": path_cost,
#                 "nodes": nodes_explored,
#                 "steps": steps
#             }
#         else:
#             print(f"{self.current_algorithm} found no path")
#             if self.current_algorithm == "and_or_search":
#                 print("AND-OR Search: No strategy ensures reaching goal due to uncertain 'W' tiles")
#             self.stats[self.current_algorithm] = {"time": 0, "cost": 0, "nodes": nodes_explored, "steps": 0}

#     def extract_one_path(self, plan):
#         """Trích xuất một đường đi khả thi từ kế hoạch AND-OR."""
#         if not plan:
#             return []
#         path = [plan[0][0]]  # Bắt đầu từ trạng thái đầu tiên
#         curr_plan = plan
#         while curr_plan:
#             _, _, _, next_state, sub_plan = curr_plan[0]
#             path.append(next_state)
#             # Ưu tiên nhánh "success" nếu có
#             next_sub_plan = None
#             for condition, _, sub_plan_i, _ in sub_plan:
#                 if condition == "success":
#                     next_sub_plan = sub_plan_i
#                     break
#             if not next_sub_plan:
#                 next_sub_plan = sub_plan[0][2] if sub_plan else None
#             curr_plan = next_sub_plan
#         return list(dict.fromkeys(path))  # Loại bỏ các phần tử trùng lặp

#     def compute_all_stats(self):
#         algorithms = ["astar", "bfs", "beam_search", "and_or_search", "backtracking", "q_learning"]
#         original_algorithm = self.current_algorithm
#         original_path = self.path
#         original_explored_tiles = self.explored_tiles.copy()
#         original_exploration_list = self.exploration_list.copy()
#         original_is_exploring = self.is_exploring
#         original_show_path = self.show_path
#         original_plan = self.plan

#         for algo in algorithms:
#             self.current_algorithm = algo
#             self.compute_path()

#         self.current_algorithm = original_algorithm
#         self.path = original_path
#         self.explored_tiles = original_explored_tiles
#         self.exploration_list = original_exploration_list
#         self.is_exploring = original_is_exploring
#         self.show_path = original_show_path
#         self.plan = original_plan

#     def calculate_path_cost(self, path):
#         if not path:
#             return 0
#         cost = 0
#         for r, c in path:
#             tile = self.tilemap[r][c]
#             cost += self.tile_cost.get(tile, 0)
#         return cost

#     def update_exploration(self):
#         if not self.is_exploring or self.current_algorithm not in ["backtracking", "and_or_search"]:
#             return
#         current_time = pygame.time.get_ticks()

#         if self.exploration_index < len(self.exploration_list) and current_time - self.last_explore_time > self.explore_delay:
#             if self.current_explored_tile:
#                 self.explored_tiles.add(self.current_explored_tile)
#             self.current_explored_tile = self.exploration_list[self.exploration_index]
#             self.exploration_index += 1
#             self.last_explore_time = current_time
#         elif self.exploration_index >= len(self.exploration_list):
#             if self.current_explored_tile:
#                 self.explored_tiles.add(self.current_explored_tile)
#             self.current_explored_tile = None
#             self.is_exploring = False

#     def follow_path(self):
#         if self.is_exploring or self.paused or self.new_level_ready or not self.auto_move_enabled:
#             return
#         current_time = pygame.time.get_ticks()
#         if self.path and self.path_index < len(self.path) and current_time - self.last_move_time > self.move_delay:
#             next_pos = self.path[self.path_index]
#             direction = None
#             curr_row, curr_col = self.player.row, self.player.col
#             next_row, next_col = next_pos
#             if next_row == curr_row - 1:
#                 direction = "UP"
#             elif next_row == curr_row + 1:
#                 direction = "DOWN"
#             elif next_col == curr_col - 1:
#                 direction = "LEFT"
#             elif next_col == curr_col + 1:
#                 direction = "RIGHT"
#             if direction:
#                 if self.player.move(direction, self.rows, self.cols, self.tilemap):
#                     self.steps += 1
#                     self.start_pos = (self.player.row, self.player.col)
#                     self.path_index += 1
#                     self.last_move_time = current_time
#                 else:
#                     print(f"Failed to move {direction} to {next_pos}")

#     def check_goal(self):
#         return (self.player.row, self.player.col) == self.goal_pos

#     def set_time_limit(self):
#         if self.level == 1:
#             self.time_limit = 60
#         elif self.level == 2:
#             self.time_limit = 40
#         elif self.level == 3:
#             self.time_limit = 20
#         self.time_left = self.time_limit
#         self.last_time_update = pygame.time.get_ticks()

#     def reset_stats(self):
#         self.stats = {
#             "astar": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "bfs": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "beam_search": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "and_or_search": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "backtracking": {"time": 0, "cost": 0, "nodes": 0, "steps": 0},
#             "q_learning": {"time": 0, "cost": 0, "nodes": 0, "steps": 0}
#         }

#     def reset_for_new_level(self):
#         self.start_pos = (0, 0)
#         self.tilemap = generate_random_map(self.rows, self.cols)
#         self.goal_pos = (self.rows - 1, self.cols - 1)
#         self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"
#         self.player.row, self.player.col = self.start_pos
#         self.steps = 0
#         self.path = []
#         self.path_index = 0
#         self.explored_tiles.clear()
#         self.exploration_list = []
#         self.exploration_index = 0
#         self.is_exploring = False
#         self.auto_move_enabled = False
#         self.show_path = False
#         self.plan = None  # Reset kế hoạch
#         self.set_time_limit()
#         self.new_level_ready = True
#         self.reset_stats()
#         self.compute_all_stats()

#     def reset_game(self):
#         self.level = 1
#         self.steps = 0
#         self.start_pos = (0, 0)
#         self.tilemap = generate_random_map(self.rows, self.cols)
#         self.goal_pos = (self.rows - 1, self.cols - 1)
#         self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"
#         self.player.row, self.player.col = self.start_pos
#         self.path = []
#         self.path_index = 0
#         self.explored_tiles.clear()
#         self.exploration_list = []
#         self.exploration_index = 0
#         self.is_exploring = False
#         self.auto_move_enabled = False
#         self.show_path = False
#         self.plan = None  # Reset kế hoạch
#         self.set_time_limit()
#         self.new_level_ready = False
#         self.paused = False
#         self.reset_stats()
#         self.compute_all_stats()

#     def run(self):
#         clock = pygame.time.Clock()
#         running = True
#         close_button_rect = None

#         while running:
#             try:
#                 if self.gif_frames and not self.paused:
#                     self.frame_timer += 1
#                     if self.frame_timer >= 10:
#                         self.current_frame = (self.current_frame + 1) % self.frame_count
#                         self.frame_timer = 0
#                     self.screen.blit(self.gif_frames[self.current_frame], (0, 0))
#                 else:
#                     self.screen.fill((0, 105, 148), (0, 0, self.screen.get_width(), PANEL_TOP_HEIGHT))
#             except pygame.error as e:
#                 print(f"Error rendering top panel background: {e}")

#             self.screen.fill((30, 30, 30), (0, PANEL_TOP_HEIGHT, self.screen.get_width(), self.screen.get_height() - PANEL_TOP_HEIGHT))
#             self.draw_tilemap()
#             self.player.render()
#             self.draw_ui()

#             if not self.paused and not self.new_level_ready:
#                 current_time = pygame.time.get_ticks()
#                 if current_time - self.last_time_update >= 1000:
#                     self.time_left -= 1
#                     self.last_time_update = current_time

#             try:
#                 button_font = pygame.font.SysFont("timesnewroman", 18, bold=True)
#                 button_width, button_height = 90, 35
#                 icon_button_size = 40
#                 button_spacing = 10

#                 top_row_y = 10
#                 replay_button_rect = pygame.Rect((self.screen.get_width() - 2 * icon_button_size - button_spacing) // 2, top_row_y, icon_button_size, icon_button_size)
#                 pause_button_rect = pygame.Rect((self.screen.get_width() - 2 * icon_button_size - button_spacing) // 2 + icon_button_size + button_spacing, top_row_y, icon_button_size, icon_button_size)

#                 bottom_row_y = 55
#                 random_map_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2, bottom_row_y, button_width, button_height)
#                 help_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + button_width + button_spacing, bottom_row_y, button_width, button_height)
#                 stats_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + 2 * (button_width + button_spacing), bottom_row_y, button_width, button_height)
#                 exit_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + 3 * (button_width + button_spacing), bottom_row_y, button_width, button_height)

#                 mouse_pos = pygame.mouse.get_pos()
#                 replay_color = (255, 215, 0) if replay_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
#                 pause_color = (255, 215, 0) if pause_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
#                 random_map_color = (255, 215, 0) if random_map_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
#                 help_color = (255, 215, 0) if help_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
#                 stats_color = (255, 215, 0) if stats_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
#                 exit_color = (255, 215, 0) if exit_button_rect.collidepoint(mouse_pos) else (160, 82, 45)

#                 pygame.draw.rect(self.screen, replay_color, replay_button_rect, border_radius=8)
#                 pygame.draw.rect(self.screen, pause_color, pause_button_rect, border_radius=8)
#                 self.screen.blit(self.replay_icon, (replay_button_rect.x + (icon_button_size - self.replay_icon.get_width()) // 2, replay_button_rect.y + (icon_button_size - self.replay_icon.get_height()) // 2))
#                 self.screen.blit(self.pause_icon, (pause_button_rect.x + (icon_button_size - self.pause_icon.get_width()) // 2, pause_button_rect.y + (icon_button_size - self.pause_icon.get_height()) // 2))

#                 pygame.draw.rect(self.screen, random_map_color, random_map_button_rect, border_radius=8)
#                 pygame.draw.rect(self.screen, help_color, help_button_rect, border_radius=8)
#                 pygame.draw.rect(self.screen, stats_color, stats_button_rect, border_radius=8)
#                 pygame.draw.rect(self.screen, exit_color, exit_button_rect, border_radius=8)

#                 random_map_text = button_font.render("Random", True, (255, 255, 255))
#                 help_text = button_font.render("Help", True, (255, 255, 255))
#                 stats_text = button_font.render("Statistics", True, (255, 255, 255))
#                 exit_text = button_font.render("Exit", True, (255, 255, 255))

#                 self.screen.blit(random_map_text, random_map_text.get_rect(center=random_map_button_rect.center))
#                 self.screen.blit(help_text, help_text.get_rect(center=help_button_rect.center))
#                 self.screen.blit(stats_text, stats_text.get_rect(center=stats_button_rect.center))
#                 self.screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))

#                 steps_text = self.font.render(f"Steps: {self.steps}", True, (0, 255, 128), (0, 0, 0))
#                 level_text = self.font.render(f"Level: {self.level}", True, (255, 165, 0), (0, 0, 0))
#                 self.screen.blit(steps_text, (10, 10))
#                 self.screen.blit(level_text, (10, 45))

#             except pygame.error as e:
#                 print(f"Error rendering buttons: {e}")

#             if self.show_stats:
#                 close_button_rect = self.draw_stats_table()

#             self.update_exploration()
#             self.follow_path()

#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     return "QUIT"
#                 elif event.type == pygame.MOUSEBUTTONDOWN:
#                     if replay_button_rect.collidepoint(event.pos):
#                         self.reset_game()
#                     elif random_map_button_rect.collidepoint(event.pos):
#                         self.tilemap = generate_random_map(self.rows, self.cols)
#                         self.goal_pos = (self.rows - 1, self.cols - 1)
#                         self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"
#                         self.player.row, self.player.col = self.start_pos
#                         self.steps = 0
#                         self.path = []
#                         self.auto_move_enabled = False
#                         self.show_path = False
#                         self.set_time_limit()
#                         self.new_level_ready = False
#                         self.reset_stats()
#                         self.compute_all_stats()
#                     elif help_button_rect.collidepoint(event.pos):
#                         self.compute_path()
#                     elif pause_button_rect.collidepoint(event.pos):
#                         self.paused = not self.paused
#                     elif stats_button_rect.collidepoint(event.pos):
#                         self.show_stats = not self.show_stats
#                     elif exit_button_rect.collidepoint(event.pos):
#                         pygame.mixer.music.stop()
#                         show_start_screen(self.screen)
#                         return "MAIN_MENU"
#                     elif self.show_stats and close_button_rect and close_button_rect.collidepoint(event.pos):
#                         self.show_stats = False
#                 elif event.type == pygame.KEYDOWN and not self.paused:
#                     if event.key == pygame.K_UP or event.key == pygame.K_w:
#                         if self.player.move("UP", self.rows, self.cols, self.tilemap):
#                             self.steps += 1
#                             self.start_pos = (self.player.row, self.player.col)
#                             self.auto_move_enabled = False
#                             self.new_level_ready = False
#                     elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
#                         if self.player.move("DOWN", self.rows, self.cols, self.tilemap):
#                             self.steps += 1
#                             self.start_pos = (self.player.row, self.player.col)
#                             self.auto_move_enabled = False
#                             self.new_level_ready = False
#                     elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
#                         if self.player.move("LEFT", self.rows, self.cols, self.tilemap):
#                             self.steps += 1
#                             self.start_pos = (self.player.row, self.player.col)
#                             self.auto_move_enabled = False
#                             self.new_level_ready = False
#                     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
#                         if self.player.move("RIGHT", self.rows, self.cols, self.tilemap):
#                             self.steps += 1
#                             self.start_pos = (self.player.row, self.player.col)
#                             self.auto_move_enabled = False
#                             self.new_level_ready = False
#                     elif event.key == pygame.K_SPACE:
#                         self.compute_path()
#                         self.auto_move_enabled = True
#                     elif event.key == pygame.K_1:
#                         self.current_algorithm = "astar"
#                         self.path = []
#                         self.show_path = False
#                         self.auto_move_enabled = False
#                         print("Selected A*")
#                     elif event.key == pygame.K_2:
#                         self.current_algorithm = "bfs"
#                         self.path = []
#                         self.show_path = False
#                         self.auto_move_enabled = False
#                         print("Selected BFS")
#                     elif event.key == pygame.K_3:
#                         self.current_algorithm = "beam_search"
#                         self.path = []
#                         self.show_path = False
#                         self.auto_move_enabled = False
#                         print("Selected Beam Search")
#                     elif event.key == pygame.K_4:
#                         self.current_algorithm = "and_or_search"
#                         self.path = []
#                         self.show_path = False
#                         self.auto_move_enabled = False
#                         print("Selected AND-OR Search: Handles uncertain 'W' tiles")
#                     elif event.key == pygame.K_5:
#                         self.current_algorithm = "backtracking"
#                         self.path = []
#                         self.show_path = False
#                         self.auto_move_enabled = False
#                         print("Selected Backtracking")
#                     elif event.key == pygame.K_6:
#                         self.current_algorithm = "q_learning"
#                         self.path = []
#                         self.show_path = False
#                         self.auto_move_enabled = False
#                         print("Selected Q-Learning")
#                     elif event.key == pygame.K_RETURN and self.new_level_ready:
#                         self.new_level_ready = False
#                         self.last_time_update = pygame.time.get_ticks()

#             if self.time_left <= 0 and not self.paused and not self.new_level_ready:
#                 game_over_text = self.win_font.render("TIME OUT!", True, (255, 0, 0))
#                 shadow_text = self.win_font.render("TIME OUT!", True, (0, 0, 0))
#                 self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 + 3, self.screen.get_height() // 2 + 3))
#                 self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 - 3, self.screen.get_height() // 2 - 3))
#                 self.screen.blit(game_over_text, (self.screen.get_width() // 2 - game_over_text.get_width() // 2, self.screen.get_height() // 2))
#                 if self.lose_sound:
#                     self.lose_sound.play()
#                 pygame.display.flip()
#                 pygame.time.wait(3000)
#                 self.reset_game()

#             if self.check_goal() and not self.paused and not self.new_level_ready:
#                 if self.win_sound:
#                     self.win_sound.play()

#                 if self.level >= 3:
#                     final_win_text = self.win_font.render("CONGRATULATIONS!", True, (255, 215, 0))
#                     shadow_text = self.win_font.render("CONGRATULATIONS!", True, (245, 245, 220))
#                     self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 + 3, self.screen.get_height() // 2 + 3))
#                     self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 - 3, self.screen.get_height() // 2 - 3))
#                     self.screen.blit(final_win_text, (self.screen.get_width() // 2 - final_win_text.get_width() // 2, self.screen.get_height() // 2))
#                     pygame.display.flip()
#                     pygame.time.wait(3000)
#                     pygame.mixer.music.stop()  # Dừng nhạc game nếu có
#                     self.reset_game()  # Reset game về level 1 và trạng thái ban đầu
#                     show_start_screen(self.screen)  # Hiển thị giao diện chính
#                     return "MAIN_MENU"  # Trả về trạng thái để main.py xử lý
#                 else:
#                     you_win_text = self.win_font.render("YOU WIN!", True, (255, 255, 0))
#                     shadow_text = self.win_font.render("YOU WIN!", True, (0, 0, 0))
#                     self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 + 3, self.screen.get_height() // 2 + 3))
#                     self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 - 3, self.screen.get_height() // 2 - 3))
#                     self.screen.blit(you_win_text, (self.screen.get_width() // 2 - you_win_text.get_width() // 2, self.screen.get_height() // 2))
#                     pygame.display.flip()
#                     pygame.time.wait(3000)
#                     self.level += 1
#                     self.reset_for_new_level()

#             pygame.display.flip()
#             clock.tick(60)

#         return "Level Complete"