import pygame
from game_combined import Game
from ui import show_start_screen, show_level_complete

try:
    from PIL import Image
    pillow_available = True
except ImportError:
    pillow_available = False

pygame.init()
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Error initializing mixer: {e}")

TILE_SIZE = 32
SCREEN_WIDTH = 930
SCREEN_HEIGHT = 650
PANEL_TOP_HEIGHT = 100
pygame.display.set_caption("TRUY TÌM KHO BÁU")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

show_start_screen(screen)

rows = (SCREEN_HEIGHT - 100) // TILE_SIZE  # Điều chỉnh rows dựa trên PANEL_TOP_HEIGHT = 100
cols = SCREEN_WIDTH // TILE_SIZE

game = Game(screen, TILE_SIZE, rows, cols)  # Khởi tạo Game một lần
running = True  # Biến để kiểm soát vòng lặp chính
while running:  # Vòng lặp chính để trò chơi có thể tiếp tục
    result = game.run()

    # Kiểm tra kết quả từ game.run()
    if result == "QUIT":
        running = False  # Thoát vòng lặp chính
    elif result == "Level Complete":
        action = show_level_complete(screen)
        if action == "QUIT":
            running = False  # Thoát vòng lặp chính
    elif result == "MAIN_MENU":
        show_start_screen(screen)  # Quay lại giao diện chính

# Thoát Pygame
pygame.quit()