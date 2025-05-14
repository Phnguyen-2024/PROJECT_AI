import pygame
import math
import random
try:
    from PIL import Image
    pillow_available = True
except ImportError:
    pillow_available = False

# Khởi tạo pygame
pygame.init()
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Error initializing mixer: {e}")

# Kích thước màn hình và panel
WIDTH, HEIGHT = 800, 600
PANEL_TOP_HEIGHT = 100
PANEL_BOTTOM_HEIGHT = HEIGHT - PANEL_TOP_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRUY TÌM KHO BÁU")

# Load GIF frames cho nền động
def load_gif_frames(gif_path):
    frames = []
    if not pillow_available:
        print("Pillow not installed, cannot load GIF")
        return frames
    try:
        image = Image.open(gif_path)
        for frame in range(image.n_frames):
            image.seek(frame)
            frame_surface = pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert()
            frame_surface = pygame.transform.scale(frame_surface, (WIDTH, PANEL_TOP_HEIGHT))
            frames.append(frame_surface)
    except Exception as e:
        print(f"Không thể load ảnh nền động: {e}")
    return frames

# Hàm tải hình ảnh
def load_image(filepath, tile_size):
    image = pygame.image.load(filepath)
    return pygame.transform.scale(image, (tile_size, tile_size))

# Hàm tải icon với kích thước tùy chỉnh
def load_icon(filepath, size):
    icon = pygame.image.load(filepath)
    return pygame.transform.scale(icon, (size, size))

# Hàm lấy các ô lân cận
def get_neighbors(pos, rows, cols, tilemap):
    row, col = pos
    neighbors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < rows and 0 <= new_col < cols and tilemap[new_row][new_col] != "T":
            neighbors.append((new_row, new_col))
    return neighbors

# Các thuật toán tìm đường
def astar(start, goal, tilemap, tile_cost):
    from heapq import heappush, heappop
    rows, cols = len(tilemap), len(tilemap[0])
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: abs(goal[0] - start[0]) + abs(goal[1] - start[1])}

    while open_set:
        current = heappop(open_set)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for neighbor in get_neighbors(current, rows, cols, tilemap):
            tentative_g_score = g_score[current] + tile_cost[tilemap[neighbor[0]][neighbor[1]]]
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + abs(goal[0] - neighbor[0]) + abs(goal[1] - neighbor[1])
                heappush(open_set, (f_score[neighbor], neighbor))
    return []

def bfs(start, goal, tilemap):
    from collections import deque
    rows, cols = len(tilemap), len(tilemap[0])
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (row, col), path = queue.popleft()
        if (row, col) == goal:
            return path

        for neighbor in get_neighbors((row, col), rows, cols, tilemap):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []

def beam_search(start, goal, tilemap, beam_width=3):
    from heapq import heappush, heappop
    rows, cols = len(tilemap), len(tilemap[0])
    beam = [(0, [start])]
    visited = {start}

    while beam:
        new_beam = []
        for _ in range(min(beam_width, len(beam))):
            if not beam:
                break
            _, path = heappop(beam)
            current = path[-1]
            if current == goal:
                return path

            for neighbor in get_neighbors(current, rows, cols, tilemap):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    score = -(abs(goal[0] - neighbor[0]) + abs(goal[1] - neighbor[1]))
                    heappush(new_beam, (score, new_path))
        beam = new_beam
    return []

def and_or_search(start, goal, tilemap):
    def solve(pos, path, visited):
        if pos == goal:
            return path
        visited.add(pos)
        neighbors = get_neighbors(pos, len(tilemap), len(tilemap[0]), tilemap)
        or_results = []
        for neighbor in neighbors:
            if neighbor not in visited:
                result = solve(neighbor, path + [neighbor], visited.copy())
                if result:
                    or_results.append(result)
        return min(or_results, key=len) if or_results else []

    path = solve(start, [start], set())
    return path

