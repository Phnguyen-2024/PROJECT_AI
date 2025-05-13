import pygame
from game_combined import Game
#from gameCopy import Game
from ui import show_start_screen, show_level_complete

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 64
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
pygame.display.set_caption("TRUY TÌM KHO BÁU")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Show start screen
show_start_screen(screen)

# Initialize game
rows = (SCREEN_HEIGHT - 100) // TILE_SIZE  # Điều chỉnh rows dựa trên PANEL_TOP_HEIGHT = 100
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