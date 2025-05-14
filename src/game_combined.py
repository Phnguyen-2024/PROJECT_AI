import pygame
import math
import random
from thuattoan import *
from player import Player
from map_generator import generate_random_map
from utils import load_image, load_icon
from ui import load_gif_frames
import time
PANEL_TOP_HEIGHT = 100

# Class Game
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
        # self.start_pos = (0, 0)
        # self.goal_pos = (rows - 1, cols - 1)
        # self.tilemap = generate_random_map(rows, cols)

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
        self.auto_move_enabled = False

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
        self.screen.blit(algo_text, (self.screen.get_width() - algo_text.get_width() - 10, 10))
        # Hiển thị thời gian
        time_text = self.font.render(f"Thời gian: {int(self.time_left)}", True, (255, 255, 255))
        self.screen.blit(time_text, (self.screen.get_width() - time_text.get_width() - 10, 45))

        # Hiển thị thông báo bắt đầu level
        if self.new_level_ready:
            start_text = self.font.render("Nhấn Enter để bắt đầu!", True, (255, 255, 0))
            self.screen.blit(start_text, (self.screen.get_width() // 2 - start_text.get_width() // 2, self.screen.get_height() // 2))

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
            self.path = bfs(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "beam_search":
            self.path = beam_search(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "AndOr":
            self.path = and_or_search(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "backtracking":
            self.is_exploring = True
            self.path = backtracking(self.start_pos, self.goal_pos, self.tilemap, self.tile_cost)
            self.exploration_list = self.path  # Use path for exploration visualization
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
                    self.screen.fill((0, 105, 148), (0, 0, self.screen.get_width(), PANEL_TOP_HEIGHT))
            except pygame.error as e:
                print(f"Error rendering top panel background: {e}")

            # Vẽ panel dưới với bản đồ
            self.screen.fill((30, 30, 30), (0, PANEL_TOP_HEIGHT, self.screen.get_width(), self.screen.get_height() - PANEL_TOP_HEIGHT))
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
                replay_button_rect = pygame.Rect((self.screen.get_width() - 2 * icon_button_size - button_spacing) // 2, top_row_y, icon_button_size, icon_button_size)
                pause_button_rect = pygame.Rect((self.screen.get_width() - 2 * icon_button_size - button_spacing) // 2 + icon_button_size + button_spacing, top_row_y, icon_button_size, icon_button_size)

                bottom_row_y = 55
                random_map_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2, bottom_row_y, button_width, button_height)
                help_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + button_width + button_spacing, bottom_row_y, button_width, button_height)
                level_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + 2 * (button_width + button_spacing), bottom_row_y, button_width, button_height)
                exit_button_rect = pygame.Rect((self.screen.get_width() - 4 * button_width - 3 * button_spacing) // 2 + 3 * (button_width + button_spacing), bottom_row_y, button_width, button_height)

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
                            self.start_pos = (self.player.row, self.player.col)
                            # self.compute_path()
                            # self.path = []
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.player.move("DOWN", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            # self.compute_path()
                            # self.path = []
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.player.move("LEFT", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            # self.compute_path()
                            # self.path = []
                            self.auto_move_enabled = False
                            self.new_level_ready = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.player.move("RIGHT", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            # self.path = []
                            # self.compute_path()
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

                if self.level >= 3:
                    final_win_text = self.win_font.render("CONGRATULATIONS!", True, (255, 215, 0))
                    shadow_text = self.win_font.render("CONGRATULATIONS!", True, (0, 0, 0))
                    self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 + 3, self.screen.get_height() // 2 + 3))
                    self.screen.blit(shadow_text, (self.screen.get_width() // 2 - shadow_text.get_width() // 2 - 3, self.screen.get_height() // 2 - 3))
                    self.screen.blit(final_win_text, (self.screen.get_width() // 2 - final_win_text.get_width() // 2, self.screen.get_height() // 2))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    self.reset_game()
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