def q_learning(start, goal, tilemap, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
    import numpy as np
    rows, cols = len(tilemap), len(tilemap[0])
    q_table = np.zeros((rows, cols, 4))
    actions = ["UP", "DOWN", "LEFT", "RIGHT"]
    tile_cost = {"G": 1, "D": 2, "T": float("inf"), "W": 5, "X": 1}

    def get_action(state, epsilon):
        if random.random() < epsilon:
            return random.choice(range(4))
        return np.argmax(q_table[state[0], state[1]])

    def move_action(state, action, rows, cols, tilemap):
        row, col = state
        new_row, new_col = row, col
        if action == 0 and row > 0 and tilemap[row - 1][col] != "T":
            new_row -= 1
        elif action == 1 and row < rows - 1 and tilemap[row + 1][col] != "T":
            new_row += 1
        elif action == 2 and col > 0 and tilemap[row][col - 1] != "T":
            new_col -= 1
        elif action == 3 and col < cols - 1 and tilemap[row][col + 1] != "T":
            new_col += 1
        return (new_row, new_col)

    for _ in range(episodes):
        state = start
        while state != goal:
            action = get_action(state, epsilon)
            next_state = move_action(state, action, rows, cols, tilemap)
            reward = -tile_cost[tilemap[next_state[0]][next_state[1]]]
            if next_state == goal:
                reward = 100
            q_table[state[0], state[1], action] = (1 - alpha) * q_table[state[0], state[1], action] + \
                alpha * (reward + gamma * np.max(q_table[next_state[0], next_state[1]]))
            state = next_state

    path = [start]
    state = start
    while state != goal:
        action = np.argmax(q_table[state[0], state[1]])
        next_state = move_action(state, action, rows, cols, tilemap)
        if next_state == state:
            break
        path.append(next_state)
        state = next_state
    return path

# Class Player
class Player:
    def __init__(self, screen, sprite, start_pos=(0, 0), tile_size=64):
        self.screen = screen
        self.sprite = pygame.transform.scale(sprite, (tile_size, tile_size))
        self.row, self.col = start_pos
        self.tile_size = tile_size

    def move(self, direction, rows, cols, tilemap):
        new_row, new_col = self.row, self.col
        if direction == "UP" and self.row > 0 and tilemap[self.row - 1][self.col] != "T":
            new_row -= 1
        elif direction == "DOWN" and self.row < rows - 1 and tilemap[self.row + 1][self.col] != "T":
            new_row += 1
        elif direction == "LEFT" and self.col > 0 and tilemap[self.row][self.col - 1] != "T":
            new_col -= 1
        elif direction == "RIGHT" and self.col < cols - 1 and tilemap[self.row][self.col + 1] != "T":
            new_col += 1
        
        if (new_row, new_col) != (self.row, self.col):
            self.row, self.col = new_row, new_col
            return True
        return False

    def render(self):
        x = self.col * self.tile_size
        y = self.row * self.tile_size + PANEL_TOP_HEIGHT
        self.screen.blit(self.sprite, (x, y))

# Hàm tạo bản đồ ngẫu nhiên
def generate_random_map(rows, cols):
    TILE_TYPES = ["G", "D", "T", "W"]
    tilemap = [[random.choice(TILE_TYPES) for _ in range(cols)] for _ in range(rows)]
    # Đảm bảo vị trí xuất phát (0, 0) và kho báu (rows-1, cols-1) không phải cây ("T")
    tilemap[0][0] = "G"
    tilemap[rows - 1][cols - 1] = "X"
    return tilemap

# Class Game
class Game:
    def __init__(self, screen, tile_size, rows, cols):
        self.screen = screen
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols

        # Load GIF frames
        self.gif_path = r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\src\hinhnen.gif"
        self.gif_frames = load_gif_frames(self.gif_path)
        self.frame_count = len(self.gif_frames)
        self.current_frame = 0
        self.frame_timer = 0
        # D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\src\

        # Load images
        self.grass_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\grass.png", tile_size)
        self.dirt_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\dirt.png", tile_size)
        self.trees_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\tree.png", tile_size)
        self.water_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\water_16px.png", tile_size)
        self.treasure_img = load_image(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\treasure.png", tile_size)
        # D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\map\

        # Load icons cho nút
        self.replay_icon = load_icon(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\replay_icon.png", 24)
        self.pause_icon = load_icon(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\pause_icon.png", 24)
        # D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets

        # Load âm thanh chiến thắng
        try:
            self.win_sound = pygame.mixer.Sound(r"D:\Nam2 - Ki2\Artificial Intelligence\PROJECT_AI\assets\win.mp3")
        except pygame.error as e:
            print(f"Không thể load âm thanh chiến thắng: {e}")
            self.win_sound = None

        # Khởi tạo bản đồ và vị trí
        self.start_pos = (0, 0)
        self.goal_pos = (rows - 1, cols - 1)
        self.tilemap = generate_random_map(rows, cols)

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
        self.time_limit = 60  # Level 1: 60 seconds
        self.time_left = self.time_limit
        self.last_time_update = pygame.time.get_ticks()

        # Path finding state
        self.path = []
        self.path_index = 0
        self.last_move_time = 0
        self.move_delay = 200
        self.current_algorithm = "astar"
        self.show_path = False

        # Tile costs for A*, Backtracking, and Q-Learning
        self.tile_cost = {
            "G": 1, "D": 2, "T": float("inf"), "W": 3, "X": 1
        }

        # Path overlay for visualization
        self.path_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.path_overlay.fill((255, 255, 0, 200))  # Vàng sáng, ít trong suốt
        # Exploration overlay for Backtracking
        self.exploration_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.exploration_overlay.fill((0, 255, 0, 64))
        self.explored_tiles = set()
        self.exploration_index = 0
        self.exploration_list = []
        self.last_explore_time = 0
        self.explore_delay = 50
        self.is_exploring = False
        self.auto_move_enabled = False

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

                # Draw exploration overlay for Backtracking
                if self.current_algorithm == "backtracking" and (row, col) in self.explored_tiles:
                    self.screen.blit(self.exploration_overlay, (x, y))

                # Draw path overlay chỉ khi show_path và có path
                if self.show_path and self.path and (row, col) in self.path and (row, col) != self.goal_pos:
                    self.screen.blit(self.path_overlay, (x, y))

                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, self.tile_size, self.tile_size), 1)

    def draw_ui(self):
        # Hiển thị thuật toán
        algo_text = self.font.render(f"Algorithm: {self.current_algorithm.upper()}", True, (255, 255, 255))
        self.screen.blit(algo_text, (WIDTH - algo_text.get_width() - 10, 10))
        # Hiển thị thời gian
        time_text = self.font.render(f"Thời gian: {int(self.time_left)}", True, (255, 255, 255))
        self.screen.blit(time_text, (WIDTH - time_text.get_width() - 10, 45))
        # Hiển thị thông báo bắt đầu level
        if self.new_level_ready:
            start_text = self.font.render("Nhấn Enter để bắt đầu!", True, (255, 255, 0))
            self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))

    def compute_path(self):
        self.path = []
        self.path_index = 0
        self.explored_tiles.clear()
        self.exploration_list = []
        self.exploration_index = 0
        self.is_exploring = False
        self.show_path = True

        if self.current_algorithm == "astar":
            self.path = astar(self.start_pos, self.goal_pos, self.tilemap, self.tile_cost)
        elif self.current_algorithm == "bfs":
            self.path = astar(self.start_pos, self.goal_pos, self.tilemap, self.tile_cost)
        elif self.current_algorithm == "beam_search":
            self.path = beam_search(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "AndOr":
            self.path = and_or_search(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "backtracking":
            self.is_exploring = True
            visited = set()
            path = []

            def backtrack(curr):
                self.exploration_list.append(curr)
                if curr == self.goal_pos:
                    path.append(curr)
                    return True
                if curr in visited:
                    return False
                visited.add(curr)
                path.append(curr)
                for neighbor in get_neighbors(curr, self.rows, self.cols, self.tilemap):
                    if backtrack(neighbor):
                        return True
                path.pop()
                visited.remove(curr)
                return False

            if backtrack(self.start_pos):
                self.path = path
            self.explored_tiles = set(self.exploration_list)
        elif self.current_algorithm == "q_learning":
            self.path = q_learning(self.start_pos, self.goal_pos, self.tilemap)

        if self.path:
            print(f"{self.current_algorithm} path: {self.path}")
            print(f"Tilemap at path: {[self.tilemap[r][c] for r, c in self.path]}")
        else:
            print(f"{self.current_algorithm} found no path")

    def update_exploration(self):
        if not self.is_exploring or self.current_algorithm != "backtracking":
            return
        current_time = pygame.time.get_ticks()
        if self.exploration_index < len(self.exploration_list) and current_time - self.last_explore_time > self.explore_delay:
            tile = self.exploration_list[self.exploration_index]
            self.explored_tiles.add(tile)
            self.exploration_index += 1
            self.last_explore_time = current_time
        elif self.exploration_index >= len(self.exploration_list):
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
        else:  # Level 3 or higher
            self.time_limit = 20
        self.time_left = self.time_limit
        self.last_time_update = pygame.time.get_ticks()

    def reset_for_new_level(self):
        self.start_pos = (0, 0)
        self.tilemap = generate_random_map(self.rows, self.cols)
        self.goal_pos = (self.rows - 1, self.cols - 1)
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
        self.set_time_limit()
        self.new_level_ready = True

    def reset_game(self):
        self.level = 1
        self.steps = 0
        self.start_pos = (0, 0)
        self.tilemap = generate_random_map(self.rows, self.cols)
        self.goal_pos = (self.rows - 1, self.cols - 1)
        self.player.row, self.player.col = self.start_pos
        self.path = []
        self.path_index = 0
        self.explored_tiles.clear()
        self.exploration_list = []
        self.exploration_index = 0
        self.is_exploring = False
        self.auto_move_enabled = False
        self.show_path = False
        self.set_time_limit()
        self.new_level_ready = False
        self.paused = False

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            # Vẽ panel trên với nền động
            try:
                if self.gif_frames and not self.paused:
                    self.frame_timer += 1
                    if self.frame_timer >= 10:
                        self.current_frame = (self.current_frame + 1) % self.frame_count
                        self.frame_timer = 0
                    self.screen.blit(self.gif_frames[self.current_frame], (0, 0))
                else:
                    self.screen.fill((0, 105, 148), (0, 0, WIDTH, PANEL_TOP_HEIGHT))
            except pygame.error as e:
                print(f"Error rendering top panel background: {e}")

            # Vẽ panel dưới với bản đồ
            self.screen.fill((30, 30, 30), (0, PANEL_TOP_HEIGHT, WIDTH, PANEL_BOTTOM_HEIGHT))
            self.draw_tilemap()
            self.player.render()
            self.draw_ui()

            # Cập nhật thời gian
            if not self.paused and not self.new_level_ready:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_time_update >= 1000:  # 1 giây
                    self.time_left -= 1
                    self.last_time_update = current_time

            # Vẽ các nút và thông tin trên panel trên
            try:
                button_font = pygame.font.SysFont("timesnewroman", 18, bold=True)
                button_width, button_height = 90, 35
                icon_button_size = 40
                button_spacing = 10

                top_row_y = 10
                replay_button_rect = pygame.Rect((WIDTH - 2 * icon_button_size - button_spacing) // 2, top_row_y, icon_button_size, icon_button_size)
                pause_button_rect = pygame.Rect((WIDTH - 2 * icon_button_size - button_spacing) // 2 + icon_button_size + button_spacing, top_row_y, icon_button_size, icon_button_size)

                bottom_row_y = 55
                random_map_button_rect = pygame.Rect((WIDTH - 4 * button_width - 3 * button_spacing) // 2, bottom_row_y, button_width, button_height)
                help_button_rect = pygame.Rect((WIDTH - 4 * button_width - 3 * button_spacing) // 2 + button_width + button_spacing, bottom_row_y, button_width, button_height)
                level_button_rect = pygame.Rect((WIDTH - 4 * button_width - 3 * button_spacing) // 2 + 2 * (button_width + button_spacing), bottom_row_y, button_width, button_height)
                exit_button_rect = pygame.Rect((WIDTH - 4 * button_width - 3 * button_spacing) // 2 + 3 * (button_width + button_spacing), bottom_row_y, button_width, button_height)

                mouse_pos = pygame.mouse.get_pos()
                replay_color = (255, 215, 0) if replay_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                pause_color = (255, 215, 0) if pause_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                random_map_color = (255, 215, 0) if random_map_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                help_color = (255, 215, 0) if help_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                level_color = (255, 215, 0) if level_button_rect.collidepoint(mouse_pos) else (160, 82, 45)
                exit_color = (255, 215, 0) if exit_button_rect.collidepoint(mouse_pos) else (160, 82, 45)

                pygame.draw.rect(self.screen, replay_color, replay_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, pause_color, pause_button_rect, border_radius=8)
                self.screen.blit(self.replay_icon, (replay_button_rect.x + (icon_button_size - self.replay_icon.get_width()) // 2, replay_button_rect.y + (icon_button_size - self.replay_icon.get_height()) // 2))
                self.screen.blit(self.pause_icon, (pause_button_rect.x + (icon_button_size - self.pause_icon.get_width()) // 2, pause_button_rect.y + (icon_button_size - self.pause_icon.get_height()) // 2))

                pygame.draw.rect(self.screen, random_map_color, random_map_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, help_color, help_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, level_color, level_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, exit_color, exit_button_rect, border_radius=8)

                random_map_text = button_font.render("Random", True, (255, 255, 255))
                help_text = button_font.render("Trợ giúp", True, (255, 255, 255))
                level_text = button_font.render("Cấp độ", True, (255, 255, 255))
                exit_text = button_font.render("Thoát", True, (255, 255, 255))

                self.screen.blit(random_map_text, random_map_text.get_rect(center=random_map_button_rect.center))
                self.screen.blit(help_text, help_text.get_rect(center=help_button_rect.center))
                self.screen.blit(level_text, level_text.get_rect(center=level_button_rect.center))
                self.screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))

                steps_text = self.font.render(f"Bước: {self.steps}", True, (0, 255, 128), (0, 0, 0))
                level_text = self.font.render(f"Cấp độ: {self.level}", True, (255, 165, 0), (0, 0, 0))
                self.screen.blit(steps_text, (10, 10))
                self.screen.blit(level_text, (10, 45))

            except pygame.error as e:
                print(f"Error rendering buttons: {e}. Vui lòng kiểm tra font chữ hỗ trợ tiếng Việt.")

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
                        self.player.row, self.player.col = self.start_pos
                        self.steps = 0
                        self.path = []
                        self.auto_move_enabled = False
                        self.show_path = False
                        self.set_time_limit()
                        self.new_level_ready = False
                    elif help_button_rect.collidepoint(event.pos):
                        self.compute_path()
                    elif pause_button_rect.collidepoint(event.pos):
                        self.paused = not self.paused
                    elif level_button_rect.collidepoint(event.pos):
                        print("Level clicked - Implement level logic here")
                        self.level += 1
                        self.reset_for_new_level()
                    elif exit_button_rect.collidepoint(event.pos):
                        return "QUIT"
                elif event.type == pygame.KEYDOWN and not self.paused:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.player.move("UP", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.player.move("DOWN", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.player.move("LEFT", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.player.move("RIGHT", self.rows, self.cols, self.tilemap):
                            self.steps += 1
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
                    elif event.key == pygame.K_2:
                        self.current_algorithm = "bfs"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                    elif event.key == pygame.K_3:
                        self.current_algorithm = "beam_search"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                    elif event.key == pygame.K_4:
                        self.current_algorithm = "AndOr"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                    elif event.key == pygame.K_5:
                        self.current_algorithm = "backtracking"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                    elif event.key == pygame.K_6:
                        self.current_algorithm = "q_learning"
                        self.path = []
                        self.show_path = False
                        self.auto_move_enabled = False
                    elif event.key == pygame.K_RETURN and self.new_level_ready:
                        self.new_level_ready = False
                        self.last_time_update = pygame.time.get_ticks()

            # Kiểm tra hết thời gian
            if self.time_left <= 0 and not self.paused and not self.new_level_ready:
                game_over_text = self.win_font.render("HẾT GIỜ!", True, (255, 0, 0))
                shadow_text = self.win_font.render("HẾT GIỜ!", True, (0, 0, 0))
                self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 + 3, self.screen.get_height() // 2 + 3))
                self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 - 3, self.screen.get_height() // 2 - 3))
                self.screen.blit(game_over_text, (self.screen.get_width() // 2 - game_over_text.get_width() // 2, self.screen.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
                self.reset_game()

            # Kiểm tra thắng
            if self.check_goal() and not self.paused and not self.new_level_ready:
                if self.win_sound:
                    self.win_sound.play()

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

if __name__ == "__main__":
    rows = PANEL_BOTTOM_HEIGHT // 64
    cols = WIDTH // 64
    game = Game(screen, 64, rows, cols)
    while True:
        result = game.run()
        if result == "QUIT":
            pygame.quit()
            break
        elif result == "Level Complete":
            pygame.quit()
            break