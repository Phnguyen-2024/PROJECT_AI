import pygame
from gameCopy import Game
from ui import show_start_screen, show_level_complete

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 64
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
pygame.display.set_caption("Island Treasure Hunt")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Show start screen
show_start_screen(screen)

# Initialize game
rows = SCREEN_HEIGHT // TILE_SIZE
cols = SCREEN_WIDTH // TILE_SIZE

running = True  # Biến để kiểm soát vòng lặp chính
while running:  # Vòng lặp chính để trò chơi có thể tiếp tục
    game = Game(screen, TILE_SIZE, rows, cols)
    result = game.run()

    # Kiểm tra kết quả từ game.run()
    if result == "QUIT":
        running = False  # Thoát vòng lặp chính
    elif result == "Level Complete":
        action = show_level_complete(screen)
        if action == "QUIT":
            running = False  # Thoát vòng lặp chính

# Thoát Pygame
pygame.quit()