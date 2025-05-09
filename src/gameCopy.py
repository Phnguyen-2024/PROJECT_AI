import pygame
from player import Player
from utils import load_image
from map_generator import generate_random_map

class Game:
    def __init__(self, screen, tile_size, rows, cols):
        self.screen = screen
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols

        # Load images
        self.grass_img = load_image("D:\\tailieumonhoc\\trituenhantao\\game\\assets\\map\\grass.png", tile_size)
        self.dirt_img = load_image("D:\\tailieumonhoc\\trituenhantao\\game\\assets\\map\\dirt.png", tile_size)
        self.trees_img = load_image("D:\\tailieumonhoc\\trituenhantao\\game\\assets\\map\\tree.png", tile_size)
        self.water_img = load_image("D:\\tailieumonhoc\\trituenhantao\\game\\assets\\map\\water_16px.png", tile_size)
        self.treasure_img = load_image("D:\\tailieumonhoc\\trituenhantao\\game\\assets\\map\\treasure.png", tile_size)

        # Generate map and set start/goal positions
        self.tilemap = generate_random_map(rows, cols)
        self.start_pos = (0, 0)  # Start at the top-left corner
        self.goal_pos = (rows - 1, cols - 1)  # Goal at the bottom-right corner
        self.tilemap[self.goal_pos[0]][self.goal_pos[1]] = "X"  # Mark goal with "X"

        # Initialize player
        blocky_sprite = pygame.image.load("D:\\tailieumonhoc\\trituenhantao\\game\\assets\\map\\blocky.png")
        self.player = Player(screen, blocky_sprite, start_pos=self.start_pos, tile_size=tile_size)

        # Game state
        self.steps = 0
        self.font = pygame.font.SysFont("Arial", 24)

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

                # Add grid lines for better visibility
                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, self.tile_size, self.tile_size), 1)

    def draw_ui(self):
        # Draw the UI elements
        steps_text = self.font.render(f"Steps: {self.steps}", True, (255, 255, 255))
        goal_text = self.font.render("Find the Treasure!", True, (255, 223, 0))
        self.screen.blit(steps_text, (10, 10))
        self.screen.blit(goal_text, (self.screen.get_width() // 2 - goal_text.get_width() // 2, 10))

    def check_goal(self):
        # Check if the player has reached the goal
        if (self.player.row, self.player.col) == self.goal_pos:
            return True
        return False

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.screen.fill((30, 30, 30))  # Dark background for better contrast
            self.draw_tilemap()
            self.player.render()
            self.draw_ui()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"  # Báo hiệu cần thoát chương trình
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.move("UP", self.rows, self.cols, self.tilemap)
                        self.steps += 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.player.move("DOWN", self.rows, self.cols, self.tilemap)
                        self.steps += 1
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player.move("LEFT", self.rows, self.cols, self.tilemap)
                        self.steps += 1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player.move("RIGHT", self.rows, self.cols, self.tilemap)
                        self.steps += 1

            # Check if the player has reached the goal
            if self.check_goal():
                win_text = self.font.render("🎉 You found the treasure! 🎉", True, (0, 255, 0))
                self.screen.blit(win_text, (self.screen.get_width() // 2 - win_text.get_width() // 2, self.screen.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
                return "Level Complete"

            pygame.display.flip()
            clock.tick(60)