# import pygame
# from player import Player
# from utils import load_image
# from map_generator import generate_random_map

# class Game:
#     def __init__(self, screen, tile_size, rows, cols):
#         self.screen = screen
#         self.tile_size = tile_size
#         self.rows = rows
#         self.cols = cols

#         # Load images
#         self.grass_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\grass.png", tile_size)
#         self.dirt_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\dirt.png", tile_size)
#         self.trees_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\tree.png", tile_size)
#         self.water_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\water_16px.png", tile_size)
#         self.treasure_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\treasure.png", tile_size)

#         # Generate map and set start/goal positions
#         self.tilemap = generate_random_map(rows, cols)
#         self.start_pos = (0, 0)  # Start at the top-left corner
#         self.goal_pos = (rows - 1, cols - 1)  # Goal at the bottom-right corner
#         self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"  # Mark goal with "X"

#         # Initialize player
#         blocky_sprite = pygame.image.load("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\blocky.png")
#         self.player = Player(screen, blocky_sprite, start_pos=self.start_pos, tile_size=tile_size)

#         # Game state
#         self.steps = 0
#         self.font = pygame.font.SysFont("Arial", 24)

#     def draw_tilemap(self):
#         for row in range(len(self.tilemap)):
#             for col in range(len(self.tilemap[row])):
#                 tile = self.tilemap[row][col]
#                 x = col * self.tile_size
#                 y = row * self.tile_size

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

#                 # Add grid lines for better visibility
#                 pygame.draw.rect(self.screen, (0, 0, 0), (x, y, self.tile_size, self.tile_size), 1)

#     def draw_ui(self):
#         # Draw the UI elements
#         steps_text = self.font.render(f"Steps: {self.steps}", True, (255, 255, 255))
#         goal_text = self.font.render("Find the Treasure!", True, (255, 223, 0))
#         self.screen.blit(steps_text, (10, 10))
#         self.screen.blit(goal_text, (self.screen.get_width() // 2 - goal_text.get_width() // 2, 10))

#     def check_goal(self):
#         # Check if the player has reached the goal
#         if (self.player.row, self.player.col) == self.goal_pos:
#             return True
#         return False

#     def run(self):
#         clock = pygame.time.Clock()
#         running = True

#         while running:
#             self.screen.fill((30, 30, 30))  # Dark background for better contrast
#             self.draw_tilemap()
#             self.player.render()
#             self.draw_ui()

#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     return "QUIT"  # Báo hiệu cần thoát chương trình
#                 elif event.type == pygame.KEYDOWN:
#                     if event.key == pygame.K_UP or event.key == pygame.K_w:
#                         self.player.move("UP", self.rows, self.cols, self.tilemap)
#                         self.steps += 1
#                     elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
#                         self.player.move("DOWN", self.rows, self.cols, self.tilemap)
#                         self.steps += 1
#                     elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
#                         self.player.move("LEFT", self.rows, self.cols, self.tilemap)
#                         self.steps += 1
#                     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
#                         self.player.move("RIGHT", self.rows, self.cols, self.tilemap)
#                         self.steps += 1

#             # Check if the player has reached the goal
#             if self.check_goal():
#                 win_text = self.font.render("🎉 You found the treasure! 🎉", True, (0, 255, 0))
#                 self.screen.blit(win_text, (self.screen.get_width() // 2 - win_text.get_width() // 2, self.screen.get_height() // 2))
#                 pygame.display.flip()
#                 pygame.time.wait(3000)
#                 return "Level Complete"

#             pygame.display.flip()
#             clock.tick(60)

import pygame
from player import Player
from utils import load_image
from map_generator import generate_random_map
from thuattoan import astar, bfs, beam_search, and_or_search, backtracking, q_learning, get_neighbors

class Game:
    def __init__(self, screen, tile_size, rows, cols):
        self.screen = screen
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols

        # Load images
        self.grass_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\grass.png", tile_size)
        self.dirt_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\dirt.png", tile_size)
        self.trees_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\tree.png", tile_size)
        self.water_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\water_16px.png", tile_size)
        self.treasure_img = load_image("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\treasure.png", tile_size)

        # Generate map and set start/goal positions
        self.tilemap = generate_random_map(self.rows, self.cols)
        self.start_pos = (0, 0)
        self.goal_pos = (self.rows - 1, self.cols - 1)
        self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"

        # Initialize player
        blocky_sprite = pygame.image.load("D:\\Nam2_HKII\\AI\\PROJECT\\PROJECT_AI\\assets\\map\\blocky.png")
        self.player = Player(screen, blocky_sprite, start_pos=self.start_pos, tile_size=tile_size)

        # Game state
        self.steps = 0
        self.font = pygame.font.SysFont("Arial", 24)
        self.path = []
        self.path_index = 0
        self.last_move_time = 0
        self.move_delay = 200
        self.current_algorithm = "astar"

        # Tile costs for A*, Backtracking, and Q-Learning
        self.tile_cost = {
            "G": 1, "D": 2, "T": float("inf"), "W": 5, "X": 1
        }

        # Path overlay for visualization
        self.path_overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.path_overlay.fill((255, 255, 0, 128))
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
                y = row * self.tile_size

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

                # Draw path overlay
                if (row, col) in self.path and (row, col) != self.goal_pos:
                    self.screen.blit(self.path_overlay, (x, y))

                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, self.tile_size, self.tile_size), 1)

    def draw_ui(self):
        steps_text = self.font.render(f"Steps: {self.steps}", True, (255, 255, 255))
        goal_text = self.font.render("Find the Treasure!", True, (255, 223, 0))
        algo_text = self.font.render(f"Algorithm: {self.current_algorithm.upper()}", True, (255, 255, 255))
        self.screen.blit(steps_text, (10, 10))
        self.screen.blit(goal_text, (self.screen.get_width() // 2 - goal_text.get_width() // 2, 10))
        self.screen.blit(algo_text, (10, 40))

    def compute_path(self):
        """Compute the path using the selected algorithm and track exploration for Backtracking."""
        self.path = []
        self.path_index = 0
        self.explored_tiles.clear()
        self.exploration_list = []
        self.exploration_index = 0
        self.is_exploring = False

        if self.current_algorithm == "astar":
            self.path = astar(self.start_pos, self.goal_pos, self.tilemap, self.tile_cost)
        elif self.current_algorithm == "bfs":
            self.path = bfs(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "beam search":
            self.path = beam_search(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "AndOr":
            self.path = and_or_search(self.start_pos, self.goal_pos, self.tilemap)
        elif self.current_algorithm == "backtracking":
            self.is_exploring = True
            visited = set()
            path = []

            def backtrack(curr):
                self.exploration_list.append(curr)
                if curr == self.goal_pos:  # Changed from 'goal' to 'self.goal_pos'
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
        """Update the exploration visualization for Backtracking step-by-step."""
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
        """Move the player along the computed path."""
        if self.is_exploring:
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
        if (self.player.row, self.player.col) == self.goal_pos:
            return True
        return False

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.screen.fill((30, 30, 30))
            self.draw_tilemap()
            self.player.render()
            self.draw_ui()

            self.update_exploration()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.player.move("UP", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            self.path = []
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.player.move("DOWN", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            self.path = []
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.player.move("LEFT", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            self.path = []
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.player.move("RIGHT", self.rows, self.cols, self.tilemap):
                            self.steps += 1
                            self.start_pos = (self.player.row, self.player.col)
                            self.path = []
                    elif event.key == pygame.K_SPACE:
                        self.compute_path()
                    elif event.key == pygame.K_1:
                        self.current_algorithm = "astar"
                        self.path = []
                    elif event.key == pygame.K_2:
                        self.current_algorithm = "bfs"
                        self.path = []
                    elif event.key == pygame.K_3:
                        self.current_algorithm = "beam search"
                        self.path = []
                    elif event.key == pygame.K_4:
                        self.current_algorithm = "AndOr"
                        self.path = []
                    elif event.key == pygame.K_5:
                        self.current_algorithm = "backtracking"
                        self.path = []
                    elif event.key == pygame.K_6:
                        self.current_algorithm = "q_learning"
                        self.path = []

            self.follow_path()

            if self.check_goal():
                win_text = self.font.render("🎉 You found the treasure! 🎉", True, (0, 255, 0))
                self.screen.blit(win_text, (self.screen.get_width() // 2 - win_text.get_width() // 2, self.screen.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
                return "Level Complete"

            pygame.display.flip()
            clock.tick(60)